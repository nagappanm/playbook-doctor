"""PB-W6-01 — specs/ exists and is non-empty.

Week 6 is spec-driven development: a human-authored contract the agent builds
against. Its absence is WARN, not FAIL — plenty of healthy repos have no specs
directory, and this is an encouragement, not a gate.
"""

from __future__ import annotations

from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W6-01", "W6", "specs/ exists and is non-empty"

_CANDIDATES = ("specs", "spec", "docs/specs")


def _has_file(directory: Path) -> bool:
    try:
        return any(p.is_file() for p in directory.rglob("*"))
    except OSError:
        return False


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    for name in _CANDIDATES:
        directory = root / name
        if directory.is_dir() and _has_file(directory):
            return Verdict(ID, WEEK, TITLE, Status.PASS, f"{name}/ present")
    searched = ", ".join(f"{c}/" for c in _CANDIDATES)
    detail = f"no non-empty specs directory (searched {searched})"
    return Verdict(ID, WEEK, TITLE, Status.WARN, detail)
