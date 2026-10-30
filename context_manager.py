"""ContextManager multi-turn per il Gateway Core (System 2).

Le API LLM sono stateless: il client mantiene l'array ``messages`` e lo
riduce entro ``max_context_tokens`` del profilo. Tre strategie, nell'ordine
in ``compact``:

1. retrieval on-demand (blocco contesto davanti alla conversazione);
2. rolling summary a soglia (default 70% del budget) sui turni piu' vecchi;
3. troncamento (si tengono gli ultimi ``keep_recent_turns`` turni).

Il messaggio ``system`` e' sempre trattenuto in testa: contentuto volatile
mai in testa, come da regola static-first del protocollo.

L'estima token e' euristica a ``len // TOKENS_PER_CHAR`` sulla serializzazione
da ``normalize_prompt`` (stessa normalizzazione usata per la Cache L1, quindi
chiave e budget restano allineati). Serve a dimensionare il contesto, non alla
fatturazione: i valori reali arrivano dai campi ``usage`` del provider.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

# 4 char per token: euristica conservativa per testi misti IT/en.
TOKENS_PER_CHAR = 4

# Riserva per l'overhead di serializzazione per messaggio (ruolo, separatori).
PER_MESSAGE_OVERHEAD = 4


def estimate_message_tokens(messages: Sequence[Any]) -> int:
    """Stima euristica dei token di un array di messaggi (o di un prompt stringa).

    Il campo ``reasoning_content`` dei modelli thinking non è mai conteggiato:
    non viene reinserito nella history (regola QwenCloud thinking model).
    """
    if isinstance(messages, str):
        return max(1, len(messages) // TOKENS_PER_CHAR)
    total = 0
    for message in messages:
        if isinstance(message, str):
            total += len(message) // TOKENS_PER_CHAR
            continue
        pieces = [str(message.get("content", "") or "")]
        for tool_call in message.get("tool_calls") or []:
            pieces.append(str(tool_call))
        total += len(" ".join(pieces)) // TOKENS_PER_CHAR + PER_MESSAGE_OVERHEAD
    return max(0, total)


class ContextManager:
    """Riduce un array ``messages`` entro il budget del profilo System 2."""

    def __init__(
        self,
        max_context_tokens: int,
        keep_recent_turns: int = 4,
        summary_threshold: float = 0.70,
        summarizer: Callable[[list[Any]], str] | None = None,
        retriever: Callable[[str], list[str]] | None = None,
        summary_prefix: str = "Riepilogo dei turni precedenti:",
    ) -> None:
        if max_context_tokens <= 0:
            raise ValueError("max_context_tokens deve essere positivo")
        if keep_recent_turns < 0:
            raise ValueError("keep_recent_turns non puo' essere negativo")
        self.max_context_tokens = int(max_context_tokens)
        self.keep_recent_turns = int(keep_recent_turns)
        self.summary_threshold = float(summary_threshold)
        self.summarizer = summarizer
        self.retriever = retriever
        self.summary_prefix = summary_prefix

    def compact(
        self,
        messages: Sequence[Any],
        query: str | None = None,
    ) -> list[Any]:
        """Restituisce un array di messaggi entro ``max_context_tokens``.

        ``query``, con un ``retriever`` configurato, antepone un blocco di
        contesto recuperato on-demand. Sotto budget la conversazione e'
        restituita invariata.
        """
        msgs = [
            {k: v for k, v in m.items() if k != "reasoning_content"}
            if isinstance(m, dict)
            else m
            for m in messages
        ]
        if not msgs:
            return []
        msgs = self._merge_tool_messages(msgs)

        prefix, body = self._split_system(msgs)

        # Se il solo system non entra nel budget si preserva comunque: la regola
        # static-first non consente di tagliare la testa del prompt.
        context_blocks: list[Any] = []
        if query and self.retriever is not None:
            for chunk in self.retriever(query):
                context_blocks.append({"role": "system", "content": str(chunk)})

        if (
            estimate_message_tokens(prefix + body + context_blocks)
            <= self.max_context_tokens
        ):
            return prefix + context_blocks + body

        summary_blocks = self._rolling_summary(prefix, body)
        if summary_blocks is not None:
            return prefix + context_blocks + summary_blocks

        return prefix + context_blocks + self._truncate(body)

    @staticmethod
    def _merge_tool_messages(messages: list[Any]) -> list[Any]:
        """Fonde i messaggi ``tool`` consecutivi dello stesso turno in un solo
        messaggio con N content block.

        Un messaggio per risultato di tool calls parallele fa crescere i
        content block oltre la finestra di lookback (20 dal marker) e provoca
        cache miss lato provider (regola QwenCloud, 2026-10-28).
        """
        merged: list[Any] = []
        for message in messages:
            if (
                isinstance(message, dict)
                and message.get("role") == "tool"
                and merged
                and isinstance(merged[-1], dict)
                and merged[-1].get("role") == "tool"
            ):
                prev = merged[-1]
                blocks = prev.get("content")
                if not isinstance(blocks, list):
                    blocks = [
                        {
                            "type": "text",
                            "text": str(prev.get("content", "")),
                            "tool_call_id": prev.get("tool_call_id"),
                        }
                    ]
                blocks.append(
                    {
                        "type": "text",
                        "text": str(message.get("content", "")),
                        "tool_call_id": message.get("tool_call_id"),
                    }
                )
                prev["content"] = blocks
                prev.setdefault("tool_call_ids", [])
                if prev.get("tool_call_id"):
                    prev["tool_call_ids"].append(prev["tool_call_id"])
                if message.get("tool_call_id"):
                    prev["tool_call_ids"].append(message["tool_call_id"])
            else:
                merged.append(message)
        return merged

    def _split_system(self, messages: list[Any]) -> tuple[list[Any], list[Any]]:
        """Isola i messaggi di sistema in testa dal transcript append-only."""
        prefix: list[Any] = []
        body: list[Any] = []
        for message in messages:
            if isinstance(message, dict) and str(message.get("content", "")).startswith(
                self.summary_prefix
            ):
                # i riepiloghi gia' prodotti restano nel transcript, non in testa
                body.append(message)
            elif isinstance(message, dict) and message.get("role") == "system":
                prefix.append(message)
            else:
                body.append(message)
        return prefix, body

    def _rolling_summary(self, prefix: list[Any], body: list[Any]) -> list[Any] | None:
        """Soglia ~70% del contesto: riassume i turni vecchi, tiene i piu' recenti.

        Ritorna ``None`` se il summarizer manca o se il risultato non sta nel
        budget: in quel caso il chiamante degrada a troncamento.
        """
        if self.summarizer is None or len(body) <= 2:
            return None

        threshold = int(self.max_context_tokens * self.summary_threshold)
        if estimate_message_tokens(prefix + body) < threshold:
            return None

        # la finestra da riassumere deve stare nel budget, con il prefisso e i
        # turni recenti gia' conteggiati
        recent = self._truncate(body)
        index = len(body) - len(recent)
        old = body[: max(0, index)]
        if not old:
            return None

        summary_text = self.summarizer(old)
        blocks = [
            {"role": "system", "content": f"{self.summary_prefix} {summary_text}"}
        ]
        if estimate_message_tokens(prefix + blocks + recent) > self.max_context_tokens:
            return None
        return blocks + recent

    def _truncate(self, body: list[Any]) -> list[Any]:
        """Tiene gli ultimi ``keep_recent_turns`` turni piu' il riassunto precedente.

        Un turno = messaggio non-system seguito dalla sua risposta: si taglia
        dalla testa finche' il budget non e' rispettato.
        """
        window = self.keep_recent_turns * 2
        kept = body[-window:] if window > 0 else []
        while kept and estimate_message_tokens(kept) > self.max_context_tokens:
            kept = kept[1:]
        if kept and estimate_message_tokens(kept) > self.max_context_tokens:
            # un singolo messaggio eccede il budget: troncato sul contenuto
            message = dict(kept[0])
            budget_chars = max(0, self.max_context_tokens * TOKENS_PER_CHAR)
            message["content"] = str(message.get("content", ""))[:budget_chars]
            return [message]
        return kept


__all__ = ["ContextManager", "estimate_message_tokens"]
