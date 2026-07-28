"""Tests for `check --fix` — additive repairs only (spec §6).

Two things must hold no matter what: --fix only ever *creates* absent artefacts,
and it refuses — loudly, without changing anything — every repair that would edit
or replace a human's file. The exit code always reflects the re-audit, so a
refusal leaves a real FAIL in place.
"""

from __future__ import annotations

import json

from playbook_doctor import scaffold
from playbook_doctor.cli import main
from playbook_doctor.registry import Status, Verdict, load_checks, run_all


def _flagged(root):
    load_checks()
    return run_all(root)


def test_fix_repairs_a_bare_repo_to_zero_fail(tmp_path, capsys):
    code = main(["check", str(tmp_path), "--fix"])
    out = capsys.readouterr().out
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / ".pre-commit-config.yaml").is_file()
    assert (tmp_path / ".claude" / "settings.json").is_file()
    assert (tmp_path / "CLAUDE.md").is_symlink()
    assert "created" in out and "symlinked" in out
    assert code == 0  # every FAIL was additively repairable


def test_fix_refuses_to_replace_a_regular_claude_md(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Agents\n")
    (tmp_path / "CLAUDE.md").write_text("# human wrote this\n")
    outcomes = scaffold.fix(tmp_path, _flagged(tmp_path))
    assert any(o == "refused" and d.startswith("CLAUDE.md: exists") for o, d in outcomes)
    assert not (tmp_path / "CLAUDE.md").is_symlink()
    assert "human wrote this" in (tmp_path / "CLAUDE.md").read_text()


def test_fix_refuses_to_edit_an_existing_agents_md(tmp_path):
    # AGENTS.md exists but lacks a verification section -> PB-W3-02 FAILs. Fixing
    # that means editing content, which --fix must refuse, not overwrite.
    (tmp_path / "AGENTS.md").write_text("# Agents\n\nNo verification here.\n")
    outcomes = scaffold.fix(tmp_path, _flagged(tmp_path))
    assert any(o == "refused" and "PB-W3-02" in d for o, d in outcomes)
    assert "No verification here." in (tmp_path / "AGENTS.md").read_text()


def test_fix_refuses_baseline_and_loop_edits(tmp_path):
    verdicts = [
        Verdict("PB-W5-03", "W5", "t", Status.FAIL, "2 unaudited"),
        Verdict("PB-M9-01", "M9", "t", Status.FAIL, "no cap"),
        Verdict("PB-M9-02", "M9", "t", Status.WARN, "unclear"),
    ]
    outcomes = scaffold.fix(tmp_path, verdicts)
    reasons = [d for o, d in outcomes if o == "refused"]
    assert any(".secrets.baseline" in r for r in reasons)
    # The loop refusal is emitted once even though two M9 checks flagged.
    assert sum("loop script" in r for r in reasons) == 1


def test_a_refusal_leaves_the_exit_code_failing(tmp_path, capsys):
    # The only defect is a regular-file CLAUDE.md; --fix refuses, so PB-W3-03
    # stays FAIL and the re-audit still exits 1.
    (tmp_path / "AGENTS.md").write_text("# Agents\n\n## Verification\n\n```bash\npytest\n```\n")
    (tmp_path / "CLAUDE.md").write_text("# copy\n")
    code = main(["check", str(tmp_path), "--fix"])
    assert code == 1
    assert not (tmp_path / "CLAUDE.md").is_symlink()


def test_fix_json_keeps_stdout_pure(tmp_path, capsys):
    main(["check", str(tmp_path), "--fix", "--json"])
    captured = capsys.readouterr()
    json.loads(captured.out)  # stdout is only JSON
    assert "repairs:" in captured.err  # the repair log went to stderr
