#!/usr/bin/env python3
"""Flush di ToDo.md verso CHANGELOG.md nel formato Keep a Changelog.

Uso (dalla root del repo): python3 agents/a-agentzero/scripts/agent-todo.py flush

Sposta in `## [Unreleased]` del CHANGELOG le voci `- [x]` (con le loro
sotto-voci) e quelle della sezione `## Già fatto`, mappando il tag nella
sezione KaC (bug → Fixed, feature → Added, altri → Changed). Le sezioni
`### ...` dentro «Già fatto» fissano la sezione KaC delle voci che contengono.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SECTION_ORDER = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
DONE_HEADING = "## Già fatto"
DONE_NOTE = (
    "_(Buffer pre-flush in formato Keep a Changelog: sotto `### Added`, "
    "`### Changed`, `### Fixed` o `### Removed`; `/todo` lo svuota nel CHANGELOG.)_"
)
CHECKED = re.compile(r"^- \[[xX]\] ")


def kac_section(tags: list[str]) -> str:
    if "bug" in tags:
        return "Fixed"
    if "feature" in tags:
        return "Added"
    return "Changed"


def clean_title(text: str) -> str:
    text = re.sub(r"\s*`#\w+`", "", text)
    text = re.sub(r"\s*·\s*P[0-2]\b", "", text)
    return text.strip()


def make_entry(
    first_line: str, children: list[str], forced: str | None
) -> tuple[str, str]:
    text = CHECKED.sub("", first_line)
    text = re.sub(r"^- ", "", text)
    tags = re.findall(r"`#(\w+)`", text)
    title = clean_title(text)
    for child in children:
        match = re.match(r"^\s+- Esito: (.*)$", child)
        if match:
            title = f"{title.rstrip('.')} — {match.group(1).strip()}"
    return forced or kac_section(tags), f"- {title}"


def split_todo(todo: str) -> tuple[str, list[tuple[str, str]]]:
    lines = todo.split("\n")
    kept: list[str] = []
    entries: list[tuple[str, str]] = []
    in_done = False
    forced: str | None = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == DONE_HEADING:
            in_done, forced = True, None
            kept.extend([line, "", DONE_NOTE])
            i += 1
            continue
        if line.startswith("## ") and in_done:
            in_done = False
            kept.extend(["", line])
            i += 1
            continue
        if in_done:
            if line.startswith("### "):
                name = line[4:].strip()
                forced = name if name in SECTION_ORDER else None
                i += 1
                continue
            if line.startswith("- "):
                children, i = _take_children(lines, i + 1)
                entries.append(make_entry(line, children, forced))
                continue
            i += 1  # righe vuote e nota: rigenerate sopra
            continue
        if CHECKED.match(line):
            children, i = _take_children(lines, i + 1)
            entries.append(make_entry(line, children, None))
            continue
        kept.append(line)
        i += 1
    return "\n".join(kept), entries


def _take_children(lines: list[str], start: int) -> tuple[list[str], int]:
    end = start
    while (
        end < len(lines) and lines[end].startswith((" ", "\t")) and lines[end].strip()
    ):
        end += 1
    return lines[start:end], end


def merge_unreleased(changelog: str, entries: list[tuple[str, str]]) -> str:
    """Merge flushed entries under '## [Unreleased]'.

    Il body della sezione si ferma al prossimo heading di livello 2 DI QUALSIASI
    stile: i repo che usano `## 1.7.0 (data)` (senza parentesi) non devono essere
    swallowati fino a EOF con perdita delle heading di versione (regressione
    2026-10-25). Se la sezione manca, è creata prima della prima release.
    """
    match = re.search(r"(?m)^## \[Unreleased\][^\n]*\n", changelog)
    if not match:
        block = "## [Unreleased]\n\n"
        first_version = re.search(r"(?m)^## \[?\d", changelog)
        if first_version:
            changelog = (
                changelog[: first_version.start()]
                + block
                + changelog[first_version.start() :]
            )
        else:
            changelog = changelog.rstrip("\n") + "\n\n" + block
        match = re.search(r"(?m)^## \[Unreleased\][^\n]*\n", changelog)
    if match is None:  # non può accadere: il blocco è appena stato inserito
        raise RuntimeError("sezione [Unreleased] non trovata dopo l'inserimento")
    nxt = re.search(r"(?m)^## ", changelog[match.end() :])
    end = match.end() + nxt.start() if nxt else len(changelog)
    body = changelog[match.end() : end]

    sections: dict[str, list[str]] = {}
    for part in re.split(r"(?m)^### ", body)[1:]:
        name, _, rest = part.partition("\n")
        sections[name.strip()] = [ln for ln in rest.split("\n") if ln.strip()]
    existing = {ln for items in sections.values() for ln in items}
    for section, line in entries:
        if line not in existing:
            sections.setdefault(section, []).append(line)
            existing.add(line)

    names = [n for n in SECTION_ORDER if n in sections]
    names += [n for n in sections if n not in SECTION_ORDER]
    rebuilt = "".join(f"\n### {n}\n\n" + "\n".join(sections[n]) + "\n" for n in names)
    tail = changelog[end:]
    return changelog[: match.end()] + rebuilt + ("\n" + tail if tail else "")


def flush(root: Path = Path(".")) -> int:
    todo_path, log_path = root / "ToDo.md", root / "CHANGELOG.md"
    if not todo_path.exists():
        print("Nessun ToDo.md trovato.")
        return 0
    new_todo, entries = split_todo(todo_path.read_text(encoding="utf-8"))
    if not entries:
        print("Nessun elemento da flushare in CHANGELOG.md.")
        return 0
    if log_path.exists():
        changelog = log_path.read_text(encoding="utf-8")
    else:
        changelog = "# Changelog\n\n## [Unreleased]\n\n"
    merged = merge_unreleased(changelog, entries)
    log_path.write_text(merged, encoding="utf-8")
    todo_path.write_text(new_todo.rstrip("\n") + "\n", encoding="utf-8")
    print(f"Flushate {len(entries)} voci in CHANGELOG.md.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "flush":
        sys.exit(flush())
    print("Usage: python3 agents/a-agentzero/scripts/agent-todo.py flush")
    sys.exit(2)
