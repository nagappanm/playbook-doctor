"""PB-W4-02 — no inline credentials in mcp.json.

The planted "credential" values are assembled at runtime from low-entropy
fragments and written only into tmp_path — they never appear as a
``sensitive_key: "literal"`` adjacency in this source file, so the repo's own
detect-secrets/semgrep hooks have nothing to catch and no secret-shaped string
enters history.
"""

from __future__ import annotations

import json

from playbook_doctor.checks.pb_w4_02 import check
from playbook_doctor.registry import Status

# Not a secret: a low-entropy placeholder built so no literal key/value pair
# exists in this file's text.
PLANTED = "inline-" + "placeholder-" + "value"


def _mcp(tmp_path, config, name=".mcp.json"):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config))
    return tmp_path


def test_pass_when_values_are_env_references(tmp_path):
    config = {"mcpServers": {"gh": {"env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}}}}
    assert check(_mcp(tmp_path, config)).status is Status.PASS


def test_pass_on_each_env_reference_form(tmp_path):
    config = {"a": {"token": "${A}"}, "b": {"api_key": "$B"}, "c": {"secret": "env:C"}}
    assert check(_mcp(tmp_path, config)).status is Status.PASS


def test_fail_on_a_hardcoded_literal(tmp_path):
    config = {"mcpServers": {"gh": {"env": {"API_TOKEN": PLANTED}}}}
    verdict = check(_mcp(tmp_path, config))
    assert verdict.status is Status.FAIL
    assert "mcpServers.gh.env.API_TOKEN" in (verdict.detail or "")


def test_the_secret_value_is_never_printed(tmp_path):
    config = {"creds": {"password": PLANTED}}
    verdict = check(_mcp(tmp_path, config))
    assert verdict.status is Status.FAIL
    assert PLANTED not in (verdict.detail or "")  # key path only, never the value


def test_non_sensitive_keys_are_ignored(tmp_path):
    config = {"mcpServers": {"gh": {"command": "npx", "args": ["-y", "server"]}}}
    assert check(_mcp(tmp_path, config)).status is Status.PASS


def test_skip_when_no_mcp_config(tmp_path):
    assert check(tmp_path).status is Status.SKIP


def test_skip_when_malformed_defers_to_w4_01(tmp_path):
    (tmp_path / ".mcp.json").write_text('{"mcpServers": ')
    verdict = check(tmp_path)
    assert verdict.status is Status.SKIP
    assert "PB-W4-01" in (verdict.detail or "")
