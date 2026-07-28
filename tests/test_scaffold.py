"""Tests for the init scaffolder and its safety boundary.

The headline test is a dogfood: a directory that has been through ``init`` must
pass the checks that init exists to satisfy. The rest pin the additive-only
contract — skip-existing by default, --force overwrites scaffolded files, and the
CLAUDE.md symlink never clobbers an existing path.
"""

from __future__ import annotations

from playbook_doctor import scaffold
from playbook_doctor.checks import pb_w3_01, pb_w3_02, pb_w3_03, pb_w5_01, pb_w5_02, pb_w5_04
from playbook_doctor.cli import main
from playbook_doctor.registry import Status


def test_init_creates_every_artefact(tmp_path):
    actions = dict((rel, action) for action, rel in scaffold.init(tmp_path))
    assert actions["AGENTS.md"] == "create"
    assert actions[".pre-commit-config.yaml"] == "create"
    assert actions[".claude/settings.json"] == "create"
    assert actions["CLAUDE.md"] == "symlink"
    assert (tmp_path / "CLAUDE.md").is_symlink()


def test_an_initialised_repo_passes_the_checks_it_scaffolds(tmp_path):
    scaffold.init(tmp_path)
    for module in (pb_w3_01, pb_w3_02, pb_w3_03, pb_w5_01, pb_w5_02, pb_w5_04):
        assert module.check(tmp_path).status is Status.PASS, module.__name__


def test_init_skips_existing_files_without_force(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Hand-written, do not clobber\n")
    actions = dict((rel, action) for action, rel in scaffold.init(tmp_path))
    assert actions["AGENTS.md"] == "skip"
    assert "do not clobber" in (tmp_path / "AGENTS.md").read_text()


def test_force_overwrites_scaffolded_files(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# stale\n")
    actions = dict((rel, action) for action, rel in scaffold.init(tmp_path, force=True))
    assert actions["AGENTS.md"] == "overwrite"
    assert "## Verification" in (tmp_path / "AGENTS.md").read_text()


def test_force_never_replaces_an_existing_claude_md(tmp_path):
    # A human's regular CLAUDE.md must survive even --force (spec §6).
    (tmp_path / "CLAUDE.md").write_text("# human wrote this\n")
    actions = dict((rel, action) for action, rel in scaffold.init(tmp_path, force=True))
    assert actions["CLAUDE.md"] == "skip"
    assert not (tmp_path / "CLAUDE.md").is_symlink()
    assert "human wrote this" in (tmp_path / "CLAUDE.md").read_text()


def test_cli_init_exits_zero_and_bad_path_is_usage_error(tmp_path, capsys):
    assert main(["init", str(tmp_path)]) == 0
    assert (tmp_path / "AGENTS.md").is_file()
    assert main(["init", str(tmp_path / "nope")]) == 2
