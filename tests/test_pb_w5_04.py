"""PB-W5-04 — Stop hook configured and non-empty."""

from __future__ import annotations

import json

from playbook_doctor.checks.pb_w5_04 import check
from playbook_doctor.registry import Status


def _settings(tmp_path, stop, name="settings.json"):
    claude = tmp_path / ".claude"
    claude.mkdir(exist_ok=True)
    (claude / name).write_text(json.dumps({"hooks": {"Stop": stop}}))
    return tmp_path


def test_pass_when_an_entry_carries_a_command(tmp_path):
    stop = [{"hooks": [{"type": "command", "command": "pytest -q"}]}]
    assert check(_settings(tmp_path, stop)).status is Status.PASS


def test_warn_when_empty_array_is_called_out(tmp_path):
    verdict = check(_settings(tmp_path, []))
    assert verdict.status is Status.WARN
    assert "empty" in (verdict.detail or "")


def test_warn_when_declared_but_runs_nothing(tmp_path):
    verdict = check(_settings(tmp_path, [{"hooks": []}]))
    assert verdict.status is Status.WARN
    assert "runs no command" in (verdict.detail or "")


def test_warn_when_no_stop_key(tmp_path):
    claude = tmp_path / ".claude"
    claude.mkdir()
    (claude / "settings.json").write_text(json.dumps({"hooks": {}}))
    assert check(tmp_path).status is Status.WARN


def test_local_settings_can_satisfy_the_check(tmp_path):
    stop = [{"hooks": [{"type": "command", "command": "make test"}]}]
    assert check(_settings(tmp_path, stop, name="settings.local.json")).status is Status.PASS
