"""PB-W5-03 — .secrets.baseline has no unaudited entries.

A baseline exists to record a human's "yes, I looked, this is not a secret"
decision for each finding. An entry whose ``is_secret`` is absent or null has not
been audited — it is a finding nobody has ruled on, silently suppressed. This is
the exact drift NOTES.md records: the config transferred but its audited state
did not. Absent baseline is WARN (a repo may scan without one); unaudited entries
are FAIL.
"""

from __future__ import annotations

import json
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W5-03", "W5", ".secrets.baseline has no unaudited entries"


def _count_unaudited(data: object) -> int:
    results = data.get("results", {}) if isinstance(data, dict) else {}
    values = results.values() if isinstance(results, dict) else []
    return sum(
        1
        for findings in values
        for entry in (findings if isinstance(findings, list) else [])
        if isinstance(entry, dict) and entry.get("is_secret") is None
    )


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    baseline = root / ".secrets.baseline"
    if not baseline.is_file():
        absent = "no .secrets.baseline (a repo may scan without one)"
        return Verdict(ID, WEEK, TITLE, Status.WARN, absent)

    try:
        data = json.loads(baseline.read_text(encoding="utf-8", errors="replace"))
    except ValueError as exc:
        return Verdict(ID, WEEK, TITLE, Status.FAIL, f"unparseable .secrets.baseline: {exc}")

    unaudited = _count_unaudited(data)
    if unaudited == 0:
        return Verdict(ID, WEEK, TITLE, Status.PASS)
    plural = "entry" if unaudited == 1 else "entries"
    detail = f"{unaudited} unaudited {plural} in .secrets.baseline"
    return Verdict(ID, WEEK, TITLE, Status.FAIL, detail)
