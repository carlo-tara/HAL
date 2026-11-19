#!/usr/bin/env python3
"""hal-contract.py — contratto consumer HAL (de-racing step 3).

Idempotente. Di default è DRY-RUN (stampa il piano, zero scritture);
--apply:
  1. rimuove i mount HAL (symlink che risolvono dentro l'albero fisico di
     hal_gateway) dalle dir note di ogni consumer: agents/, .agents/, .zed/,
     product/ — ricorsivamente, senza seguire i link;
  2. installa/aggiorna il fence «hal-contract» nell'AGENTS.md del consumer:
     regole d'ingaggio + catalogo L1/comandi generato dai frontmatter del
     canonico (righe corte: il fence è iniettivo a ogni sessione).

Non tocca mai file reali del consumer (L2 proprie, contenuti): solo symlink
verso HAL e il blocco fenced. Le rimozioni di path tracciati vanno committate
nel repo del consumer dall'operatore (protocollo /commit).

Uso:
  python3 agents/scripts/hal-contract.py [--apply] [repo ...]
  senza repo: CONSUMERS di default.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

HAL = Path("/var/www/hal_gateway").resolve()
AGENTS = HAL / "agents"
CONSUMERS = [
    "/var/www/hal_system1",
    "/var/www/hal_system2",
    "/var/www/hal_mcp_tools",
    "/var/www/hal_mcp_docs",
    "/var/www/hal_seo",
    "/var/www/hal_translate",
    "/var/www/hal_tts",
    "/var/www/semidifocusing",
    "/var/www/brainbeez",
    "/var/www/WTP_App",
    "/var/www/InnerCircle",
]
SCAN_DIRS = ["agents", ".agents", ".zed", "product"]
BEGIN = "<!-- BEGIN hal-contract: generato da a-agentzero {ver} — NON EDITARE TRA I FENCE -->"
END = "<!-- END hal-contract -->"

L1 = [
    "a-agentzero",
    "a-b2b",
    "a-copywriter",
    "a-design",
    "a-harness",
    "a-knowledge",
    "a-product",
    "a-seozoom",
    "a-wordpress",
]
BUNDLED = {  # skill → owner
    "learn": "a-agentzero",
    "sync": "a-agentzero",
    "enrichment": "a-b2b",
    "personas": "a-product",
    "jtbd": "a-product",
    "gherkin": "a-product",
    "charts": "a-design",
    "illustrator": "a-design",
    "uiux": "a-design",
}
PROJECT_SKILLS = [
    "gdrive-sync-safe",
    "project-skills/laya",
    "project-skills/harness-agentfactory",
    "project-skills/harness-hal",
]
COMMANDS = [
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
    "laya",
]


def fm_field(path: Path, field: str) -> str:
    """Legge un campo del frontmatter (supporta `>-` multilinea)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return ""
    fm = m.group(1)
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        mm = re.match(rf"^{field}:\s*(.*)$", line)
        if not mm:
            continue
        val = mm.group(1).strip()
        if val in (">-", ">", "|", "|-"):
            parts = []
            for cont in lines[i + 1 :]:
                if re.match(r"^\S", cont):
                    break
                parts.append(cont.strip())
            return " ".join(p for p in parts if p)
        return val.strip("'\"")
    return ""


def shorten(desc: str, limit: int = 150) -> str:
    desc = re.sub(r"^Reason why:\s*.*?\.\s*", "", desc)
    desc = re.split(r"(?<=[.;])\s+", desc, maxsplit=1)[0] if len(desc) > limit else desc
    desc = desc.split(".")[0].strip(". ")
    return (desc[: limit - 1] + "…") if len(desc) > limit else desc


def agent_version() -> str:
    return fm_field(AGENTS / "a-agentzero" / "SKILL.md", "version") or "?"


