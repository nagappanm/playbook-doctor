"""PB-W3-03 — CLAUDE.md symlinks to AGENTS.md.

A copied CLAUDE.md is worse than an absent one: it silently feeds a second agent
a divergent copy of the rules. So a regular-file CLAUDE.md is FAIL *even when its
content is byte-identical today* — content equality now is not equality tomorrow.
The copy is the defect, not the drift.
"""

from __future__ import annotations

from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W3-03", "W3", "CLAUDE.md symlink"


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    claude = root / "CLAUDE.md"

    # is_symlink() is true even for a broken link; exists() follows it. Absent
    # means neither -- nothing there at all.
    if not claude.is_symlink() and not claude.exists():
        return Verdict(ID, WEEK, TITLE, Status.SKIP, "CLAUDE.md absent")

    if claude.is_symlink():
        agents = (root / "AGENTS.md").resolve()
        if not claude.exists():
            return Verdict(ID, WEEK, TITLE, Status.FAIL, "CLAUDE.md is a broken symlink")
        if claude.resolve() == agents:
            return Verdict(ID, WEEK, TITLE, Status.PASS)
        return Verdict(
            ID, WEEK, TITLE, Status.FAIL, f"CLAUDE.md symlinks to {claude.resolve()}, not AGENTS.md"
        )

    return Verdict(
        ID,
        WEEK,
        TITLE,
        Status.FAIL,
        "CLAUDE.md is a regular file, not a symlink to AGENTS.md — a copy drifts silently",
    )
