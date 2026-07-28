"""PB-M9-01 — loop caps its iterations.

An agent loop with no ceiling is a runaway: it burns tokens until something else
stops it. This looks for a bounded construct (a MAX_ITER, a --max-iters flag, a
seq-driven for, or a counter-tested while). A bare ``while true`` / ``while :``
with no counter guard is FAIL; anything it cannot read confidently is WARN,
because a check that cannot be sure must not block a merge.
"""

from __future__ import annotations

import re
from pathlib import Path

from playbook_doctor.loops import find_loop_scripts
from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-M9-01", "M9", "loop caps its iterations"

_BOUNDED = (
    re.compile(r"MAX_ITER", re.IGNORECASE),
    re.compile(r"--max-iters"),
    re.compile(r"for\s+\w+\s+in\s+\$\(\s*seq"),
    re.compile(r"while\s*\(\("),  # arithmetic while (( i < n ))
    re.compile(r"while\s+\[.*-(lt|le|gt|ge).*\]"),  # while [ $i -lt N ]
)
_INFINITE = re.compile(r"while\s+(true|:)\b")
_COUNTER_GUARD = re.compile(r"-(lt|le|gt|ge)\b|MAX_ITER", re.IGNORECASE)
_RANK = {Status.PASS: 0, Status.WARN: 1, Status.FAIL: 2}


def _classify(text: str) -> Status:
    if any(pattern.search(text) for pattern in _BOUNDED):
        return Status.PASS
    if _INFINITE.search(text):
        # An infinite header with some numeric guard *might* break out; we cannot
        # confirm the bound, so WARN rather than clear it or fail it outright.
        return Status.WARN if _COUNTER_GUARD.search(text) else Status.FAIL
    return Status.WARN


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    scripts = find_loop_scripts(root)
    if not scripts:
        return Verdict(ID, WEEK, TITLE, Status.SKIP, "no loop script found")

    worst, worst_path = Status.PASS, scripts[0]
    for path in scripts:
        status = _classify(path.read_text(encoding="utf-8", errors="replace"))
        if _RANK[status] > _RANK[worst]:
            worst, worst_path = status, path

    if worst is Status.PASS:
        return Verdict(ID, WEEK, TITLE, Status.PASS)
    rel = worst_path.relative_to(root)
    if worst is Status.FAIL:
        return Verdict(ID, WEEK, TITLE, Status.FAIL, f"{rel} loops with no iteration cap")
    return Verdict(ID, WEEK, TITLE, Status.WARN, f"{rel}: could not confirm an iteration cap")
