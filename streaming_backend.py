"""Backend di esecuzione streaming System 2 (SSE) — voce P1 ToDo 2026-10-28.

Tutti i percorsi HAL chiamavano l'upstream con ``stream: false``: il timeout
end-to-end della richiesta (504 "al vecchio timeout upstream di 60 s") è un
problema strutturale delle generazioni lunghe, non una sfortuna di rete. Lo
streaming elimina il timeout end-to-end e non influisce sulla qualità della
risposta (FAQ QwenCloud).

Il modulo ricostruisce un ``SystemTwoResponse`` dal flusso SSE:

- accumulo dei ``delta.content`` dei chunk;
- gestione del chunk finale SENZA ``choices`` ma con ``usage`` (con
  ``stream_options.include_usage`` l'usage reale arriva nell'ultimo chunk,
  OpenAI-compatibile);
- terminazione alla sentinella ``data: [DONE]``.

Si registra con ``SystemTwoEngine.register_backend`` e passa la validazione di
frontiera ``validate_chat_payload`` (modelli streaming_only, system+tools).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from typing import Any

from global_config import SystemTwoResponse, validate_chat_payload

DONE_SENTINEL = "data: [DONE]"
_SSE_PREFIX = "data:"


class ToolCallAccumulator:
    """Accumulo dei delta di ``tool_calls`` per index, parsing solo a stream finito.

    Gli argomenti JSON arrivano spezzati in stringhe parziali: concatenarli per
    ``index`` e passare a ``json.loads`` solo a fine stream evita sia il parsing
    su chunk singolo (che solleverebbe su ogni frammento) sia la corruzione
    dell'argomento. Con thinking mode il flusso emette tre fasi (token di
    thinking, delta tool, risposta finale): questa classe ignora tutto cio' che
    non e' delta.tool_calls.
    """

    def __init__(self) -> None:
        self._by_index: dict[int, dict[str, Any]] = {}
        self.parse_count = 0

    def feed(self, chunk: dict[str, Any]) -> None:
        """Accoda i frammenti del chunk; mai parsing qui."""
        for choice in chunk.get("choices") or []:
            delta = choice.get("delta") or {}
            for tc in delta.get("tool_calls") or []:
                index = tc.get("index", len(self._by_index))
                entry = self._by_index.setdefault(
                    index,
                    {
                        "id": None,
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    },
                )
                if tc.get("id") is not None:
                    entry["id"] = tc["id"]
                if tc.get("type"):
                    entry["type"] = tc["type"]
                fn = tc.get("function") or {}
                if fn.get("name"):
                    entry["function"]["name"] += fn["name"]
                if fn.get("arguments"):
                    entry["function"]["arguments"] += fn["arguments"]

    def final_tool_calls(self) -> list[dict[str, Any]]:
        """Un solo parsing per call, a stream terminato; in ordine di index."""
        out: list[dict[str, Any]] = []
        for index in sorted(self._by_index):
            entry = self._by_index[index]
            raw = entry["function"]["arguments"]
            arguments: Any = None
            if raw:
                self.parse_count += 1
                arguments = json.loads(raw)
            out.append(
                {
                    "id": entry["id"],
                    "type": entry["type"],
                    "index": index,
                    "function": {
                        "name": entry["function"]["name"],
                        "arguments": arguments,
                    },
                }
            )
        return out


def extract_sse_data(line: str) -> str | None:
    """Estrae il payload di una riga SSE; None per commenti/keep-alive/vuoti.

    La sentinella ritorna come ``"[DONE]"`` cosicché il chiamante possa
    terminare il loop alla sentinella invece di ignorarla.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith(":"):
        return None
    if stripped.startswith(_SSE_PREFIX):
        return stripped[len(_SSE_PREFIX) :].strip()
    return None


def build_stream_payload(
    task: str,
    text: str,
    model: str,
    *,
    include_usage: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Payload OpenAI-compatibile per la chiamata streaming, validato alla frontiera."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": text}],
        "stream": True,
    }
    if include_usage:
        payload["stream_options"] = {"include_usage": True}
    if extra:
        payload.update(extra)
    return validate_chat_payload(payload)


def accumulate_stream(
    lines: Iterable[str],
    model: str,
    provider: str,
) -> SystemTwoResponse:
    """Ricostruisce la risposta completa dai chunk SSE.

    Il testo accumulato (non i chunk) e' la forma corretta da mettere in Cache
    L1: con JSON Mode + streaming solo l'output concatenato e' JSON valido.
    I delta di ``tool_calls`` passano dal ``ToolCallAccumulator`` interno: il
    parsing JSON avviene una sola volta, a fine stream.
    """
    parts: list[str] = []
    usage: dict[str, Any] = {}
    tool_acc = ToolCallAccumulator()
    for line in lines:
        data = extract_sse_data(line)
        if data is None:
            continue
        if data == "[DONE]":
            break
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            continue
        tool_acc.feed(chunk)
        choices = chunk.get("choices") or []
        if choices:
            delta = choices[0].get("delta") or {}
            content = delta.get("content")
            if content:
                parts.append(str(content))
        elif chunk.get("usage"):
            # chunk finale senza choices ma con usage reale
            usage = dict(chunk["usage"])
    response = SystemTwoResponse("".join(parts), model, provider, fallback_used=False)
    response.usage = usage  # type: ignore[attr-defined]
    response.tool_calls = tool_acc.final_tool_calls()  # type: ignore[attr-defined]
    return response


class SSESystemTwoBackend:
    """Backend registrabile su SystemTwoEngine con sorgente di righe SSE iniettata.

    ``line_source(payload)`` fornisce un iterable di righe (in produzione la
    ``resp.iter_lines()`` di una sessione requests; nei test un mock).
    """

    def __init__(
        self,
        line_source: Callable[[dict[str, Any]], Iterable[str]],
        provider: str = "orcarouter",
    ) -> None:
        self._line_source = line_source
        self.provider = provider

    def __call__(
        self,
        task: str,
        text: str,
        *args: Any,
        model: str | None = None,
        agent: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        served = model or "unknown"
        payload = build_stream_payload(task, text, served, extra=kwargs.get("extra"))
        response = accumulate_stream(self._line_source(payload), served, self.provider)
        return {
            "response": str(response),
            "model": served,
            "provider": self.provider,
            "usage": getattr(response, "usage", {}),
        }
