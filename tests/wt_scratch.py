"""Factory di repo scratch per i test del protocollo worktree/flush.

Motivazione (hal_system2 2026-11-18): ogni nuovo test di protocollo reinventava
il plumbing git (origin bare, seed pushato, clone, untracked d'ambiente,
symlink di registry) con bug ricorrenti — remote mancante → push 128, symlink
non tracciata → falso negativo. Qui il plumbing è uno; i test restano asserzioni.

`make_scratch` costruisce dentro tmp_path (zero contatto con gli ambienti reali):
  origin.git   bare remoto
  app/         seed committato e pushato (README + opz. .wt-extra + opz. symlink
               `agents` → shared-registry con .tools/shellcheck eseguibile)
  clone/       clone di origin con gli untracked d'ambiente (.env…): è il MAIN
               da cui lanciare `new_slice` (scenario consumer reale)
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

WORKTREE_SCRIPT = (
    Path(__file__).resolve().parents[1] / "agents" / "scripts" / "agent-worktree.sh"
)

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def git(cwd, *args: str) -> None:
    subprocess.run(
        ("git", *args),
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )


def git_out(cwd, *args: str) -> str:
    r = subprocess.run(
        ("git", *args),
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )
    return r.stdout.strip()


@dataclass
class Scratch:
    origin: Path
    main: Path
    clone: Path
    ext: Path | None = None


def make_scratch(
    tmp_path,
    *,
    wt_extra: bool = False,
    registry_symlink: bool = False,
    untracked: tuple[str, ...] = (".env",),
) -> Scratch:
    tmp = Path(tmp_path)
    origin = tmp / "origin.git"
    git(tmp, "init", "--bare", "-q", str(origin))

    main = tmp / "app"
    main.mkdir()
    git(main, "init", "-q", "-b", "master")
    (main / ".gitignore").write_text("\n".join(untracked) + "\n", encoding="utf-8")
    (main / "README.md").write_text("scratch\n", encoding="utf-8")

    ext = None
    if registry_symlink:
        # caso consumer: `agents` symlink TRACCIATA verso registry condivisa,
        # con .tools/shellcheck eseguibile (il percorso è lo stesso inode in
        # main e worktree — cp same-file sotto set -e)
        ext = tmp / "shared-registry"
        (ext / ".tools").mkdir(parents=True)
        sc = ext / ".tools" / "shellcheck"
        sc.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        os.chmod(sc, 0o755)
        (main / "agents").symlink_to(ext, target_is_directory=True)
    if wt_extra:
        (main / ".wt-extra").write_text(
            "# file untracked da symlinkare nei worktree\n"
            + "\n".join(untracked)
            + "\n",
            encoding="utf-8",
        )

    git(main, "add", "-A")
    git(main, "commit", "-q", "-m", "base")
    git(main, "push", "-q", str(origin), "master")

    clone = tmp / "clone"
    git(tmp, "clone", "-q", str(origin), str(clone))
    for name in untracked:
        if name == ".env":
            (clone / ".env").write_text("SECRET=1\n", encoding="utf-8")
        else:
            (clone / name).write_text(f"{name}=1\n", encoding="utf-8")
    return Scratch(origin=origin, main=main, clone=clone, ext=ext)


def new_slice(clone, name: str) -> Path:
    """Esegue il vero `agent-worktree.sh new <name>` dal clone; resa il wt path."""
    r = subprocess.run(
        ("bash", str(WORKTREE_SCRIPT), "new", name),
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
