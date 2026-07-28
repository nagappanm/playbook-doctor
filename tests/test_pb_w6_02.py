"""PB-W6-02 — every SKILL.md carries required frontmatter."""

from __future__ import annotations

from playbook_doctor.checks.pb_w6_02 import check
from playbook_doctor.registry import Status

_GOOD = "---\nname: deploy\ndescription: Ship the app safely.\n---\n\n# Deploy\n"


def _skill(tmp_path, rel, text):
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_pass_when_frontmatter_is_complete(tmp_path):
    _skill(tmp_path, "skills/deploy/SKILL.md", _GOOD)
    assert check(tmp_path).status is Status.PASS


def test_fail_names_file_and_missing_field(tmp_path):
    _skill(tmp_path, "skills/x/SKILL.md", "---\nname: x\n---\n# X\n")
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "description" in (verdict.detail or "")
    assert "skills/x/SKILL.md" in (verdict.detail or "")


def test_fail_when_no_frontmatter(tmp_path):
    _skill(tmp_path, "skills/x/SKILL.md", "# X\n\nNo frontmatter here.\n")
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "frontmatter" in (verdict.detail or "")


def test_skip_when_no_skill_files(tmp_path):
    assert check(tmp_path).status is Status.SKIP


def test_excluded_directories_are_ignored(tmp_path):
    _skill(tmp_path, "node_modules/pkg/SKILL.md", "# broken\n")
    # The only SKILL.md is under an excluded dir, so the repo has no skills.
    assert check(tmp_path).status is Status.SKIP
