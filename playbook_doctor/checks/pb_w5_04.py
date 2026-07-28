"""PB-W5-04 — Stop hook configured and non-empty.

The stop hook is what makes the model run its own verification before claiming
"done". The failure this catches is the one that reads as configured at a glance:
an empty ``"Stop": []``, or entries that declare a matcher but wire no command.
Never FAIL — a stop hook is a strong practice, not a hard requirement — but the
empty-array case gets its own message because it is the deceptive one.
"""

from __future__ import annotations

import json
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W5-04", "W5", "stop hook configured"


def _stop_from(path: Path) -> object | None:
    """The ``hooks.Stop`` value from a settings file, or None if absent/broken."""
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except ValueError:
        return None
    hooks = data.get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, dict) or "Stop" not in hooks:
        return None
    return hooks.get("Stop")


def _has_command(stop: object) -> bool:
    for group in stop if isinstance(stop, list) else []:
        entries = group.get("hooks", []) if isinstance(group, dict) else []
        for entry in entries if isinstance(entries, list) else []:
            command = entry.get("command") if isinstance(entry, dict) else None
            if isinstance(command, str) and command.strip():
                return True
    return False


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    settings = _stop_from(root / ".claude" / "settings.json")
    local = _stop_from(root / ".claude" / "settings.local.json")
    present = [s for s in (settings, local) if s is not None]

    if not present:
        return Verdict(ID, WEEK, TITLE, Status.WARN, "no Stop hook in .claude/settings.json")
    if any(_has_command(s) for s in present):
        return Verdict(ID, WEEK, TITLE, Status.PASS)
    if not any(isinstance(s, list) and s for s in present):
        return Verdict(ID, WEEK, TITLE, Status.WARN, 'Stop hook configured but empty ("Stop": [])')
    return Verdict(ID, WEEK, TITLE, Status.WARN, "Stop hook declared but runs no command")
