"""Smoke del protocollo worktree (regola `.wt-extra`): `new` deve rendere
disponibili i file untracked necessari ai gate del repo (es. `.env`), che il
checkout del worktree non contiene. Evidenza: hal_system2 2026-11-18, test e
deploy dal worktree senza `.env`.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agents" / "scripts" / "agent-worktree.sh"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def _git(cwd, *args):
    subprocess.run(
        ("git", *args),
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )


def _scratch(tmp_path, with_extra):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-q", str(origin))
    main = tmp_path / "app"
    main.mkdir()
    _git(main, "init", "-q", "-b", "master")
    (main / ".gitignore").write_text(".env\n", encoding="utf-8")
    (main / "README.md").write_text("scratch\n", encoding="utf-8")
    if with_extra:
        (main / ".wt-extra").write_text(
            "# file untracked da symlinkare nei worktree\n.env\n",
            encoding="utf-8",
        )
    (main / ".env").write_text("SECRET=1\n", encoding="utf-8")  # ignored, mai committato
    _git(main, "add", "-A")
    _git(main, "commit", "-q", "-m", "base")
    _git(main, "push", "-q", str(origin), "master")
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", str(origin), str(clone))
    # l'ambiente del checkout principale: i file untracked (es. .env) vivono qui,
    # non nel seed — è da MAIN (il checkout chiamante) che il worktree li symlinka.
    (clone / ".env").write_text("SECRET=1\n", encoding="utf-8")
    return main, clone


def _new(clone, name):
    r = subprocess.run(
        ("bash", str(SCRIPT), "new", name),
        cwd=str(clone),
        check=True,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )
    for ln in r.stdout.splitlines():
        if ln.startswith("worktree: "):
            return Path(ln.split("worktree: ", 1)[1].strip())
    raise AssertionError(f"stdout privo di worktree: {r.stdout!r}")


def test_new_symlinks_wt_extra_files(tmp_path):
    main, clone = _scratch(tmp_path, with_extra=True)
    wt = _new(clone, "s1")
    assert (wt / ".tmp").is_dir()
    link = wt / ".env"
    assert link.is_symlink()
    assert link.resolve() == (clone / ".env").resolve()
    assert link.read_text(encoding="utf-8") == "SECRET=1\n"
    assert (wt / "README.md").is_file()  # il checkout normale non è toccato


def test_new_without_wt_extra_is_not_broken(tmp_path):
    _, clone = _scratch(tmp_path, with_extra=False)
    wt = _new(clone, "s2")
    assert wt.is_dir()
    assert not (wt / ".env").exists()


def test_wt_extra_missing_source_skipped_with_warning(tmp_path):
    _, clone = _scratch(tmp_path, with_extra=True)
    (clone / ".wt-extra").write_text(
        ".env\nno-absente.txt\n", encoding="utf-8"
    )  # dichiarazione nel MAIN chiamante: la riga buona vale, la mancante degrada
    wt = _new(clone, "s3")
    assert (wt / ".env").is_symlink()
    assert not (wt / "no-absente.txt").exists()
