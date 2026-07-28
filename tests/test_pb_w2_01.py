"""PB-W2-01 — AGENTS.md within context budget."""

from __future__ import annotations

from playbook_doctor.checks.pb_w2_01 import check
from playbook_doctor.registry import Status


def test_pass_at_the_threshold(tmp_path):
    (tmp_path / "AGENTS.md").write_text("\n".join("x" for _ in range(400)))
    assert check(tmp_path).status is Status.PASS


def test_warn_above_the_threshold_reports_the_count(tmp_path):
    (tmp_path / "AGENTS.md").write_text("\n".join("x" for _ in range(401)))
    verdict = check(tmp_path)
    assert verdict.status is Status.WARN
    assert "401" in (verdict.detail or "")


def test_skip_when_absent(tmp_path):
    assert check(tmp_path).status is Status.SKIP
