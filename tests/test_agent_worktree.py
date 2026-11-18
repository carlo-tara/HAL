"""Smoke del protocollo worktree sul builder riusabile `wt_scratch`.

I test sono asserzioni sul comportamento di `agent-worktree.sh new` (.wt-extra,
registry symlinkata dei consumer, assenza file); il plumbing git vive in
`wt_scratch.make_scratch` (strategia 4: ~5 chiamate/turno di reinvenzione del
fixture evitate — evidenza hal_system2 2026-11-18: remote mancante → push 128,
symlink non tracciata → falso negativo).
"""

from __future__ import annotations

from pathlib import Path

from wt_scratch import git_out, make_scratch, new_slice


def test_scratch_builder_provides_clone_origin_env_and_extra(tmp_path):
    """Il builder costruisce: origin bare, clone con untracked, .wt-extra."""
    s = make_scratch(tmp_path, wt_extra=True)
    assert (s.clone / "README.md").is_file()
    assert (s.clone / ".env").read_text(encoding="utf-8") == "SECRET=1\n"
    assert (s.origin / "HEAD").is_file()
    assert git_out(s.clone, "remote", "get-url", "origin") == str(s.origin)
    assert (s.clone / ".wt-extra").read_text(encoding="utf-8").endswith(".env\n")


def test_scratch_builder_registry_symlink_tracked(tmp_path):
    """Variante consumer: `agents` è symlink TRACCIATA verso registry condivisa."""
    s = make_scratch(tmp_path, registry_symlink=True)
    assert s.ext is not None
    assert (s.clone / "agents").is_symlink()
    assert (s.clone / "agents").resolve() == s.ext.resolve()
    assert (s.ext / ".tools/shellcheck").is_file()


def test_new_symlinks_wt_extra_files(tmp_path):
    s = make_scratch(tmp_path, wt_extra=True)
    wt = new_slice(s.clone, "s1")
    assert (wt / ".tmp").is_dir()
    link = wt / ".env"
    assert link.is_symlink()
    assert link.resolve() == (s.clone / ".env").resolve()
    assert (wt / "README.md").is_file()


def test_new_without_wt_extra_is_not_broken(tmp_path):
    s = make_scratch(tmp_path)
    wt = new_slice(s.clone, "s2")
    assert wt.is_dir()
    assert not (wt / ".env").exists()


def test_wt_extra_missing_source_skipped_with_warning(tmp_path):
    s = make_scratch(tmp_path, wt_extra=True)
    (s.clone / ".wt-extra").write_text(
        ".env\nno-absente.txt\n", encoding="utf-8"
    )  # dichiarazione nel MAIN chiamante: la riga buona vale, la mancante degrada
    wt = new_slice(s.clone, "s3")
    assert (wt / ".env").is_symlink()
    assert not (wt / "no-absente.txt").exists()


def test_new_survives_registry_symlinked_to_main(tmp_path):
    """Consumer con registry via symlink tracciata: cp same-file non aborta new."""
    s = make_scratch(tmp_path, registry_symlink=True)
    wt = new_slice(s.clone, "s4")
    assert wt.is_dir()
    assert (wt / "agents").resolve() == s.ext.resolve()
    assert (wt / "README.md").is_file()
