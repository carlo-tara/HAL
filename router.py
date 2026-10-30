#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, TypedDict

from global_config import GlobalLayaHandler, configure_laya_defaults
from laya_service import LayaOutcome, LayaSystemOneService
from system1_preflight import LayaCallBudget

# Assicura che le impostazioni di default siano attive all'importazione
configure_laya_defaults()

PRIMARY_AGENTS: list[str] = [
    "a-agentzero",
    "a-b2b",
    "a-copywriter",
    "a-design",
    "a-harness",
    "a-product",
    "a-seozoom",
    "a-wordpress",
]

AGENT_SUB_SKILLS: dict[str, list[str]] = {
    "a-b2b": ["enrichment", "core"],
    "a-design": ["uiux", "charts", "illustrator", "core"],
    "a-product": ["personas", "jtbd", "gherkin", "core"],
}

# ==========================================
# Catalogo skill compatto (tool-search System 1)
# ==========================================
# Le descrizioni complete di ~39 skill esposte a ogni prompt sono Tool
# Definition Bloat: il catalogo sotto è la forma compatta (nome + keyword)
# interrogabile via routing Laya; il bundle completo si carica solo su domanda.

SKILLS_ROOT = Path(__file__).resolve().parent / ".agents" / "skills"

_USE_HINTS = (
    "usare proattivamente per",
    "usa proattivamente per",
    "usalo proattivamente per",
    "invocabile per",
    "usare per",
    "usa per",
    "usati per",
    "use with",
    "use for",
    "use when",
)


