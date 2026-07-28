"""PB-W6-02 — every SKILL.md carries required frontmatter.

A skill without a ``name`` and ``description`` cannot be discovered or dispatched
by the tools that load it — it is dead weight that looks like capability. Each
SKILL.md must open with YAML frontmatter carrying both, non-empty. SKIP when the
repo ships no skills; FAIL naming the file and the missing field.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import yaml

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W6-02", "W6", "every SKILL.md carries required frontmatter"

_EXCLUDE = {".venv", "node_modules", ".git"}


def _skill_files(root: Path) -> Iterator[Path]:
    try:
        for path in root.rglob("SKILL.md"):
            if _EXCLUDE.isdisjoint(path.parts):
                yield path
    except OSError:
        return


def _frontmatter(text: str) -> dict | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            try:
                data = yaml.safe_load("\n".join(lines[1:i]))
            except yaml.YAMLError:
                return None
            return data if isinstance(data, dict) else None
    return None


def _missing_fields(data: dict) -> list[str]:
    missing = []
    for field in ("name", "description"):
        value = data.get(field)
        if not (isinstance(value, str) and value.strip()):
            missing.append(field)
    return missing


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    skills = list(_skill_files(root))
    if not skills:
        return Verdict(ID, WEEK, TITLE, Status.SKIP, "no SKILL.md in the repo")

    problems: list[str] = []
    for path in skills:
        rel = path.relative_to(root)
        data = _frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if data is None:
            problems.append(f"{rel}: no YAML frontmatter")
        elif missing := _missing_fields(data):
            problems.append(f"{rel}: missing {', '.join(missing)}")

    if problems:
        return Verdict(ID, WEEK, TITLE, Status.FAIL, "; ".join(problems))
    return Verdict(ID, WEEK, TITLE, Status.PASS)
