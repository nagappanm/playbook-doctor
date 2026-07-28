"""PB-W3-01 — AGENTS.md exists.

The root of Week 3: an agent's operating instructions live in ``AGENTS.md`` at
the repo root. Without it there is nothing for the rest of the W3 catalog to
check, so this is a hard FAIL rather than a warning.
"""

from __future__ import annotations

from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W3-01", "W3", "AGENTS.md exists"


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    if (root / "AGENTS.md").is_file():
        return Verdict(ID, WEEK, TITLE, Status.PASS)
    return Verdict(ID, WEEK, TITLE, Status.FAIL, "AGENTS.md is missing from the repo root")
