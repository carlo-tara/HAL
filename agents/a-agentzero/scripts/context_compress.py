#!/usr/bin/env python3
"""Semantic-aware compression for HAL skill/instruction files.

Derivato da vidanov/context-compress: compressione aware del contenuto per tipo,
deduplicazione cross-file, stima token e validazione dei marker comportamentali.
Nessuna dipendenza esterna.

Uso CLI:
    python3 context_compress.py stats <file|dir...>
    python3 context_compress.py dedup <dir>
    python3 context_compress.py compress <file|dir> [-o out] [--dry-run]
    python3 context_compress.py validate <original> <compressed>
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import sys
from pathlib import Path
from typing import Any

# ── Costanti ────────────────────────────────────────────────────────────────

SAFETY_RE = re.compile(
    r"\b(?:mai|never|must not|non negoziabile|obbligatorio|vietato|"
    r"denylist|rbac|pii|segret[oi]|credenziali|sicurezza)\b",
    re.IGNORECASE,
)

FILLER_PATTERNS = [
    # Italian
    (re.compile(r"\bè importante notare che\b", re.I), ""),
    (re.compile(r"\bsi noti che\b", re.I), ""),
    (re.compile(r"\btenere presente che\b", re.I), ""),
    (re.compile(r"\bricorda che\b", re.I), ""),
    (re.compile(r"\bassicurarsi di\b", re.I), ""),
    (re.compile(r"\bassicurarsi che\b", re.I), ""),
    (re.compile(r"\binoltre\b", re.I), ""),
    (re.compile(r"\bovviamente\b", re.I), ""),
    (re.compile(r"\bnaturalmente\b", re.I), ""),
    (re.compile(r"\bdifault\b", re.I), ""),  # typo guard
    (re.compile(r"\bin generale\b", re.I), ""),
    (re.compile(r"\bcome saprai\b", re.I), ""),
    # English
    (re.compile(r"\bnote that\b", re.I), ""),
    (re.compile(r"\bit is important to note\b", re.I), ""),
    (re.compile(r"\bkeep in mind that\b", re.I), ""),
    (re.compile(r"\bmake sure to\b", re.I), ""),
    (re.compile(r"\bin order to\b", re.I), "to"),
    (re.compile(r"\bas a matter of fact\b", re.I), ""),
    (re.compile(r"\bbasically\b", re.I), ""),
    (re.compile(r"\bactually\b", re.I), ""),
    (re.compile(r"\bsimply\b", re.I), ""),
    (re.compile(r"\bjust\b", re.I), ""),
]

# Normalizzazione spazi / punteggiatura residua dopo rimozione filler
_CLEANUP = re.compile(r"[^\S\n]{2,}")  # non sostituisce newline con spazio


# ── Classificazione ─────────────────────────────────────────────────────────

_SAFETY_TITLE = re.compile(
    r"(?:regole?\s*(?:di\s*)?(?:sicurezza|security)|sicurezza|security)",
    re.I,
)
_REF_TITLE = re.compile(
    r"(?:riferimenti?|references?|paths?|elenco|collegamenti?)",
    re.I,
)
_STYLE_TITLE = re.compile(
    r"(?:stile|style|tono|tone|personalità|personality|voce|voice|prospettiva)",
    re.I,
)
_LIST_LINE = re.compile(r"^\s*[-*]\s")
_TABLE_LINE = re.compile(r"^\s*\|")


def classify_section(title: str, content: str) -> str:
    """Classifica una sezione markdown nel suo tipo di contenuto."""
    # Code: traccia stati dei fence e conta caratteri reali del codice
    lines = content.splitlines(True)
    in_fence = False
    code_chars = 0
    total_chars = 0
    fence_count = 0
    for line in lines:
        total_chars += len(line)
        stripped = line.strip()
        if stripped.startswith("```"):
            fence_count += 1
            in_fence = not in_fence
        elif in_fence:
            code_chars += len(line)
    if fence_count >= 2 and total_chars > 0 and code_chars / total_chars > 0.4:
        return "code"

    # Safety: titolo o contenuto contiene parole chiave di sicurezza
    if _SAFETY_TITLE.search(title) or SAFETY_RE.search(content):
        return "safety"

    # Reference: titolo o struttura lista/tabella
    if _REF_TITLE.search(title):
        return "reference"
    non_empty = [l for l in content.splitlines() if l.strip()]
    if (
        non_empty
        and (
            sum(1 for l in non_empty if _LIST_LINE.match(l))
            + sum(1 for l in non_empty if _TABLE_LINE.match(l))
        )
        / max(len(non_empty), 1)
        > 0.6
    ):
        return "reference"

    # Personality: titolo indica stile/tono
    if _STYLE_TITLE.search(title):
        return "personality"

    return "procedure"


_DEFAULT_LEVELS: dict[str, str] = {
    "safety": "light",
    "code": "none",
    "reference": "max",
    "personality": "heavy",
    "procedure": "medium",
}


# ── Frontmatter & splitting ─────────────────────────────────────────────────


def split_frontmatter(text: str) -> tuple[str, str]:
    """Separa il frontmatter YAML (tra ---) dal corpo restante."""
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if m:
        return m.group(0), text[m.end() :]
    return "", text


def split_sections(body: str) -> list[tuple[str, str]]:
    """Divide il corpo in sezioni per heading (# ...), preservando i blocchi ```."""
    sections: list[tuple[str, str]] = []
    current_title = ""
    lines: list[str] = []
    in_fence = False

    for line in body.splitlines(True):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue

        if not in_fence and line.startswith("#"):
            if lines:
                sections.append((current_title, "".join(lines)))
            current_title = line.lstrip("#").strip()
            lines = [line]
        else:
            lines.append(line)

    if lines:
        sections.append((current_title, "".join(lines)))
    return sections


# ── Compressione per livello ────────────────────────────────────────────────

_STRIP_EMPHASIS = [
    (re.compile(r"\*\*(.+?)\*\*"), r"\1"),
    (re.compile(r"__(.+?)__"), r"\1"),
]


def _strip_emphasis(text: str) -> str:
    for pat, repl in _STRIP_EMPHASIS:
        text = pat.sub(repl, text)
    return text


def _collapse_blanks(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def _remove_decorative_rules(text: str) -> str:
    # Righe solo separatori decorativi (---, ***, ___) fuori dal frontmatter
    return re.sub(r"^(?<!-)\s*([-*_]\s*){3,}$\n?", "", text, flags=re.M)


def _collapse_list_blanks(text: str) -> str:
    """Rimuove righe vuote tra elementi consecutivi di lista, preservando almeno un newline."""
    prev = ""
    while prev != text:
        prev = text
        # Sostituisce \n\n (riga vuota) tra item con \n (singolo newline)
        text = re.sub(r"(\n- [^\n]+)\n\n(?=\n?- )", r"\1\n", text)
    return text


def _apply_fillers(text: str) -> str:
    for pat, repl in FILLER_PATTERNS:
        text = pat.sub(repl, text)
    text = _CLEANUP.sub(" ", text)
    # Pulizia punteggiatura residua (es. "word ." → "word.")
    text = re.sub(r"\s+([.,;:!?)])", r"\1", text)
    return text


_COMPRESSORS: dict[str, list[tuple[str, Any]]] = {
    "none": [],
    "light": [("emphasis", _strip_emphasis), ("blanks", _collapse_blanks)],
    "medium": [
        ("emphasis", _strip_emphasis),
        ("decorative", _remove_decorative_rules),
        ("blanks", _collapse_blanks),
    ],
    "heavy": [
        ("emphasis", _strip_emphasis),
        ("decorative", _remove_decorative_rules),
        ("fillers", _apply_fillers),
        ("blanks", _collapse_blanks),
    ],
    "max": [
        ("emphasis", _strip_emphasis),
        ("decorative", _remove_decorative_rules),
        ("list_blanks", _collapse_list_blanks),
        ("blanks", _collapse_blanks),
    ],
}


def _compress_segment(segment: str, level: str) -> str:
    """Applica le regole di compressione per un segmento non-code."""
    rules = _COMPRESSORS.get(level, [])
    result = segment
    for _, fn in rules:
        result = fn(result)
    return result


def _compress_section(section_text: str, level: str) -> str:
    """Comprime una sezione proteggendo i blocchi di codice."""
    parts: list[str] = []
    in_fence = False
    current_parts: list[str] = []

    for line in section_text.splitlines(True):
        if line.strip().startswith("```"):
            if in_fence:
                # Fine blocco: comprime prima, poi aggiunge il blocco
                parts.append(_compress_segment("".join(current_parts), level))
                current_parts = []
            in_fence = not in_fence
            current_parts.append(line)
        else:
            current_parts.append(line)

    if current_parts:
        parts.append(_compress_segment("".join(current_parts), level))

    return "".join(parts)


# ── API pubblica ────────────────────────────────────────────────────────────


def estimate_tokens(text: str) -> int:
    """Stima approssimativa dei token (chars / 4, arrotondato per eccesso)."""
    return math.ceil(len(text) / 4)


def extract_safety_sentences(text: str) -> list[str]:
    """Estrae frasi contenenti marker di sicurezza dal testo originale."""
    sentences: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.lstrip("- ").strip()
        if not stripped:
            continue
        if SAFETY_RE.search(stripped):
            sentences.append(stripped)
    return sentences


def validate_markers(original: str, compressed: str) -> tuple[bool, list[str]]:
    """Verifica che tutte le frasi di sicurezza originali siano presenti nel compresso."""
    originals = extract_safety_sentences(original)
    # Normalizza entrambi i testi: minuscolo, spazi collassati, enfasi rimossa
    norm_comp = re.sub(r"\s+", " ", _strip_emphasis(compressed.lower()))
    missing: list[str] = []
    for sent in originals:
        norm_sent = re.sub(r"\s+", " ", _strip_emphasis(sent.lower()))
        if norm_sent not in norm_comp:
            missing.append(sent)
    return len(missing) == 0, missing


def compress_text(
    text: str, config: dict | None = None, level: str | None = None
) -> tuple[str, dict]:
    """Comprime un testo markdown applicando regole semantiche per tipo di sezione.

    Args:
        text: testo markdown completo (con eventuale frontmatter).
        config: configurazione opzionale (parse_config output).
        level: livello esplicito sovrascrive la classificazione automatica.

    Returns:
        (testo_compresso, report_dict con info per-sezione).
    """
    fm, body = split_frontmatter(text)
    sections = split_sections(body)
    report_sections: list[dict[str, Any]] = []
    result_parts: list[str] = [fm]

    for title, content in sections:
        ctype = classify_section(title, content)
        comp_level = level or _DEFAULT_LEVELS.get(ctype, "medium")
        before = len(content)
        compressed = _compress_section(content, comp_level)
        after = len(compressed)
        report_sections.append(
            {
                "title": title,
                "type": ctype,
                "level": comp_level,
                "chars_before": before,
                "chars_after": after,
                "saved": before - after,
            }
        )
        result_parts.append(compressed)

    result = "".join(result_parts)
    # Garanzia: output termina con newline singolo
    result = result.rstrip("\n") + "\n" if result.strip() else result
    return result, {
        "sections": report_sections,
        "total_saved": sum(s["saved"] for s in report_sections),
    }


def compress_file(path: Path, config: dict | None = None) -> tuple[str, dict]:
    """Comprime un singolo file, applicando eventuali override dalla config."""
    text = path.read_text(encoding="utf-8")
    ov = (config or {}).get("overrides", {}).get(path.name, {})
    explicit_level = ov.get("compression_level")
    if explicit_level == "none":
        return text, {"sections": [], "total_saved": 0}
    return compress_text(text, config=config, level=explicit_level)


# ── Deduplicazione ──────────────────────────────────────────────────────────


def _normalize_block(block: str) -> str:
    """Normalizza un blocco per il confronto (minuscolo, spazi collassati, no emphasis)."""
    t = block.lower()
    t = _strip_emphasis(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def dedup_blocks(texts: dict[str, str]) -> list[dict[str, Any]]:
    """Trova blocchi duplicati tra più testi.

    Args:
        texts: mapping {nome_file: contenuto}.

    Returns:
        Lista di gruppi di duplicati con posizioni e byte sprecati stimati.
    """
    blocks_by_hash: dict[str, list[dict[str, Any]]] = {}

    for name, text in texts.items():
        _, body = split_frontmatter(text)
        # Split in paragraphs separated by blank lines
        paragraphs = re.split(r"\n{2,}", body)
        for para in paragraphs:
            norm = _normalize_block(para)
            if len(norm) < 60:
                continue
            h = hashlib.md5(norm.encode()).hexdigest()
            entry = {"name": name, "preview": norm[:80], "norm_len": len(norm)}
            blocks_by_hash.setdefault(h, []).append(entry)

    results: list[dict[str, Any]] = []
    for h, entries in blocks_by_hash.items():
        if len(entries) <= 1:
            continue
        locations = [{"file": e["name"], "preview": e["preview"]} for e in entries]
        wasted = (len(entries) - 1) * entries[0]["norm_len"]
        results.append(
            {
                "hash": h,
                "locations": locations,
                "wasted_chars": wasted,
                "count": len(entries),
            }
        )
    return sorted(results, key=lambda g: g["wasted_chars"], reverse=True)


# ── Statistiche ──────────────────────────────────────────────────────────────


def stats(paths: list[Path]) -> list[dict[str, Any]]:
    """Calcola statistiche token per una lista di file/directory."""
    rows: list[dict[str, Any]] = []
    for p in paths:
        if p.is_dir():
            for sub in sorted(p.rglob("*.md")):
                rows.append(
                    {
                        "path": str(sub),
                        "chars": sub.stat().st_size,
                        "est_tokens": estimate_tokens(str(sub)),
                    }
                )
        elif p.is_file():
            text = p.read_text(encoding="utf-8")
            rows.append(
                {
                    "path": str(p),
                    "chars": len(text),
                    "est_tokens": estimate_tokens(text),
                }
            )
    return rows


# ── Config parser (YAML subset minimale) ────────────────────────────────────


def _parse_scalar(val: str) -> Any:
    v = val.strip().strip('"').strip("'")
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    try:
        return int(v)
    except ValueError:
        pass
    return v


def parse_config(raw: str) -> dict[str, Any]:
    """Parser YAML minimale per compress.yaml (solo chiavi semplici e nidificazione ≤ 3 livelli)."""
    cfg: dict[str, Any] = {"defaults": {}, "overrides": {}}
    current_top: str | None = None
    current_file: str | None = None

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()

        if indent == 0:
            current_top = key
            current_file = None
            cfg.setdefault(current_top, {})
        elif indent >= 2 and current_top == "overrides" and not val:
            current_file = key.strip("\"'")
            cfg["overrides"].setdefault(current_file, {})
        elif current_top:
            target = cfg[current_top]
            if current_top == "overrides" and current_file:
                target = cfg["overrides"][current_file]
            target[key] = _parse_scalar(val)

    return cfg


def load_config(path: Path) -> dict[str, Any]:
    """Carica una configurazione da file compress.yaml."""
    return parse_config(path.read_text(encoding="utf-8"))


# ── CLI ─────────────────────────────────────────────────────────────────────


def cmd_stats(args: argparse.Namespace) -> None:
    paths = [Path(p) for p in args.path]
    rows = stats(paths)
    total_chars = sum(r["chars"] for r in rows)
    total_tokens = sum(r["est_tokens"] for r in rows)
    print(f"{'File':<50} {'Chars':>8} {'Tokens~':>8}")
    print("-" * 70)
    for r in rows:
        print(f"{r['path']:<50} {r['chars']:>8} {r['est_tokens']:>8}")
    print("-" * 70)
    print(f"{'Totale':<50} {total_chars:>8} {total_tokens:>8}")


def cmd_dedup(args: argparse.Namespace) -> None:
    d = Path(args.dir)
    texts: dict[str, str] = {}
    for md in sorted(d.rglob("*.md")):
        texts[md.name] = md.read_text(encoding="utf-8")
    groups = dedup_blocks(texts)
    if not groups:
        print("Nessun duplicato trovato.")
        return
    total_wasted = 0
    for g in groups:
        locs = ", ".join(f"{l['file']} ({l['preview'][:40]}…)" for l in g["locations"])
        print(f"[{g['count']}x] ~{g['wasted_chars']} chars — {locs}")
        total_wasted += g["wasted_chars"]
    print(
        f"\nTotale sprecato: ~{total_wasted} chars (~{estimate_tokens(str(total_wasted))} token)"
    )


def cmd_compress(args: argparse.namespace) -> None:
    src = Path(args.src)
    cfg = load_config(args.config) if args.config else {}

    if src.is_file():
        compressed, report = compress_file(src, cfg)
        out_path = (
            Path(args.output)
            if args.output
            else src.with_suffix(src.suffix + ".compressed.md")
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(compressed, encoding="utf-8")
        saved = report["total_saved"]
        pct = (
            saved / max(report["sections"][0]["chars_before"], 1) * 100
            if report["sections"]
            else 0
        )
        print(f"{src} → {out_path}: -{saved} chars (-{pct:.1f}%)")
        for s in report["sections"]:
            print(
                f"  [{s['type']}] {s['title'] or '(intro)'}: {s['chars_before']}→{s['chars_after']} ({s['level']})"
            )
    elif src.is_dir():
        written = 0
        for md in sorted(src.rglob("*.md")):
            compressed, report = compress_file(md, cfg)
            out_path = src / f"{md.stem}.compressed{md.suffix}"
            out_path.write_text(compressed, encoding="utf-8")
            written += 1
        print(f"{written} file compressi in {src}/")
    else:
        print(f"Errore: percorso non trovato {src}", file=sys.stderr)
        sys.exit(1)


def cmd_validate(args: argparse.Namespace) -> None:
    orig = Path(args.original).read_text(encoding="utf-8")
    comp = Path(args.compressed).read_text(encoding="utf-8")
    ok, missing = validate_markers(orig, comp)
    if ok:
        print("OK — tutti i marker di sicurezza preservati.")
    else:
        print(f"FAIL — {len(missing)} marker persi:")
        for m in missing:
            print(f"  ✗ {m[:80]}")
        sys.exit(1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd")

    p_stats = sub.add_parser("stats", help="Stima token per file/directory")
    p_stats.add_argument("path", nargs="+", help="File o directory da analizzare")

    p_dedup = sub.add_parser("dedup", help="Trova blocchi duplicati tra file")
    p_dedup.add_argument("dir", help="Directory da scansionare")

    p_comp = sub.add_parser("compress", help="Comprimi file o directory")
    p_comp.add_argument("src", help="File o directory sorgente")
    p_comp.add_argument(
        "-o", "--output", default=None, help="Percorso output (file) o dir"
    )
    p_comp.add_argument("--config", type=Path, default=None, help="File compress.yaml")
    p_comp.add_argument(
        "--dry-run", action="store_true", help="Solo calcolo, nessuna scrittura"
    )

    p_val = sub.add_parser(
        "validate", help="Verifica preservazione marker di sicurezza"
    )
    p_val.add_argument("original", help="File originale")
    p_val.add_argument("compressed", help="File compresso")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0

    dispatch = {
        "stats": cmd_stats,
        "dedup": cmd_dedup,
        "compress": cmd_compress,
        "validate": cmd_validate,
    }
    dispatch[args.cmd](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
