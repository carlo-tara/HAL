#!/usr/bin/env python3
"""Token Budget Telemetry — Traccia l'efficienza token delle sessioni HAL.

Traccia: tokens in/out, chiamate System1 vs System2, file letti, diff size,
violazioni regole, skill compression e deduplicazione. Output JSONL in
events/token-budget.jsonl.

Uso:
    python3 token_budget.py init                    # Inizia sessione
    python3 token_budget.py log s1_call             # Log chiamata System1
    python3 token_budget.py log s2_call             # Log chiamata System2
    python3 token_budget.py log file_read <path> <lines>
    python3 token_budget.py log diff_read <lines>
    python3 token_budget.py log output <tokens>
    python3 token_budget.py log violation <type>
    python3 token_budget.py log attachment_filter <original_count> <summary>
    python3 token_budget.py log lazy_load <path> <lines_read> <total_lines>
    python3 token_budget.py log chunk_score <score> <threshold>
    python3 token_budget.py log skill_compress <orig_bytes> <comp_bytes>
    python3 token_budget.py log dedup_found <blocks> <bytes_saved>
    python3 token_budget.py report                  # Report finale
    python3 token_budget.py status                  # Stato corrente
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Directory eventi: stessa struttura del progetto esistente
EVENTS_DIR = Path("events")
TOKEN_BUDGET_FILE = EVENTS_DIR / "token-budget.jsonl"
SESSION_FILE = EVENTS_DIR / "token-budget-session.json"

# Thresholds di default
DEFAULT_OUTPUT_TARGET = 500  # token max output per sessione
DEFAULT_CONTEXT_TARGET = 50000  # token max context caricato
DEFAULT_S1_S2_RATIO = 3.0  # rapporto minimo S1:S2


def _ensure_events_dir():
    """Crea la directory events se non esiste."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)


def _read_session():
    """Legge lo stato della sessione corrente."""
    _ensure_events_dir()
    if SESSION_FILE.exists():
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None


def _write_session(data):
    """Salva lo stato della sessione."""
    _ensure_events_dir()
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _append_event(event_type, data):
    """Aggiunge un evento al file JSONL."""
    _ensure_events_dir()
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        **data,
    }
    with open(TOKEN_BUDGET_FILE, "a") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def cmd_init():
    """Inizia una nuova sessione di tracciamento."""
    session = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "s1_calls": 0,
        "s2_calls": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "files_read": 0,
        "total_lines_read": 0,
        "diff_lines_read": 0,
        "violations": [],
        "attachments_filtered": 0,
        "lazy_loads": 0,
        "chunks_scored": 0,
        "skill_compressions": 0,
        "dedup_blocks": 0,
        "context_saved_estimates": 0,
    }
    _write_session(session)
    print(f"Sessione iniziata: {session['started_at']}")
    print(f"Log: {TOKEN_BUDGET_FILE}")


