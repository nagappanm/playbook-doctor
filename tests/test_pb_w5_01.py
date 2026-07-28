"""PB-W5-01 — .pre-commit-config.yaml exists."""

from __future__ import annotations

from playbook_doctor.checks.pb_w5_01 import check
from playbook_doctor.registry import Status


def test_pass_when_present(tmp_path):
    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
    assert check(tmp_path).status is Status.PASS


def test_fail_when_absent(tmp_path):
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert verdict.detail
