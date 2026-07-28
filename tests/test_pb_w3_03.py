"""PB-W3-03 — CLAUDE.md symlinks to AGENTS.md.

Symlinks are built at runtime, never committed: a committed symlink fixture can
materialise as a regular file on checkout, which is the very defect this check
exists to catch. Building it here keeps the test honest on every host.
"""

from __future__ import annotations

import os

from playbook_doctor.checks.pb_w3_03 import check
from playbook_doctor.registry import Status


def _with_agents(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Agents\n")
    return tmp_path / "CLAUDE.md"


def test_pass_when_symlinked_to_agents_md(tmp_path):
    claude = _with_agents(tmp_path)
    os.symlink("AGENTS.md", claude)
    assert check(tmp_path).status is Status.PASS


def test_fail_when_regular_file_even_if_identical(tmp_path):
    claude = _with_agents(tmp_path)
    claude.write_text("# Agents\n")  # byte-identical copy
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "regular file" in (verdict.detail or "")


def test_fail_when_symlink_points_elsewhere(tmp_path):
    claude = _with_agents(tmp_path)
    (tmp_path / "README.md").write_text("# Readme\n")
    os.symlink("README.md", claude)
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "not AGENTS.md" in (verdict.detail or "")


def test_fail_when_symlink_is_broken(tmp_path):
    claude = _with_agents(tmp_path)
    os.symlink("GONE.md", claude)
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "broken" in (verdict.detail or "")


def test_skip_when_claude_md_absent(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Agents\n")
    assert check(tmp_path).status is Status.SKIP
