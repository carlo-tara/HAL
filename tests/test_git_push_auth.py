"""Anti-hang delle push non interattive (git-push-auth.sh, L0).

Evidenza 2026-11-18: il land si bloccò su `Username for 'https://github.com'`
(credenziale non valida, terminal prompt attivo). Evidenza 2026-11-22 (HT-019):
`gh auth refresh -s api` fallisce con error 403 su account free con 2FA — manca
un tier SSH non interattivo.

Stile unittest.TestCase: eseguito sia da `python3 -m unittest tests.test_git_push_auth`
(recipe Makefile `test-unit` e CI) sia da pytest.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "agents" / "scripts" / "git-push-auth.sh"
ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def _bash(snippet: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-c", f'source "{LIB}"\n{snippet}'],
        capture_output=True,
        text=True,
        env=ENV,
    )


def _mk_repo(tmp: str) -> str:
    """Bare remote locale + worktree clone con un commit pronto da spingere."""
    origin = str(Path(tmp) / "origin.git")
    work = Path(tmp) / "work"
    subprocess.run(
        ["git", "init", "--bare", "-b", "master", origin],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "clone", origin, str(work)], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=work, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=work, check=True)
    (work / "f.txt").write_text("x")
    subprocess.run(["git", "add", "f.txt"], cwd=work, check=True)
    subprocess.run(
        ["git", "commit", "-m", "c"], cwd=work, check=True, capture_output=True
    )
    return origin


class TestHttpsToSshUrl(unittest.TestCase):
    def test_converts_https_to_ssh(self):
        out = _bash(
            'printf "%s" "$(https_to_ssh_url "https://github.com/foo/bar.git")"'
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout, "git@github.com:foo/bar.git")

    def test_non_https_returned_unchanged(self):
        out = _bash('printf "%s" "$(https_to_ssh_url "git@github.com:foo/bar.git")"')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout, "git@github.com:foo/bar.git")


class TestPushWithSshFallback(unittest.TestCase):
    def test_falls_back_after_https_failure(self):
        # host https irraggiungibile → il tier SSH deve essere innescato e
        # fallire a sua volta (nessun host ssh valido): exit != 0, riga fallback presente
        out = _bash('push_with_ssh_fallback "https://github.invalid/r.git" master 2>&1')
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("auth fallback", out.stdout)
        self.assertIn("git@github.invalid:r.git", out.stdout)

    def test_success_and_no_rewrite_for_non_https(self):
        with tempfile.TemporaryDirectory() as tmp:
            origin = _mk_repo(tmp)
            out = _bash(
                f'cd "{tmp}/work" && push_with_ssh_fallback "{origin}" master 2>&1'
            )
            self.assertEqual(out.returncode, 0, out.stdout)
            self.assertNotIn("auth fallback", out.stdout)
            ls = subprocess.run(
                ["git", "ls-remote", origin, "refs/heads/master"],
                capture_output=True,
                text=True,
                env=ENV,
            )
            head = subprocess.run(
                ["git", "rev-parse", "master"],
                cwd=f"{tmp}/work",
                capture_output=True,
                text=True,
            )
            self.assertIn(head.stdout.strip(), ls.stdout)


if __name__ == "__main__":
    unittest.main()
