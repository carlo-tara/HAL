#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from global_config import GlobalLayaHandler, configure_laya_defaults

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

def triage_request(request_text: str) -> dict[str, Any]:
    """
    Valuta una richiesta utente tramite Laya System 1 per decidere:
    1. A quale agente primario instradarla (o 'none' se fuori perimetro)
    2. Se l'agente ha sotto-skill, a quale sotto-skill instradarla (o 'core').
    """
    candidate_routes = PRIMARY_AGENTS + ["none"]
    chosen_agent = handle_routing(request_text, candidate_routes)

    chosen_skill: str | None = None
    if chosen_agent in AGENT_SUB_SKILLS:
        skills = AGENT_SUB_SKILLS[chosen_agent]
        chosen_skill = handle_choice(
            f"Per la richiesta '{request_text}', quale componente di {chosen_agent} è più indicato?",
            skills,
        )

    return {
        "request": request_text,
        "agent": chosen_agent,
        "skill": chosen_skill,
        "is_routed": chosen_agent != "none",
    }

def handle_choice(prompt: str, options: list[str]) -> str:
    """Interfaccia obbligatoria per la scelta multipla (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("choice", prompt, options)

def handle_routing(request_text: str, routes: list[str]) -> str:
    """Interfaccia obbligatoria per il routing (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("routing", request_text, routes)

def handle_score(text: str, criteria: str) -> float:
    """Interfaccia obbligatoria per lo score (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("score", text, criteria)

def handle_noul(text: str) -> str:
    """Interfaccia obbligatoria per noul (System 1 - Laya)."""
    return GlobalLayaHandler.evaluate("noul", text)

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
    parent_parser.add_argument("--json", action="store_true", help="Formatta l'output come JSON")

    parser = argparse.ArgumentParser(
        description="HAL System 1 (Laya) CLI Interface & Task Router",
        parents=[parent_parser],
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Comando System 1 da eseguire")

    # routing
    parser_routing = subparsers.add_parser(
        "routing",
        parents=[parent_parser],
        help="Classifica e instrada testo verso una lista di rotte",
    )
    parser_routing.add_argument("text", help="Testo o richiesta da instradare")
    parser_routing.add_argument("--routes", "-r", nargs="+", required=True, help="Rotte candidate (separate da spazio o virgola)")

    # choice
    parser_choice = subparsers.add_parser(
        "choice",
        parents=[parent_parser],
        help="Seleziona un'opzione tra alternative discrete",
    )
    parser_choice.add_argument("prompt", help="Prompt o domanda di decisione")
    parser_choice.add_argument("--options", "-o", nargs="+", required=True, help="Opzioni candidate (separate da spazio o virgola)")

    # score
    parser_score = subparsers.add_parser(
        "score",
        parents=[parent_parser],
        help="Valuta lo score euristico rispetto a un criterio",
    )
    parser_score.add_argument("text", help="Testo o oggetto da valutare")
    parser_score.add_argument("--criteria", "-c", required=True, help="Criterio di valutazione")

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

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    if args.subcommand == "routing":
        routes = _parse_list(args.routes)
        result = handle_routing(args.text, routes)
        if args.json:
            print(json.dumps({"task": "routing", "text": args.text, "routes": routes, "route": result}, ensure_ascii=False))
        else:
            print(result)
    elif args.subcommand == "choice":
        options = _parse_list(args.options)
        result = handle_choice(args.prompt, options)
        if args.json:
            print(json.dumps({"task": "choice", "prompt": args.prompt, "options": options, "choice": result}, ensure_ascii=False))
        else:
            print(result)
    elif args.subcommand == "score":
        result = handle_score(args.text, args.criteria)
        if args.json:
            print(json.dumps({"task": "score", "text": args.text, "criteria": args.criteria, "score": result}, ensure_ascii=False))
        else:
            print(result)
    elif args.subcommand == "noul":
        result = handle_noul(args.text)
        if args.json:
            print(json.dumps({"task": "noul", "text": args.text, "result": result}, ensure_ascii=False))
        else:
            print(result)
    elif args.subcommand == "triage":
        result = triage_request(args.text)
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            agent = result["agent"]
            skill = result.get("skill")
            if agent == "none":
                print("none (Nessun agente specifico richiesto — gestito da System 2 generico)")
            elif skill and skill != "core":
                print(f"{agent} -> skill: {skill}")
            else:
                print(agent)

if __name__ == "__main__":
    main()
