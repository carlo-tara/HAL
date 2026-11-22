"""test_toth_index.py — guardia dell'indice canonico (slice v0-toth-index).

RED-first 2026-11-22: toth_index.py e il gemello meccanico del catalogo
hal-contract (stesse liste-fonte L1/BUNDLED/PROJECT_SKILLS/COMMANDS da
agents/scripts/hal-contract.py) e stesso parser (fm_field/shorten). Non
aggiunge regole proprie; dove il fence tace sulle fonti mancanti (skipped
di build_fence), l'indice le marca present=false: il drift del canone e il
deliverable di v0, non un effetto collaterale.

Pattern sys.path: tests/test_agent_todo.py.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "agents" / "a-agentzero" / "scripts" / "toth_index.py"


def _load_toth():
    assert SCRIPT.is_file(), f"generatore assente: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("toth_index", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fm(name, *, version="1.0.0", desc="Test.", extends=None):
    lines = ["---", f"name: {name}", f"version: {version}",
             f"description: >-\n  {desc}"]
    if extends:
        lines.append(f"extends: {extends}")
    lines += ["---", "", f"# {name}", ""]
    return "\n".join(lines)


def _fake_root(tmp):
    root = tmp / "wt"
    ag = root / "agents"
    (ag / "a-one").mkdir(parents=True)
    (ag / "a-one" / "SKILL.md").write_text(
        _fm("a-one", extends="a-agentzero", desc="Reason why: test. Agente uno."),
        encoding="utf-8")
    (ag / "a-one" / "sub").mkdir(parents=True)
    (ag / "a-one" / "sub" / "SKILL.md").write_text(
        _fm("sub", desc="Skill embedded in a-one."), encoding="utf-8")
    (ag / "ps" / "proj").mkdir(parents=True)
    (ag / "ps" / "proj" / "SKILL.md").write_text(
        _fm("proj", desc="Skill di progetto."), encoding="utf-8")
    cmds = ag / "a-agentzero" / "commands"
    cmds.mkdir(parents=True)
    (cmds / "one.md").write_text("---\nversion: 0.9.0\n---\n# /one\n",
                                 encoding="utf-8")
    return root


def _lists():
    return dict(l1=["a-one"], bundled={"sub": "a-one"},
                project_skills=["ps/proj", "ps/absent"],
                commands=["one", "missing"])


def test_entries_complete_and_schema(tmp_path):
    toth = _load_toth()
    index = toth.build_index(_fake_root(tmp_path), **_lists())
    assert {e["kind"] for e in index["entries"]} == {
        "agent", "bundled", "project", "command"}
    by = {(e["kind"], e["name"]): e for e in index["entries"]}
    a1 = by[("agent", "a-one")]
    assert a1["present"] is True and a1["host"] is None
    assert a1["parent"] == "a-agentzero"
    assert a1["path"] == "agents/a-one/SKILL.md" and a1["version"] == "1.0.0"
    assert a1["description"] == "Agente uno"  # shorten come nel fence: senza punto
    b = by[("bundled", "sub")]
    assert b["host"] == "a-one" and b["present"] is True
    assert by[("project", "proj")]["present"] is True
    miss = by[("project", "absent")]
    assert miss["present"] is False and miss["version"] is None
    assert by[("command", "one")]["version"] == "0.9.0"
    assert by[("command", "missing")]["present"] is False
    assert index["metadata"]["drift"] == ["project:ps/absent", "command:missing"]
    assert index["metadata"]["counts"] == {"agent": 1, "bundled": 1,
                                           "project": 2, "command": 2}


def test_deterministic_bytes(tmp_path):
    toth = _load_toth()
    root = _fake_root(tmp_path)
    one = toth.render(toth.build_index(root, **_lists()))
    two = toth.render(toth.build_index(root, **_lists()))
    assert one == two and one.endswith("\n")


def test_main_write_check(tmp_path, monkeypatch):
    toth = _load_toth()
    root = _fake_root(tmp_path)
    monkeypatch.setattr(toth, "default_lists", _lists)
    art = root / "agents/a-agentzero/references/toth-index.json"
    assert toth.main(["--root", str(root)]) == 0 and art.is_file()
    assert toth.main(["--root", str(root), "--check"]) == 0
    art.write_text(art.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert toth.main(["--root", str(root), "--check"]) == 1
    assert toth.main(["--root", str(root)]) == 0
    assert toth.main(["--root", str(root), "--check"]) == 0


def test_real_canon_counts():
    toth = _load_toth()
    hc = toth.HC
    index = toth.build_index(toth.REPO_ROOT)
    assert len(index["entries"]) == (len(hc.L1) + len(hc.BUNDLED)
                                     + len(hc.PROJECT_SKILLS) + len(hc.COMMANDS))
    agents = [e for e in index["entries"] if e["kind"] == "agent"]
    assert len(agents) == len(hc.L1) and all(e["present"] for e in agents)
    assert all("a-" in e["name"] for e in agents)


def test_real_artifact_up_to_date():
    toth = _load_toth()
    fresh = toth.render(toth.build_index(toth.REPO_ROOT))
    on_disk = toth.ARTIFACT_PATH.read_text(encoding="utf-8")
    assert fresh == on_disk, "rigenerare: python3 agents/a-agentzero/scripts/toth_index.py"
