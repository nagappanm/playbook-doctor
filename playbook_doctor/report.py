"""Rendering: a grouped console report and a machine-readable JSON document.

Both consume the same list of Verdicts. The console form is grouped by week for
a human skim; the JSON form is stable and is the only thing ``--json`` prints.
"""

from __future__ import annotations

import json
from collections.abc import Sequence

from playbook_doctor.registry import Status, Verdict, score


def _week_key(week: str) -> tuple[int, int, str]:
    """Sort weeks ``W2 < W3 < ... < W7 < M9`` rather than lexically."""
    rank = {"W": 0, "M": 1}.get(week[:1], 2)
    try:
        num = int(week[1:])
    except ValueError:
        num = 0
    return (rank, num, week)


def _counts(verdicts: Sequence[Verdict]) -> dict[Status, int]:
    counts = dict.fromkeys(Status, 0)
    for v in verdicts:
        counts[v.status] += 1
    return counts


def _summary_line(verdicts: Sequence[Verdict]) -> str:
    counts = _counts(verdicts)
    sc = score(verdicts)
    pct = "n/a" if sc is None else f"{sc * 100:.0f}%"
    return (
        f"score {pct}  "
        f"({counts[Status.PASS]} pass, {counts[Status.WARN]} warn, "
        f"{counts[Status.FAIL]} fail, {counts[Status.SKIP]} skip)"
    )


def render_console(verdicts: Sequence[Verdict]) -> str:
    """A week-grouped, human-readable report ending in a summary line."""
    lines: list[str] = []
    for week in sorted({v.week for v in verdicts}, key=_week_key):
        lines.append(week)
        for v in sorted((v for v in verdicts if v.week == week), key=lambda v: v.id):
            tail = f" — {v.detail}" if v.detail else ""
            lines.append(f"  [{v.status.value}] {v.id}  {v.title}{tail}")
        lines.append("")
    lines.append(_summary_line(verdicts))
    return "\n".join(lines)


def render_json(verdicts: Sequence[Verdict]) -> str:
    """A stable JSON document: ``score``, ``summary`` counts, and every check."""
    doc = {
        "score": score(verdicts),
        "summary": {status.value: count for status, count in _counts(verdicts).items()},
        "checks": [
            {
                "id": v.id,
                "week": v.week,
                "title": v.title,
                "status": v.status.value,
                "detail": v.detail,
            }
            for v in verdicts
        ],
    }
    return json.dumps(doc, indent=2)
