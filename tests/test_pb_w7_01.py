"""PB-W7-01 — token or cost ceiling declared."""

from __future__ import annotations

import json

from playbook_doctor.checks.pb_w7_01 import check
from playbook_doctor.registry import Status


def _settings(tmp_path, env):
    claude = tmp_path / ".claude"
    claude.mkdir(exist_ok=True)
    (claude / "settings.json").write_text(json.dumps({"env": env}))


def test_pass_via_env_key(tmp_path):
    _settings(tmp_path, {"MAX_OUTPUT_TOKENS": "4096"})
    assert check(tmp_path).status is Status.PASS


def test_pass_via_agents_md_line(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Repo\n\nHard token ceiling: 200k per run.\n")
    assert check(tmp_path).status is Status.PASS


def test_warn_when_nothing_declared(tmp_path):
    _settings(tmp_path, {"PATH": "/usr/bin"})
    (tmp_path / "AGENTS.md").write_text("# Repo\n\nNothing about limits.\n")
    assert check(tmp_path).status is Status.WARN


def test_warn_on_a_bare_repo(tmp_path):
    assert check(tmp_path).status is Status.WARN
