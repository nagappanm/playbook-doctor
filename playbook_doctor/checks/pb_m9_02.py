"""PB-M9-02 — loop exits 0 only on a green test signal.

The model must never be the voice that says "done". A loop that can reach a
top-level ``exit 0`` without ever running a test has let the agent declare its own
success. FAIL is reserved for the unambiguous case — an ``exit 0`` with no test
command anywhere. When a test command is present but its wiring to the exit is
unclear, WARN: the split by confidence is deliberate (NOTES.md, U2).
"""

from __future__ import annotations

import re
from pathlib import Path

from playbook_doctor.loops import find_loop_scripts
from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-M9-02", "M9", "loop exits 0 only on a green test signal"

_TEST = r"pytest|npm test|go test|playwright|make test"
_TEST_CMD = re.compile(_TEST)
_EXIT_ZERO = re.compile(r"^\s*exit\s+0\b", re.MULTILINE)
_GUARD_SAMELINE = re.compile(rf"({_TEST}).*&&")
_GUARD_IF = re.compile(rf"if\s+.*({_TEST})")
_GUARD_STATUS = re.compile(r"\$\?")
_RANK = {Status.PASS: 0, Status.WARN: 1, Status.FAIL: 2}


def _guarded(text: str) -> bool:
    return any(p.search(text) for p in (_GUARD_SAMELINE, _GUARD_IF, _GUARD_STATUS))


def _classify(text: str) -> Status:
    if _TEST_CMD.search(text):
        return Status.PASS if _guarded(text) else Status.WARN
    if _EXIT_ZERO.search(text):
        return Status.FAIL
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
        return Verdict(ID, WEEK, TITLE, Status.FAIL, f"{rel} can exit 0 without running tests")
    return Verdict(ID, WEEK, TITLE, Status.WARN, f"{rel}: completion not clearly gated on tests")
