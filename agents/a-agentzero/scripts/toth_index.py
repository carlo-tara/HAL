#!/usr/bin/env python3
"""toth_index.py — indice meccanico del canone HAL (slice v0-toth-index).

Gemello del catalogo «hal-contract»: stesse liste-fonte (L1, BUNDLED,
PROJECT_SKILLS, COMMANDS lette da agents/scripts/hal-contract.py) e stesso
parser (fm_field/shorten). Non aggiunge regole proprie; dove il fence tace
sulle fonti mancanti (skipped di build_fence), l'indice le marca
present=false: il drift del canone e il deliverable di v0, non un effetto
collaterale. Unica eccezione dichiarata: COMMAND_SOURCE_OVERRIDES, che
vincola l'esistenza dei comandi alla stessa fonte del publisher globale
(HT-017; test_override_tied_to_publisher impedisce la divergenza).

Uso:
  python3 agents/a-agentzero/scripts/toth_index.py            # rigenera
  python3 agents/a-agentzero/scripts/toth_index.py --check    # exit 1 su drift
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _import_contract() -> object:
    path = REPO_ROOT / "agents" / "scripts" / "hal-contract.py"
    spec = importlib.util.spec_from_file_location("hal_contract", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HC = _import_contract()

ARTIFACT_RELPATH = "agents/a-agentzero/references/toth-index.json"
ARTIFACT_PATH = REPO_ROOT / ARTIFACT_RELPATH

KINDS = ("agent", "bundled", "project", "command")

# Comandi la cui fonte canonica NON e' in a-agentzero/commands: mirror della
# LAYASRC dichiarata da publish-global-commands.sh (guardia: test_toth_index).
COMMAND_SOURCE_OVERRIDES = {
    "laya": "agents/project-skills/laya/commands/laya.md",
}


def default_lists() -> dict:
    return dict(l1=list(HC.L1), bundled=dict(HC.BUNDLED),
                project_skills=list(HC.PROJECT_SKILLS),
                commands=list(HC.COMMANDS))


def _entry(root: Path, name: str, kind: str, rel: str, *, host: str | None = None) -> dict:
    p = root / rel
    present = p.is_file()
    ext = HC.fm_field(p, "extends") if present else ""
    return {
        "kind": kind,
        "name": name,
        "path": rel,
        "host": host,
        "parent": (ext or None) if kind == "agent" else None,
        "version": (HC.fm_field(p, "version") or None) if present else None,
        "description": HC.shorten(HC.fm_field(p, "description")) if present else None,
        "present": present,
    }


def build_index(root: Path, *, l1=None, bundled=None, project_skills=None,
                commands=None) -> dict:
    lists = default_lists()
    l1 = lists["l1"] if l1 is None else list(l1)
    bundled = lists["bundled"] if bundled is None else dict(bundled)
    project_skills = (lists["project_skills"] if project_skills is None
                      else list(project_skills))
    commands = lists["commands"] if commands is None else list(commands)

    entries = [_entry(root, n, "agent", f"agents/{n}/SKILL.md") for n in l1]
    for name, owner in sorted(bundled.items()):
        entries.append(_entry(root, name, "bundled",
                              f"agents/{owner}/{name}/SKILL.md", host=owner))
    for ps in project_skills:
        entries.append(_entry(root, ps.split("/")[-1], "project",
                              f"agents/{ps}/SKILL.md"))
    for c in commands:
        rel = COMMAND_SOURCE_OVERRIDES.get(
            c, f"agents/a-agentzero/commands/{c}.md")
        entries.append(_entry(root, c, "command", rel))

    # token della lista-fonte: per project skills e' il path nel canone (ps),
    # non il basename — rende il driftActionabile senza indovinare l'owner.
    tokens = ([f"agent:{n}" for n in l1]
              + [f"bundled:{n}" for n in sorted(bundled)]
              + [f"project:{ps}" for ps in project_skills]
              + [f"command:{c}" for c in commands])
    drift = [t for t, e in zip(tokens, entries) if not e["present"]]
    counts = {k: sum(1 for e in entries if e["kind"] == k) for k in KINDS}
    return {
        "schema": 1,
        "metadata": {
            "source": "agents/scripts/hal-contract.py (liste L1/BUNDLED/"
                      "PROJECT_SKILLS/COMMANDS)",
            "note": "present=false = drift del canone: voce listata ma "
                    "sorgente assente; correggere la lista o aggiungere il "
                    "bundle, poi rigenerare",
            "agentzero_version": HC.fm_field(
                root / "agents/a-agentzero/SKILL.md", "version") or "?",
            "counts": counts,
            "drift": drift,
        },
        "entries": entries,
    }


def render(index: dict) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help="radice checkout (default: repo dello script)")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 se l'artefatto on-disk diverge dalla rigenerazione")
    args = ap.parse_args(argv)

    fresh = render(build_index(args.root))
    artifact = args.root / ARTIFACT_RELPATH
    if args.check:
        on_disk = artifact.read_text(encoding="utf-8") if artifact.is_file() else ""
        if on_disk == fresh:
            print(f"OK toth-index ({sum(json.loads(fresh)['metadata']['counts'].values())} voci)")
            return 0
        fl, ol = fresh.split("\n"), on_disk.split("\n")
        first = next((i for i, (a, b) in enumerate(zip(fl, ol)) if a != b),
                     min(len(fl), len(ol)))
        print(f"DRIFT toth-index: riga {first + 1}; rigenerare: python3 "
              f"{args.root / 'agents/a-agentzero/scripts/toth_index.py'}",
              file=sys.stderr)
        return 1
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(fresh, encoding="utf-8")
    meta = json.loads(fresh)["metadata"]
    c = meta["counts"]
    print(f"scritte {sum(c.values())} voci (agent {c['agent']}, "
          f"bundled {c['bundled']}, project {c['project']}, "
          f"command {c['command']}); drift: {len(meta['drift'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