def build_fence(ver: str) -> str:
    rows = []
    for name in L1:
        d = shorten(fm_field(AGENTS / name / "SKILL.md", "description"))
        rows.append(
            f"- **{name}** — {d}. Istruzioni: `read {HAL}/agents/{name}/SKILL.md`"
        )
    for name, owner in sorted(BUNDLED.items()):
        d = shorten(fm_field(AGENTS / owner / name / "SKILL.md", "description"))
        rows.append(
            f"- **{name}** (in {owner}) — {d}. `read {HAL}/agents/{owner}/{name}/SKILL.md`"
        )
    for ps in PROJECT_SKILLS:
        p = AGENTS / ps / "SKILL.md"
        if not p.is_file():
            continue
        name = ps.split("/")[-1]
        d = shorten(fm_field(p, "description"))
        note = " (solo gateway)" if "harness-hal" in ps else ""
        rows.append(f"- **{name}**{note} — {d}. `read {HAL}/agents/{ps}/SKILL.md`")
    cmds = ", ".join(f"`/{c}`" for c in COMMANDS)
    fence = "\n".join(
        [
            BEGIN.format(ver=ver),
            "## HAL — contratto consumer",
            "",
            f"- HAL canonico: `{HAL}` (repo `hal_gateway`). **Da questo progetto**: mai modificare",
            "  `agents/` del canonico, mai eseguire `link-workspace-skills.sh` / `deploy-all.sh` /",
            "  `publish-global-commands.sh` (guardie: «Guardia HAL» e path assoluto), mai ricreare",
            "  symlink HAL verso `.agents`/`agents`/`.zed`/`product` — i mount sono rimossi (de-racing).",
            f"- Script L0: invocarli con path assoluto, es. `bash {HAL}/agents/a-agentzero/scripts/<script>.sh`.",
            f"- Comandi L0 {cmds}: pubblicati come skill globali (`~/.agents/skills/`,",
            "  rigenerate solo da hal_gateway via `publish-global-commands.sh`); una skill locale",
            "  omonima ha priorità. Lettura del canone: `read`",
            f"  `{HAL}/agents/a-agentzero/commands/<cmd>.md`.",
            "- Le skill `.agents/skills/` presenti in questo repo sono L2 di questo progetto.",
            "",
            "### Catalogo HAL (generato — non editare a mano)",
            "",
            *rows,
            END,
        ]
    )
    return fence


def find_mounts(repo: Path) -> list[Path]:
    """Symlink (o dir symlink) che risolvono dentro HAL, nelle dir note."""
    found: list[Path] = []
    for rel in SCAN_DIRS:
        top = repo / rel
        if not top.exists() and not top.is_symlink():
            continue
        if top.is_symlink():
            try:
                if top.resolve().is_relative_to(HAL):
                    found.append(top)
                    continue
            except OSError:
                pass
        for root, dirs, files in os.walk(top, topdown=True, followlinks=False):
            keep = []
            for d in dirs:
                p = Path(root) / d
                if p.is_symlink():
                    try:
                        if p.resolve().is_relative_to(HAL):
                            found.append(p)
                            continue  # non scendere
                    except OSError:
                        pass
                keep.append(d)
            dirs[:] = keep
            for f in files:
                p = Path(root) / f
                if p.is_symlink():
                    try:
                        if p.resolve().is_relative_to(HAL):
                            found.append(p)
                    except OSError:
                        pass
    return sorted(found)


def fence_state(md: Path, ver: str) -> str:
    if not md.exists():
        return "create"
    text = md.read_text(encoding="utf-8")
    m = re.search(r"<!-- BEGIN hal-contract: generato da a-agentzero (\S+)", text)
    if not m:
        return "append"
    return "current" if m.group(1) == ver else "refresh"


def install_fence(md: Path, ver: str, apply: bool) -> str:
    state = fence_state(md, ver)
    if state == "current":
        return state
    if not apply:
        return state
    fence = build_fence(ver)
    if state == "create":
        md.write_text(f"{fence}\n", encoding="utf-8")
    elif state == "append":
        text = md.read_text(encoding="utf-8")
        md.write_text(text.rstrip("\n") + "\n\n" + fence + "\n", encoding="utf-8")
    else:  # refresh
        text = md.read_text(encoding="utf-8")
        new = re.sub(
            re.escape(BEGIN.format(ver=re.escape(ver)).replace("\\?", "."))
            + r".*?"
            + re.escape(END),
            fence,
            text,
            flags=re.S,
        )
        if new == text:
            new = re.sub(
                r"<!-- BEGIN hal-contract:.*?-->.*?<!-- END hal-contract -->",
                fence.replace("\\", "\\\\"),
                text,
                flags=re.S,
            )
        md.write_text(new, encoding="utf-8")
    return state


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="esegui (default: dry-run)")
    ap.add_argument("repos", nargs="*", default=CONSUMERS)
    args = ap.parse_args()
    ver = agent_version()
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"hal-contract [{mode}] — canonico {HAL} (a-agentzero {ver})")
    for r in args.repos:
        repo = Path(r)
        if not repo.is_dir():
            print(f"--- {repo}: NON DIR, saltato")
            continue
        mounts = find_mounts(repo)
        state = install_fence(repo / "AGENTS.md", ver, args.apply)
        print(f"--- {repo.name}: {len(mounts)} mount, fence {state}")
        for m in mounts:
            try:
                rel = m.relative_to(repo)
            except ValueError:
                rel = m
            if args.apply:
                if m.is_dir() and not m.is_symlink():
                    print(f"    SKIP (dir reale!): {rel}")
                    continue
                m.unlink()
                print(f"    rimosso: {rel}")
            else:
                print(f"    rimuoverò: {rel}")
    if not args.apply:
        print("\ndry-run: nessuna scrittura. Riesegui con --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
