from __future__ import annotations

import fcntl
import importlib.util
import os
import subprocess
import time
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "agent_todo",
    Path(__file__).resolve().parents[1]
    / "agents"
    / "a-agentzero"
    / "scripts"
    / "agent-todo.py",
)
agent_todo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_todo)

CHANGELOG = """# Changelog

## [Unreleased]

### Fixed

- Già presente.

## [1.0.0] - 2026-01-01

### Added

- Prima release.
"""


def run(tmp_path, todo):
    (tmp_path / "ToDo.md").write_text(todo, encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    code = agent_todo.flush(tmp_path)
    return (
        code,
        (tmp_path / "ToDo.md").read_text(encoding="utf-8"),
        (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8"),
    )


def test_checked_item_is_removed_with_children_and_mapped_by_tag(tmp_path):
    todo = (
        "## P1\n\n"
        "- [ ] Aperta `#infra` · P1\n"
        "  - Perché utile: resta.\n"
        "- [x] Correggere il merge `#bug` · P1\n"
        "  - Perché utile: sparisce con il titolo.\n"
        "  - Esito: guardia su `--output`.\n"
        "- [ ] Altra aperta `#spike` · P2\n"
        "  - Acceptance: resta.\n"
    )
    code, new_todo, log = run(tmp_path, todo)
    assert code == 0
    assert "sparisce" not in new_todo and "Correggere" not in new_todo
    assert "Perché utile: resta." in new_todo and "Acceptance: resta." in new_todo
    assert "- Correggere il merge — guardia su `--output`." in log
    assert log.index("### Fixed") < log.index("Correggere") < log.index("## [1.0.0]")
    assert "#bug" not in log and "· P1" not in log


def test_done_section_headings_set_kac_section_and_buffer_is_emptied(tmp_path):
    todo = (
        "## P1\n\n- [ ] Aperta `#infra` · P1\n\n"
        "## Già fatto\n\n### Added\n\n- Nuova opzione `--x`.\n\n### Removed\n\n- Vecchio flag.\n"
    )
    code, new_todo, log = run(tmp_path, todo)
    assert code == 0
    assert "Nuova opzione" not in new_todo
    assert not [ln for ln in new_todo.split("\n") if ln.startswith("### ")]
    assert "## Già fatto" in new_todo
    assert log.index("### Added") < log.index("### Removed") < log.index("### Fixed")
    assert "- Nuova opzione `--x`." in log and "- Vecchio flag." in log


def test_flush_is_idempotent_and_deduplicates(tmp_path):
    todo = "## P1\n\n- [x] Già presente. `#bug` · P1\n"
    run(tmp_path, todo)
    (tmp_path / "ToDo.md").write_text(todo, encoding="utf-8")
    code = agent_todo.flush(tmp_path)
    log = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert code == 0
    assert log.count("Già presente.") == 1


def _git(repo, *args):
    subprocess.run(
        ("git", *args),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_EMAIL": "t@t",
        },
    )


def _repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "master")
    (tmp_path / "ToDo.md").write_text(
        "## P1\n\n- [x] Voce da consolidare `#infra` · P1\n  - Esito: ok.\n",
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


def test_flush_refuses_on_slice_branch_and_force_overrides(tmp_path):
    """Regola di consolidamento: su slice le [x] restano nel ToDo; il flush è di master."""
    repo = _repo(tmp_path)
    _git(repo, "checkout", "-q", "-b", "slice/t104")
    assert agent_todo.flush(repo) != 0
    assert "- [x]" in (repo / "ToDo.md").read_text(encoding="utf-8")
    assert "consolidare" not in (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert agent_todo.flush(repo, force=True) == 0
    assert "- [x]" not in (repo / "ToDo.md").read_text(encoding="utf-8")


def test_flush_serializes_on_agent_commit_lock(tmp_path):
    """Stesso flock cooperativo di agent-commit.sh/land: mai due scritture concorrenti."""
    repo = _repo(tmp_path)
    holder = open(repo / ".git" / "agent-commit.lock", "a+")
    fcntl.flock(holder, fcntl.LOCK_EX)
    try:
        assert agent_todo.flush(repo, lock_wait_s=0.2) != 0
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()
    assert agent_todo.flush(repo, lock_wait_s=2) == 0


def test_flush_still_works_outside_git(tmp_path):
    """Degrado grazioso: senza repo (guardia e lock saltati) il flush è quello storico."""
    code, _, log = run(tmp_path, "## P1\n\n- [x] Fuori repo `#infra` · P1\n")
    assert code == 0
    assert "Fuori repo" in log
