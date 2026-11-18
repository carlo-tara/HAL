"""Anti-hang delle push non interattive (git-push-auth.sh, L0).

Evidenza 2026-11-18: il land si bloccò su `Username for 'https://github.com'`
(helper di credenziali scaduto a metà sessione, terminale interattivo = hold
infinito). Canone: mai far sparire un land in un prompt — fallimento rapido
(GIT_TERMINAL_PROMPT=0) + fallback helper gh quando gh è autenticato.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "agents" / "scripts" / "git-push-auth.sh"
SCRIPTS = (
    ROOT / "agents" / "scripts" / "agent-worktree.sh",
    ROOT / "agents" / "a-agentzero" / "scripts" / "agent-commit.sh",
)

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def bash(code, cwd=None, timeout=60):
    return subprocess.run(
        ["bash", "-c", code],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        env=GIT_ENV,
        timeout=timeout,
    )


def test_lib_exists_and_land_commit_source_it():
    assert LIB.is_file(), "git-push-auth.sh assente"
    for s in SCRIPTS:
        t = s.read_text(encoding="utf-8")
        assert "git-push-auth.sh" in t, f"{s.name}: manca il source della lib"
        assert "push_with_gh_fallback" in t, f"{s.name}: push non avvolta"


def test_classifier_auth_vs_structural(tmp_path):
    code = (
        f'source "{LIB}" || exit 9;'
        f'printf %s "fatal: could not read Username for \'https://github.com\'"'
        f" > {tmp_path}/a; printf %s '! [rejected] master -> master (non-fast-forward)'"
        f" > {tmp_path}/b;"
        f"git_auth_failure {tmp_path}/a; ok1=$?;"
        f"git_auth_failure {tmp_path}/b; ok2=$?;"
        'test $ok1 -eq 0 -a $ok2 -ne 0'
    )
    r = bash(code)
    assert r.returncode == 0, r.stderr


def test_push_fails_fast_never_hangs(tmp_path):
    """Remote https irraggiungibile: la lib deve restituire in pochi secondi
    (mai attendere un prompt), con messaggio git-push-auth e rc≠0."""
    repo = tmp_path / "r"
    repo.mkdir()
    (repo / "f").write_text("x\n")
    bash("git init -q -b master . && git add -A && git commit -q -m base", cwd=repo)
    code = (
        f'source "{LIB}" || exit 9;'
        f"git -C {repo} remote add origin https://github.invalid/r.git;"
        f"push_with_gh_fallback --git-dir={repo}/.git --work-tree={repo} origin master"
    )
    r = bash(code, timeout=60)  # un hang solleva TimeoutExpired → test rosso
    assert r.returncode != 0
    assert "git-push-auth" in (r.stderr + r.stdout), r.stderr[-400:]
