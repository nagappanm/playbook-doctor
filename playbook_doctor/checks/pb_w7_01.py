"""PB-W7-01 — token or cost ceiling declared.

The weakest check in the catalog, and it says so. There is no standard for
declaring a budget, so this looks in the two plausible places — an env key in
.claude/settings.json, or a budget line in AGENTS.md — and can only ever WARN.
It is a nudge toward cost-awareness, never a gate.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W7-01", "W7", "token or cost ceiling declared"

_ENV_KEY = re.compile(r"TOKEN|BUDGET|MAX_.*TOKENS|COST", re.IGNORECASE)
_AGENTS_LINE = re.compile(r"budget|token ceiling|max tokens|cost cap", re.IGNORECASE)


def _env_declares(root: Path) -> bool:
    path = root / ".claude" / "settings.json"
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except ValueError:
        return False
    env = data.get("env") if isinstance(data, dict) else None
    if not isinstance(env, dict):
        return False
    return any(isinstance(key, str) and _ENV_KEY.search(key) for key in env)


def _agents_mentions(root: Path) -> bool:
    path = root / "AGENTS.md"
    if not path.is_file():
        return False
    return _AGENTS_LINE.search(path.read_text(encoding="utf-8", errors="replace")) is not None


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    if _env_declares(root):
        return Verdict(ID, WEEK, TITLE, Status.PASS, "budget declared in .claude/settings.json env")
    if _agents_mentions(root):
        return Verdict(ID, WEEK, TITLE, Status.PASS, "budget mentioned in AGENTS.md")
    return Verdict(ID, WEEK, TITLE, Status.WARN, "no token or cost ceiling declared (advisory)")
