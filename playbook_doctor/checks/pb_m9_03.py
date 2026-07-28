"""PB-M9-03 — loop works on a branch or worktree.

A bad night's autonomous work should be a ``git reset``, not an outage on the
default branch. This looks for a git isolation primitive — a worktree, a
``checkout -b``, or a ``switch -c``. WARN when none is found: running on a branch
is a strong safety practice, but it is not something to hard-fail a repo over.
"""

from __future__ import annotations

import re
from pathlib import Path

from playbook_doctor.loops import find_loop_scripts
from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-M9-03", "M9", "loop works on a branch or worktree"

_ISOLATION = re.compile(r"git\s+worktree|git\s+checkout\s+-b|git\s+switch\s+-c")


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    scripts = find_loop_scripts(root)
    if not scripts:
        return Verdict(ID, WEEK, TITLE, Status.SKIP, "no loop script found")

    for path in scripts:
        text = path.read_text(encoding="utf-8", errors="replace")
        if _ISOLATION.search(text):
            detail = f"{path.relative_to(root)} isolates work on a branch/worktree"
            return Verdict(ID, WEEK, TITLE, Status.PASS, detail)

    detail = "loop does not appear to isolate work on a branch or worktree"
    return Verdict(ID, WEEK, TITLE, Status.WARN, detail)
