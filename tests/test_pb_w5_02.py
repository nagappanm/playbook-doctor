"""PB-W5-02 — format, lint, and secret-scan hooks all present."""

from __future__ import annotations

from playbook_doctor.checks.pb_w5_02 import check
from playbook_doctor.registry import Status

_ALL = """\
repos:
  - repo: local
    hooks:
      - id: black
      - id: ruff
      - id: detect-secrets
"""

_NO_SECRETS = """\
repos:
  - repo: local
    hooks:
      - id: black
      - id: ruff
"""


def _write(tmp_path, text):
    (tmp_path / ".pre-commit-config.yaml").write_text(text)
    return tmp_path


def test_pass_when_all_three_categories_covered(tmp_path):
    assert check(_write(tmp_path, _ALL)).status is Status.PASS


def test_fail_names_the_missing_category(tmp_path):
    verdict = check(_write(tmp_path, _NO_SECRETS))
    assert verdict.status is Status.FAIL
    assert "secrets" in (verdict.detail or "")


def test_fail_when_unparseable(tmp_path):
    verdict = check(_write(tmp_path, "repos: 'unterminated\n"))
    assert verdict.status is Status.FAIL
    assert "unparseable" in (verdict.detail or "")


def test_skip_when_config_absent(tmp_path):
    assert check(tmp_path).status is Status.SKIP
