"""Smoke tests for the packaging and guardrail surface.

These are not placeholders. They assert the two U1 invariants that are easy to
break silently: the package imports under the installed entry point, and
CLAUDE.md is a symlink rather than a copy that can drift from AGENTS.md.
"""

from pathlib import Path

import playbook_doctor

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_package_imports_with_version():
    assert playbook_doctor.__version__


def test_claude_md_is_a_symlink_to_agents_md():
    """A copied CLAUDE.md drifts from AGENTS.md and silently feeds a second
    agent different rules. This repo must not regress into that shape."""
    claude = REPO_ROOT / "CLAUDE.md"
    assert claude.is_symlink(), "CLAUDE.md must be a symlink, not a regular file"
    assert claude.resolve() == (REPO_ROOT / "AGENTS.md").resolve()


def test_agents_md_declares_verification_commands():
    text = (REPO_ROOT / "AGENTS.md").read_text()
    assert "## Verification" in text
    for cmd in ("pytest", "ruff check", "playbook-doctor check"):
        assert cmd in text, f"AGENTS.md must declare `{cmd}` as a verification step"


def test_secrets_baseline_has_no_unaudited_entries():
    import json

    baseline = json.loads((REPO_ROOT / ".secrets.baseline").read_text())
    unaudited = [
        entry
        for findings in baseline.get("results", {}).values()
        for entry in findings
        if entry.get("is_secret") is None
    ]
    assert not unaudited, f"{len(unaudited)} unaudited entries in .secrets.baseline"


def test_stop_hook_is_configured_and_non_empty():
    """An empty `"Stop": []` looks configured and does nothing -- the exact
    failure mode PB-W5-04 exists to catch."""
    import json

    settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text())
    stop = settings.get("hooks", {}).get("Stop", [])
    assert stop, "Stop hook must be configured"
    assert any(h.get("hooks") for h in stop), "Stop hook must contain at least one command"
