"""PB-W4-01 — mcp.json parses."""

from __future__ import annotations

from playbook_doctor.checks.pb_w4_01 import check
from playbook_doctor.registry import Status


def test_pass_on_valid_mcp_json(tmp_path):
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {}}')
    assert check(tmp_path).status is Status.PASS


def test_fail_on_malformed_mcp_json(tmp_path):
    (tmp_path / ".mcp.json").write_text('{"mcpServers": ')
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "malformed" in (verdict.detail or "")


def test_skip_when_no_mcp_config(tmp_path):
    assert check(tmp_path).status is Status.SKIP


def test_finds_vscode_config_when_root_absent(tmp_path):
    vscode = tmp_path / ".vscode"
    vscode.mkdir()
    (vscode / "mcp.json").write_text('{"servers": {}}')
    verdict = check(tmp_path)
    assert verdict.status is Status.PASS
    assert ".vscode/mcp.json" in (verdict.detail or "")
