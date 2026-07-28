"""PB-W3-02 — AGENTS.md declares verification commands."""

from __future__ import annotations

from playbook_doctor.checks.pb_w3_02 import check
from playbook_doctor.registry import Status

_GOOD = "# Repo\n\n## Verification\n\n```bash\npytest -q\n```\n"


def test_pass_with_heading_and_fenced_block(tmp_path):
    (tmp_path / "AGENTS.md").write_text(_GOOD)
    assert check(tmp_path).status is Status.PASS


def test_fail_when_heading_present_but_no_code_block(tmp_path):
    (tmp_path / "AGENTS.md").write_text("## Testing\n\nRun the tests somehow.\n")
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "fenced" in (verdict.detail or "")


def test_fail_when_code_block_present_but_no_verification_heading(tmp_path):
    (tmp_path / "AGENTS.md").write_text("## Setup\n\n```bash\npip install -e .\n```\n")
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "heading" in (verdict.detail or "")


def test_skip_when_agents_md_absent(tmp_path):
    assert check(tmp_path).status is Status.SKIP
