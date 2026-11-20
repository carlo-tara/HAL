#!/usr/bin/env python3
"""prune-local-commands.py — rimuove i comandi locali dei consumer che duplicano i globali.

Contesto (de-racing): i comandi L0 HAL sono skill globali in ~/.agents/skills
(pubblicate solo da hal_gateway). Le copie locali che fossero rimaste nei
progetti (mirror di epoca symlink, `.zed/prompts`, `.agents/commands`) hanno
priorità sulle globali in Zed: se sono vecchie, il progetto esegue silenziosamente
un comando stantio. Questo script le elimina, ma SOLO se sono duplicati:

  1. body-uguali-al-canone (frontmatter rimosso con la stessa regex del
     canonico) → «duplicato-esatto», rimuovi;
  2. `.agents/skills/<cmd>/SKILL.md` generato dai publisher (description che
     inizia con «Command <cmd> for HAL workspace») → copia di rigenerazione:
     rimuovi anche se il body è vecchio (è la copia di un comando, non una
     voce scritta dal progetto; è lo shadowing più pericoloso);
  3. altrimenti → override di progetto autentico: KEEP e segnala.

Non tocca symlink (materia di hal-contract) e non tocca hal_gateway.
Dry-run di default; --apply per eliminare. Le directory rimaste vuote
(`.agents/commands`, `.zed/prompts`, skill dir) vengono rimosse.

Percorsi rimossi scritti in JSON su --plan-out (default /tmp/prune-removed.json)
per Allow-List dei commit per-repo.

Uso:
  python3 agents/scripts/prune-local-commands.py [--apply] [--plan-out PATH] [repo ...]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import consumers_list  # single source of truth: agents/consumers.list

HAL = Path(os.environ.get("HAL_ROOT", "/var/www/hal_gateway")).resolve()
CONSUMERS = (
    consumers_list.load_consumers()
)  # single source of truth: agents/consumers.list

# comando → canone (relativo a HAL). laya-cmd è l'alias-skill di laya.
CANON = {
    name: f"agents/a-agentzero/commands/{name}.md"
    for name in (
        "version",
        "document",
        "review",
        "improve",
        "commit",
        "todo",
        "slice",
        "cycle",
        "graph",
        "sync",
        "learn",
    )
}
CANON["laya"] = "agents/project-skills/laya/commands/laya.md"
SKILL_ALIAS = {"laya": "laya-cmd"}


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)


def fm_description(text: str) -> str:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return ""
    mm = re.search(r"(?m)^description:\s*(.*)$", m.group(1))
    return mm.group(1).strip().strip("'\"") if mm else ""


def candidates(repo: Path) -> list[tuple[str, Path]]:
    """(comando, percorso) delle possibili copie locali, senza symlink."""
    out: list[tuple[str, Path]] = []
    for cmd in CANON:
        skill_name = SKILL_ALIAS.get(cmd, cmd)
        for p in (
            repo / ".agents/commands" / f"{cmd}.md",
            repo / ".agents/skills" / skill_name / "SKILL.md",
            repo / ".zed/prompts" / f"{cmd}.md",
            repo / "product/adapters/commands" / f"{cmd}.md",
        ):
            if p.is_symlink():
                continue  # mount: materia di hal-contract, non di qui
            if p.is_file():
                out.append((cmd, p))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--apply", action="store_true", help="elimina davvero (default: dry-run)"
    )
    ap.add_argument("--plan-out", default="/tmp/prune-removed.json")
    ap.add_argument("repos", nargs="*", default=CONSUMERS)
    args = ap.parse_args()

    bodies: dict[str, str] = {}
    for cmd, rel in CANON.items():
        src = HAL / rel
        if not src.is_file():
            print(f"ERRORE: canone assente {src}", file=sys.stderr)
            return 1
        bodies[cmd] = strip_frontmatter(src.read_text(encoding="utf-8"))

    removed: dict[str, list[str]] = {}
    for r in args.repos:
        repo = Path(r)
        if not repo.is_dir():
            print(f"--- {repo}: NON DIR, saltato")
            continue
        if repo.resolve() == HAL:
            print("--- hal_gateway: canone, mai toccato")
            continue
        removes: list[tuple[str, Path, str]] = []
        keeps: list[tuple[str, Path]] = []
        for cmd, path in candidates(repo):
            text = path.read_text(encoding="utf-8")
            if strip_frontmatter(text) == bodies[cmd]:
                removes.append((cmd, path, "duplicato-esatto"))
                continue
            desc = fm_description(text)
            skill_name = SKILL_ALIAS.get(cmd, cmd)
            if (
                path.parent.name == skill_name
                and path.name == "SKILL.md"
                and desc.startswith(f"Command {skill_name} for HAL workspace")
            ):
                removes.append((cmd, path, "copia-di-rigenerazione-stale"))
            else:
                keeps.append((cmd, path))

        rels: list[str] = []
        if removes or keeps:
            print(f"--- {repo.name}: {len(removes)} da rimuovere, {len(keeps)} keep")
        for cmd, path, why in removes:
            if args.apply:
                path.unlink()
                d = path.parent
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()
            print(
                f"    [{'APPLY' if args.apply else 'DRY'}] {path.relative_to(repo)}  ({cmd}: {why})"
            )
            rels.append(str(path.relative_to(repo)))
        for cmd, path in keeps:
            print(
                f"    KEEP {path.relative_to(repo)}  ({cmd}: override? body diverso da canone)"
            )
        if rels:
            removed[repo.name] = rels
        # directory-genitori vuote leftover
        if args.apply:
            for d in (
                repo / ".agents/commands",
                repo / ".zed/prompts",
                repo / "product/adapters/commands",
            ):
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()

    Path(args.plan_out).write_text(
        json.dumps(removed, ensure_ascii=False, indent=0), encoding="utf-8"
    )
    tot = sum(len(v) for v in removed.values())
    print(
        f"\n{'APPLY' if args.apply else 'DRY-RUN'}: {tot} file in {len(removed)} repo; piano: {args.plan_out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
