"""PB-W3-01 — AGENTS.md exists.

Fixtures are built at runtime in ``tmp_path`` rather than committed: it keeps
each check's pass/fail subjects local to its test and avoids planting stray
files in the repo the audit runs against.
"""

from __future__ import annotations

from playbook_doctor.checks.pb_w3_01 import check
from playbook_doctor.registry import Status


def test_pass_when_agents_md_present(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Agents\n")
    assert check(tmp_path).status is Status.PASS


def test_fail_when_agents_md_absent(tmp_path):
    (tmp_path / "README.md").write_text("# Just a readme\n")
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert verdict.detail


def test_a_directory_named_agents_md_does_not_count(tmp_path):
    (tmp_path / "AGENTS.md").mkdir()
    assert check(tmp_path).status is Status.FAIL
