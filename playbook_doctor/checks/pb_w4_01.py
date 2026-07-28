"""PB-W4-01 — mcp.json parses.

Not every repo uses MCP, so an absent config is SKIP, not a finding. But a
*present* config that does not parse is FAIL: a malformed mcp.json means the
tools an agent expects to have silently fail to load. Searched in tool-preference
order — repo root, then VS Code, then Cursor.
"""

from __future__ import annotations

import json
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W4-01", "W4", "mcp.json parses"

_CANDIDATES = (".mcp.json", ".vscode/mcp.json", ".cursor/mcp.json")


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    for name in _CANDIDATES:
        path = root / name
        if not path.is_file():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except ValueError as exc:
            return Verdict(ID, WEEK, TITLE, Status.FAIL, f"{name} is malformed JSON: {exc}")
        return Verdict(ID, WEEK, TITLE, Status.PASS, f"{name} parses")

    return Verdict(ID, WEEK, TITLE, Status.SKIP, "no MCP config found")
