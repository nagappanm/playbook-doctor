"""PB-W5-01 — .pre-commit-config.yaml exists.

Week 5 is guardrails. The pre-commit config is where format, lint, and
secret-scan hooks are wired; its absence means none of them run locally, so this
is a FAIL. Whether the right hooks are present is PB-W5-02's job.
"""

from __future__ import annotations

from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W5-01", "W5", ".pre-commit-config.yaml exists"


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    if (root / ".pre-commit-config.yaml").is_file():
        return Verdict(ID, WEEK, TITLE, Status.PASS)
    detail = ".pre-commit-config.yaml is missing from the repo root"
    return Verdict(ID, WEEK, TITLE, Status.FAIL, detail)