def cmd_log(args):
    """Registra un evento di telemetria."""
    if not args:
        print("Errore: specificare tipo evento e parametri", file=sys.stderr)
        print(
            "Tipi: s1_call, s2_call, file_read, diff_read, output, violation,",
            file=sys.stderr,
        )
        print(
            "  attachment_filter, lazy_load, chunk_score, skill_compress,",
            file=sys.stderr,
        )
        print("  dedup_found", file=sys.stderr)
        sys.exit(1)

    event_type = args[0]
    session = _read_session()
    if not session:
        print(
            "Errore: sessione non inizializzata. Eseguire 'init' prima.",
            file=sys.stderr,
        )
        sys.exit(1)

    if event_type == "s1_call":
        session["s1_calls"] += 1
        _append_event("s1_call", {"count": session["s1_calls"]})

    elif event_type == "s2_call":
        session["s2_calls"] += 1
        _append_event("s2_call", {"count": session["s2_calls"]})

    elif event_type == "file_read" and len(args) >= 3:
        path = args[1]
        lines = int(args[2])
        session["files_read"] += 1
        session["total_lines_read"] += lines
        _append_event("file_read", {"path": path, "lines": lines})

    elif event_type == "diff_read" and len(args) >= 2:
        lines = int(args[1])
        session["diff_lines_read"] += lines
        _append_event("diff_read", {"lines": lines})

    elif event_type == "output" and len(args) >= 2:
        tokens = int(args[1])
        session["total_output_tokens"] += tokens
        _append_event(
            "output", {"tokens": tokens, "cumulative": session["total_output_tokens"]}
        )

    elif event_type == "violation" and len(args) >= 2:
        vtype = args[1]
        session["violations"].append(vtype)
        _append_event("violation", {"type": vtype, "total": len(session["violations"])})

    elif event_type == "attachment_filter" and len(args) >= 3:
        original = int(args[1])
        summary_len = int(args[2])
        saved = max(0, original - summary_len)
        session["attachments_filtered"] += 1
        session["context_saved_estimates"] += saved
        _append_event(
            "attachment_filter",
            {
                "original_count": original,
                "summary_length": summary_len,
                "saved_tokens": saved,
            },
        )

    elif event_type == "lazy_load" and len(args) >= 4:
        path = args[1]
        lines_read = int(args[2])
        total_lines = int(args[3])
        session["lazy_loads"] += 1
        saved = max(0, total_lines - lines_read)
        session["context_saved_estimates"] += saved
        _append_event(
            "lazy_load",
            {
                "path": path,
                "lines_read": lines_read,
                "total_lines": total_lines,
                "saved_lines": saved,
            },
        )

    elif event_type == "chunk_score" and len(args) >= 3:
        score = float(args[1])
        threshold = float(args[2])
        session["chunks_scored"] += 1
        passed = score >= threshold
        session["context_saved_estimates"] += (
            0 if passed else 200
        )  # stima token salvati
        _append_event(
            "chunk_score", {"score": score, "threshold": threshold, "passed": passed}
        )

    elif event_type == "skill_compress" and len(args) >= 3:
        orig = int(args[1])
        comp = int(args[2])
        saved = max(0, (orig - comp) // 4)
        session["skill_compressions"] += 1
        session["context_saved_estimates"] += saved
        _append_event(
            "skill_compress",
            {
                "original_bytes": orig,
                "compressed_bytes": comp,
                "saved_tokens": saved,
            },
        )

    elif event_type == "dedup_found" and len(args) >= 3:
        blocks = int(args[1])
        bytes_saved = int(args[2])
        session["dedup_blocks"] += blocks
        session["context_saved_estimates"] += bytes_saved // 4
        _append_event(
            "dedup_found",
            {
                "blocks": blocks,
                "bytes_saved": bytes_saved,
                "tokens_saved": bytes_saved // 4,
            },
        )

    else:
        print(f"Errore: tipo evento sconosciuto '{event_type}'", file=sys.stderr)
        sys.exit(1)

    _write_session(session)
    print(f"Evento registrato: {event_type}")


def cmd_report():
    """Stampa il report finale della sessione."""
    session = _read_session()
    if not session:
        print("Nessuna sessione attiva.", file=sys.stderr)
        sys.exit(1)

    s1 = session["s1_calls"]
    s2 = session["s2_calls"]
    s1_s2_ratio = s1 / max(s2, 1)
    output_target_met = session["total_output_tokens"] <= DEFAULT_OUTPUT_TARGET
    violations_count = len(session["violations"])

    print("=" * 60)
    print("TOKEN BUDGET REPORT")
    print("=" * 60)
    print(f"Iniziata:       {session['started_at']}")
    print(f"System 1 call:   {s1}")
    print(f"System 2 call:   {s2}")
    print(f"Rapporto S1:S2:  {s1_s2_ratio:.1f}x (target ≥{DEFAULT_S1_S2_RATIO}x)")
    print(f"Input tokens:    {session['total_input_tokens']:,}")
    print(
        f"Output tokens:   {session['total_output_tokens']:,} (target ≤{DEFAULT_OUTPUT_TARGET:,}) {'✓' if output_target_met else '✗'}"
    )
    print(f"File letti:      {session['files_read']}")
    print(f"Linee lette:     {session['total_lines_read']:,}")
    print(f"Diff righe:      {session['diff_lines_read']:,}")
    print(
        f"Violazioni:      {violations_count} {'✓' if violations_count == 0 else '✗'}"
    )
    print(f"Allegati filtrati: {session['attachments_filtered']}")
    print(f"Lazy load hit:   {session['lazy_loads']}")
    print(f"Chunk scored:    {session['chunks_scored']}")
    print(f"Skill compress:  {session['skill_compressions']}")
    print(f"Dedup blocchi:   {session['dedup_blocks']}")
    print(f"Context stimato salvato: ~{session['context_saved_estimates']:,} token")
    print("=" * 60)

    if session["violations"]:
        print("\nViolazioni:")
        for v in session["violations"]:
            print(f"  - {v}")

    # Salva report come evento
    _append_event(
        "report",
        {
            "s1_calls": s1,
            "s2_calls": s2,
            "s1_s2_ratio": round(s1_s2_ratio, 2),
            "output_tokens": session["total_output_tokens"],
            "output_target_met": output_target_met,
            "files_read": session["files_read"],
            "total_lines_read": session["total_lines_read"],
            "diff_lines_read": session["diff_lines_read"],
            "violations_count": violations_count,
            "attachments_filtered": session["attachments_filtered"],
            "lazy_loads": session["lazy_loads"],
            "chunks_scored": session["chunks_scored"],
            "skill_compressions": session["skill_compressions"],
            "dedup_blocks": session["dedup_blocks"],
            "context_saved_estimates": session["context_saved_estimates"],
        },
    )


def cmd_status():
    """Mostra lo stato corrente della sessione."""
    session = _read_session()
    if not session:
        print("Nessuna sessione attiva. Eseguire 'init' per iniziare.")
        return

    s1 = session["s1_calls"]
    s2 = session["s2_calls"]
    ratio = s1 / max(s2, 1)
    output_pct = (
        min(100, (session["total_output_tokens"] / DEFAULT_OUTPUT_TARGET) * 100)
        if DEFAULT_OUTPUT_TARGET
        else 0
    )

    print(
        f"S1: {s1} | S2: {s2} | Ratio: {ratio:.1f}x | Output: {session['total_output_tokens']}/{DEFAULT_OUTPUT_TARGET} ({output_pct:.0f}%) | Violazioni: {len(session['violations'])}"
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        cmd_init()
    elif command == "log":
        cmd_log(sys.argv[2:])
    elif command == "report":
        cmd_report()
    elif command == "status":
        cmd_status()
    else:
        print(f"Comando sconosciuto: {command}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