def _parse_skill_frontmatter(text: str) -> dict[str, Any]:
    """Mini-parser del frontmatter YAML (name, description folded/inline, competencies)."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    info: dict[str, Any] = {}
    current_key: str | None = None
    buffer: list[str] = []
    for raw in parts[1].splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            info.setdefault(current_key, []).append(line[4:].strip())
            continue
        if current_key and line[:1] in (" ", "\t"):
            buffer.append(line.strip())
            continue
        if current_key and buffer:
            info[current_key] = " ".join(buffer)
            buffer = []
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value in {">-", ">", "|", "|-"}:
                current_key = key
                buffer = []
                info[key] = ""
            elif value == "":
                current_key = key
                info[key] = []
            else:
                current_key = None
                info[key] = value
    if current_key and buffer:
        info[current_key] = " ".join(buffer)
    return info


def _extract_keywords(
    name: str, description: str, competencies: list[str]
) -> list[str]:
    keywords: list[str] = []

    def add(token: str) -> None:
        token = token.strip().strip(".")
        if len(token) >= 2 and token.lower() not in {k.lower() for k in keywords}:
            keywords.append(token)

    for comp in competencies:
        add(comp)
    lowered = description.lower()
    for hint in _USE_HINTS:
        idx = lowered.find(hint)
        if idx != -1:
            tail = description[idx + len(hint) :]
            tail = tail.split(".", 1)[0]
            for part in re.split(r"[,;]| e ", tail):
                add(part)
            break
    if not keywords:
        for part in name.split("-"):
            add(part)
    return keywords[:10]


class SkillCatalogEntry(TypedDict):
    """Riga compatta del catalogo: nome + keyword, bundle completo on-demand."""

    name: str
    keywords: list[str]
    description: str
    line: str
    path: str


def load_skill_catalog(skills_root: Path = SKILLS_ROOT) -> list[SkillCatalogEntry]:
    """Catalogo compatto: una riga (nome + keyword) per skill, path on-demand."""
    entries: list[SkillCatalogEntry] = []
    if not skills_root.is_dir():
        return entries
    for child in sorted(skills_root.iterdir()):
        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        info = _parse_skill_frontmatter(text)
        name = str(info.get("name") or child.name)
        description = str(info.get("description") or "")
        competencies = info.get("competencies") or []
        keywords = _extract_keywords(
            name, description, competencies if isinstance(competencies, list) else []
        )
        line = f"{name}: {', '.join(keywords)}"
        entries.append(
            {
                "name": name,
                "keywords": keywords,
                "description": description,
                "line": line,
                "path": str(skill_md),
            }
        )
    return entries


def _query_tokens(text: str) -> list[str]:
    return [
        t for t in re.split(r"[^0-9a-zA-ZàèéìòùÀÈÉÌÒÙ_-]+", text.lower()) if len(t) >= 3
    ]


def _skill_score(query_tokens: list[str], entry: SkillCatalogEntry) -> int:
    haystack = [str(k).lower() for k in entry["keywords"]]
    haystack.append(str(entry["name"]).lower())
    score = 0
    for token in query_tokens:
        best = 0
        for hay in haystack:
            for unit in re.split(r"[^0-9a-zA-Z_éàèìòù-]+", hay):
                unit = unit.lower()
                if len(unit) < 3:
                    continue
                if token == unit:
                    best = max(best, 3)
                elif len(token) >= 4 and (token in unit or unit in token):
                    best = max(best, 2)
                elif SequenceMatcher(None, token, unit).ratio() >= 0.72:
                    best = max(best, 1)
        score += best
    return score


def search_skills(
    query: str, top_k: int = 5, *, use_laya: bool = True
) -> list[SkillCatalogEntry]:
    """Sottoinsieme di skill da keyword tag (tool-search System 1).

        Pre-selezione locale deterministica (keyword overlap); se Laya è
    disponibile, il routing conferma/declassa la prima scelta. Con Laya assente
        (ABSTAIN) il sottoinsieme locale resta valido: il gateway non si blocca.
    """
    catalog = load_skill_catalog()
    tokens = _query_tokens(query)
    scored = [(_skill_score(tokens, e), e) for e in catalog]
    scored = [(s, e) for s, e in scored if s > 0]
    scored.sort(key=lambda pair: (-pair[0], str(pair[1]["name"])))
    subset = [e for _, e in scored[: max(int(top_k), 1)]]
    if use_laya and subset:
        names = [str(e["name"]) for e in subset]
        try:
            verdict = handle_routing(query, names)
        except Exception:  # noqa: BLE001 - Laya assente: tiene il fallback locale
            verdict = LayaOutcome(status="abstain")
        if verdict.status == "ok" and verdict.value in names:
            subset = sorted(
                subset, key=lambda e: 0 if str(e["name"]) == verdict.value else 1
            )
    return subset


def catalog_token_report(catalog: list[SkillCatalogEntry]) -> dict[str, float]:
    """Misura il risparmio token: descrizioni integrali vs righe compatte."""
    full_chars = sum(len(str(e["name"])) + len(str(e["description"])) for e in catalog)
    compact_chars = sum(len(str(e["line"])) for e in catalog)
    full_tokens = full_chars // 4
    compact_tokens = compact_chars // 4
    reduction_pct = (
        round(100.0 * (full_tokens - compact_tokens) / full_tokens, 1)
        if full_tokens
        else 0.0
    )
    return {
        "skills": len(catalog),
        "full_tokens": full_tokens,
        "compact_tokens": compact_tokens,
        "reduction_pct": reduction_pct,
    }


def triage_request(
    request_text: str, *, laya_budget: LayaCallBudget | None = None
) -> dict[str, Any]:
    """Bound agent/skill decisions to two attempts, or a stricter enclosing budget."""
    with LayaSystemOneService.budget(laya_budget, max_calls=2):
        return _triage_request(request_text)


def _triage_request(request_text: str) -> dict[str, Any]:
    """
    Valuta una richiesta utente tramite Laya System 1 per decidere:
    1. A quale agente primario instradarla (o 'none' se fuori perimetro)
    2. Se l'agente ha sotto-skill, a quale sotto-skill instradarla (o 'core').
    """
    candidate_routes = PRIMARY_AGENTS + ["none"]
    route_result = handle_routing(request_text, candidate_routes)
    if route_result.status != "ok" or route_result.value not in candidate_routes:
        return {
            "request": request_text,
            "agent": "none",
            "skill": None,
            "is_routed": False,
            "decision_status": "abstain",
        }

    chosen_agent = route_result.value
    chosen_skill: str | None = None
    if chosen_agent in AGENT_SUB_SKILLS:
        skills = AGENT_SUB_SKILLS[chosen_agent]
        skill_result = handle_choice(
            f"Per la richiesta '{request_text}', quale componente di {chosen_agent} è più indicato?",
            skills,
        )
        if skill_result.status != "ok" or skill_result.value not in skills:
            return {
                "request": request_text,
                "agent": "none",
                "skill": None,
                "is_routed": False,
                "decision_status": "abstain",
            }
        chosen_skill = skill_result.value

    return {
        "request": request_text,
        "agent": chosen_agent,
        "skill": chosen_skill,
        "is_routed": chosen_agent != "none",
        "decision_status": "ok",
    }


def handle_choice(prompt: str, options: list[str]) -> LayaOutcome[str]:
    """Interfaccia obbligatoria per la scelta multipla (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("choice", prompt, options)


def handle_routing(request_text: str, routes: list[str]) -> LayaOutcome[str]:
    """Interfaccia obbligatoria per il routing (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("routing", request_text, routes)


def handle_score(text: str, criteria: str) -> Any:
    """Interfaccia obbligatoria per lo score euristico (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("score", text, criteria)


def handle_noul(text: str) -> Any:
    """Interfaccia obbligatoria per noul (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("noul", text)


def handle_batch_score(texts: list[str], criteria: str) -> list[LayaOutcome[float]]:
    """Valuta in batch una lista di testi rispetto a un criterio (System 1 - Laya)."""
    with LayaSystemOneService.budget(max_calls=len(texts)):
        return [handle_score(t, criteria) for t in texts]


def handle_batch_routing(texts: list[str], routes: list[str]) -> list[LayaOutcome[str]]:
    """Instrada in batch una lista di testi verso le rotte candidate (System 1 - Laya)."""
    with LayaSystemOneService.budget(max_calls=len(texts)):
        return [handle_routing(t, routes) for t in texts]


def route_task(task_type: str, *args: Any, **kwargs: Any) -> Any:
    """
    Funzione di routing unificata per gestire sia i task System 1 (Laya)
    sia i task System 2 (Modello di interfaccia / motori estensibili).
    """
    return GlobalLayaHandler.evaluate(task_type, *args, **kwargs)


def _parse_list(values: list[str] | None) -> list[str]:
    if not values:
        return []
    result: list[str] = []
    for item in values:
        for part in item.split(","):
            cleaned = part.strip()
            if cleaned:
                result.append(cleaned)
    return result


def main() -> None:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--json", action="store_true", help="Formatta l'output come JSON"
    )

    parser = argparse.ArgumentParser(
        description="HAL System 1 (Laya) CLI Interface & Task Router",
        parents=[parent_parser],
    )
    subparsers = parser.add_subparsers(
        dest="subcommand", help="Comando System 1 da eseguire"
    )

    # routing
    parser_routing = subparsers.add_parser(
        "routing",
        parents=[parent_parser],
        help="Classifica e instrada testo verso una lista di rotte",
    )
    parser_routing.add_argument("text", help="Testo o richiesta da instradare")
    parser_routing.add_argument(
        "--routes",
        "-r",
        nargs="+",
        required=True,
        help="Rotte candidate (separate da spazio o virgola)",
    )

    # choice
    parser_choice = subparsers.add_parser(
        "choice",
        parents=[parent_parser],
        help="Seleziona un'opzione tra alternative discrete",
    )
    parser_choice.add_argument("prompt", help="Prompt o domanda di decisione")
    parser_choice.add_argument(
        "--options",
        "-o",
        nargs="+",
        required=True,
        help="Opzioni candidate (separate da spazio o virgola)",
    )

    # score
    parser_score = subparsers.add_parser(
        "score",
        parents=[parent_parser],
        help="Valuta lo score euristico rispetto a un criterio",
    )
    parser_score.add_argument("text", help="Testo o oggetto da valutare")
    parser_score.add_argument(
        "--criteria", "-c", required=True, help="Criterio di valutazione"
    )

    # noul
    parser_noul = subparsers.add_parser(
        "noul",
        parents=[parent_parser],
        help="Esegue elaborazione veloce noul",
    )
    parser_noul.add_argument("text", help="Testo di input")

    # triage
    parser_triage = subparsers.add_parser(
        "triage",
        parents=[parent_parser],
        help="Valuta una richiesta tramite Laya e la instrada all'agente opportuno (o none)",
    )
    parser_triage.add_argument("text", help="Richiesta utente da valutare e instradare")

    # catalog
    parser_catalog = subparsers.add_parser(
        "catalog",
        parents=[parent_parser],
        help="Emitte il catalogo skill compatto (nome + keyword) con report token",
    )
    parser_catalog.add_argument(
        "--tokens", action="store_true", help="Includi il report token"
    )

    # search
    parser_search = subparsers.add_parser(
        "search",
        parents=[parent_parser],
        help="Tool-search: sottoinsieme di skill da keyword tag per una richiesta",
    )
    parser_search.add_argument("text", help="Richiesta da confrontare col catalogo")
    parser_search.add_argument("--top", type=int, default=5, help="Massimo risultati")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    if args.subcommand == "routing":
        routes = _parse_list(args.routes)
        result = handle_routing(args.text, routes)
        if args.json:
            print(
                json.dumps(
                    {
                        "task": "routing",
                        "text": args.text,
                        "routes": routes,
                        "route": result.value,
                        "status": result.status,
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(result.value if result.status == "ok" else "ABSTAIN")
    elif args.subcommand == "choice":
        options = _parse_list(args.options)
        result = handle_choice(args.prompt, options)
        if args.json:
            print(
                json.dumps(
                    {
                        "task": "choice",
                        "prompt": args.prompt,
                        "options": options,
                        "choice": result.value,
                        "status": result.status,
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(result.value if result.status == "ok" else "ABSTAIN")
    elif args.subcommand == "score":
        result = handle_score(args.text, args.criteria)
        if args.json:
            print(
                json.dumps(
                    {
                        "task": "score",
                        "text": args.text,
                        "criteria": args.criteria,
                        "score": result.value,
                        "status": result.status,
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(result.value if result.status == "ok" else "ABSTAIN")
    elif args.subcommand == "noul":
        result = handle_noul(args.text)
        if args.json:
            print(
                json.dumps(
                    {
                        "task": "noul",
                        "text": args.text,
                        "result": result.value,
                        "status": result.status,
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(result)
    elif args.subcommand == "triage":
        result = triage_request(args.text)
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            agent = result["agent"]
            skill = result.get("skill")
            if result["decision_status"] == "abstain":
                print(
                    "ABSTAIN (instradamento non affidabile — richiedere verifica System 2)"
                )
            elif agent == "none":
                print(
                    "none (Nessun agente specifico richiesto — gestito da System 2 generico)"
                )
            elif skill and skill != "core":
                print(f"{agent} -> skill: {skill}")
            else:
                print(agent)

    elif args.subcommand == "catalog":
        catalog = load_skill_catalog()
        report = catalog_token_report(catalog) if args.tokens else None
        if args.json:
            payload = {
                "task": "catalog",
                "catalog": [
                    {"name": e["name"], "keywords": e["keywords"]} for e in catalog
                ],
            }
            if report:
                payload["token_report"] = report
            print(json.dumps(payload, ensure_ascii=False))
        else:
            for entry in catalog:
                print(entry["line"])
            if report:
                print(
                    f"-- {report['skills']} skill: {report['full_tokens']} token "
                    f"integrale -> {report['compact_tokens']} compatte "
                    f"(-{report['reduction_pct']}%)",
                    file=sys.stderr,
                )
    elif args.subcommand == "search":
        hits = search_skills(args.text, top_k=args.top)
        names = [str(h["name"]) for h in hits]
        if args.json:
            print(
                json.dumps(
                    {
                        "task": "search",
                        "text": args.text,
                        "skills": [
                            {
                                "name": h["name"],
                                "keywords": h["keywords"],
                                "path": h["path"],
                            }
                            for h in hits
                        ],
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(", ".join(names) if names else "NONE")


if __name__ == "__main__":
    main()
