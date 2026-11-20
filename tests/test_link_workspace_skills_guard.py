"""Guardia anti-collisione di `link-workspace-skills.sh` (de-racing step 1).

Un consumer che monta l'albero fisico di hal_gateway deve essere rifiutato
PRIMA di qualunque scrittura nel tree condiviso: nessuna rigenerazione da
progetti diversi dal canonico. Copre le tre topologie osservate sul campo
(symlink totale di `.agents`, wrapper-skill in fuga, symlink rotto) oltre al
caso verde del workspace canonico e al consumer con `.agents`/`.zed` locali.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agents/scripts/link-workspace-skills.sh"

AGENTS = [
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
]


def make_canonical(root: Path) -> Path:
    """Finto hal_gateway con il minimo perché il link script giri per intero."""
    agents = root / "agents"
    (agents / "scripts").mkdir(parents=True)
    shutil.copy(SCRIPT, agents / "scripts" / "link-workspace-skills.sh")
    for name in AGENTS:
        (agents / name / "agents").mkdir(parents=True)
        (agents / name / "SKILL.md").write_text(
            f"---\nname: {name}\nversion: 0.0.1\n---\n", encoding="utf-8"
        )
        (agents / name / "agents" / f"{name}.md").write_text(
            "# agent\n", encoding="utf-8"
        )
    commands = agents / "a-agentzero" / "commands"
    commands.mkdir(parents=True)
    for cmd in COMMANDS:
        (commands / f"{cmd}.md").write_text(
            f"---\nversion: 0.1.0\n---\n\n# {cmd}\n", encoding="utf-8"
        )
    for skill in ("learn", "sync"):
        (agents / "a-agentzero" / skill).mkdir()
    (agents / "gdrive-sync-safe").mkdir()
    (agents / "a-b2b" / "enrichment").mkdir()
    for skill in ("personas", "jtbd", "gherkin"):
        (agents / "a-product" / skill).mkdir()
    for skill in ("charts", "illustrator", "uiux"):
        (agents / "a-design" / skill).mkdir()
    (agents / "project-skills" / "harness-agentfactory").mkdir(parents=True)
    (agents / "project-skills" / "laya").mkdir(parents=True)
    (root / ".agents").mkdir()
    return root


def run_link(workspace_root: Path) -> subprocess.CompletedProcess[str]:
    cmd = f'cd "{workspace_root}" && bash agents/scripts/link-workspace-skills.sh'
    return subprocess.run(
        ["bash", "-c", cmd], capture_output=True, text=True, check=False
    )


def test_canonical_workspace_links_everything(tmp_path):
    hal = make_canonical(tmp_path / "hal")

    result = run_link(hal)

    assert result.returncode == 0, result.stderr
    assert (hal / ".agents/skills/a-b2b").is_symlink()
    assert (hal / ".agents/commands/commit.md").is_symlink()
    assert (hal / ".zed/prompts/commit.md").is_file()
    # Sede unica delle skill-comando: globale. Nessun wrapper locale generato.
    assert not (hal / ".agents/skills/commit").exists()
    assert (hal / "product/adapters/agents/a-b2b.md").is_symlink()
    # Il branch laya.md è opzionale: assente nei sorgenti, assente il wrapper.
    assert not (hal / ".agents/skills/laya-cmd").exists()


def test_stale_local_wrappers_are_pruned(tmp_path):
    """Mirror di epoca link_zed_skill (marker nel description) vengono potati;
    una directory reale che NON è wrapper (override di progetto) resta."""
    hal = make_canonical(tmp_path / "hal")
    stale = hal / ".agents/skills/commit"
    stale.mkdir(parents=True)
    (stale / "SKILL.md").write_text(
        "---\nname: commit\nversion: 0.1.0\n"
        "description: Command commit for HAL workspace.\n---\n\n# stale\n",
        encoding="utf-8",
    )
    kept = hal / ".agents/skills/graph"
    kept.mkdir()
    (kept / "SKILL.md").write_text(
        "---\nname: graph\nversion: 9.9.9\n"
        "description: Override di progetto, non un wrapper.\n---\n\n# keep\n",
        encoding="utf-8",
    )

    result = run_link(hal)

    assert result.returncode == 0, result.stderr
    assert not stale.exists()
    assert (kept / "SKILL.md").is_file()


def test_symlinked_wrapper_dir_is_never_pruned_through(tmp_path):
    """Un vecchio wrapper SYMLINKATO non si pota through-link: il bersaglio
    (fuori workspace) resta intatto."""
    hal = make_canonical(tmp_path / "hal")
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    target = outside / "commit"
    target.mkdir()
    (target / "SKILL.md").write_text(
        "---\nname: commit\nversion: 0.1.0\n"
        "description: Command commit for HAL workspace.\n---\n",
        encoding="utf-8",
    )
    consumer = tmp_path / "consumer"
    (consumer / ".agents/skills").mkdir(parents=True)
    (consumer / "agents").symlink_to(hal / "agents")
    (consumer / ".agents/skills/commit").symlink_to(target)

    result = run_link(consumer)

    assert result.returncode == 0, result.stderr
    assert (consumer / ".agents/skills/commit").is_symlink()
    assert (target / "SKILL.md").is_file()


def test_full_symlink_consumer_refused_before_any_write(tmp_path):
    """Topologia hal_system2/hal_mcp_*: `.agents` e `.zed` symlink a gateway."""
    hal = make_canonical(tmp_path / "hal")
    sentinel = hal / ".agents/skills/harness-x"
    sentinel.mkdir(parents=True)
    (sentinel / "marker.txt").write_text("hal\n", encoding="utf-8")
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    (consumer / "agents").symlink_to(hal / "agents")
    (consumer / ".agents").symlink_to(hal / ".agents")

    result = run_link(consumer)

    assert result.returncode != 0
    assert "Guardia HAL" in result.stderr
    # Il tree canonico non ha ricevuto una singola scrittura.
    assert (sentinel / "marker.txt").read_text(encoding="utf-8") == "hal\n"
    assert not (hal / ".zed").exists()
    assert not (hal / ".agents/commands").exists()
    assert not (hal / "product").exists()


def test_escaped_wrapper_skill_symlink_left_untouched(tmp_path):
    """Topologia brainbeez/WTP: `.agents` reale, ma la skill wrapper è symlink a gateway."""
    hal = make_canonical(tmp_path / "hal")
    assert run_link(hal).returncode == 0
    wrapper_skill = hal / ".agents/skills/graph"
    wrapper_skill.mkdir(parents=True)
    wrapper_marker = "# keep-me\n"
    (wrapper_skill / "SKILL.md").write_text(wrapper_marker, encoding="utf-8")

    consumer = tmp_path / "consumer"
    (consumer / ".agents/skills").mkdir(parents=True)
    (consumer / "agents").symlink_to(hal / "agents")
    (consumer / ".agents/skills/graph").symlink_to(wrapper_skill)

    result = run_link(consumer)

    assert result.returncode == 0, result.stderr
    # Nessuna scrittura/pruning through-symlink: il bersaglio in hal è intatto.
    assert (wrapper_skill / "SKILL.md").read_text(encoding="utf-8") == wrapper_marker


def test_broken_symlink_root_refused(tmp_path):
    """Symlink `.agents` verso target inesistente: irraggiungibile, rifiutato."""
    hal = make_canonical(tmp_path / "hal")
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    (consumer / "agents").symlink_to(hal / "agents")
    (consumer / ".agents").symlink_to(tmp_path / "fantasma")

    result = run_link(consumer)

    assert result.returncode != 0
    assert "Guardia HAL" in result.stderr


def test_consumer_with_local_destination_roots_writes_locally(tmp_path):
    """`.agents` e `.zed` reali (topologia hal_system1 pre-contratto): via, scrive in locale."""
    hal = make_canonical(tmp_path / "hal")
    consumer = tmp_path / "consumer"
    (consumer / ".agents").mkdir(parents=True)
    (consumer / "agents").symlink_to(hal / "agents")

    result = run_link(consumer)

    assert result.returncode == 0, result.stderr
    assert (consumer / ".agents/skills/a-b2b").is_symlink()
    # Il canonico non viene toccato: nessun mirror generato dentro hal.
    assert not (hal / ".agents/skills/a-b2b").exists()
    assert not (hal / ".zed").exists()
