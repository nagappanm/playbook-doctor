"""PB-W2-01 — AGENTS.md within context budget.

AGENTS.md is loaded on every request, so its length is a recurring token cost on
every turn, not a one-time read. Over the threshold is WARN, never FAIL — a long
AGENTS.md is a cost smell, not a broken artefact. The 400-line threshold is
provisional and flagged for calibration in the spec.
"""

from __future__ import annotations

from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W2-01", "W2", "AGENTS.md within context budget"

_MAX_LINES = 400


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return Verdict(ID, WEEK, TITLE, Status.SKIP, "AGENTS.md absent (PB-W3-01 owns that)")

    lines = len(agents.read_text(encoding="utf-8", errors="replace").splitlines())
    if lines <= _MAX_LINES:
        return Verdict(ID, WEEK, TITLE, Status.PASS)
    detail = f"AGENTS.md is {lines} lines (> {_MAX_LINES}); it loads on every request"
    return Verdict(ID, WEEK, TITLE, Status.WARN, detail)
