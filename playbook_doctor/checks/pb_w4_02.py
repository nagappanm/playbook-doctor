"""PB-W4-02 — no inline credentials in mcp.json.

Credential-adjacent, and human-reviewed by policy (AGENTS.md). A finding is a
string value whose *key* names a secret (`token|key|secret|password|credential`)
and whose value is a non-empty literal rather than an environment reference
(`${VAR}`, `$VAR`, `env:VAR`). The report names the offending key *paths* and
never the values — printing a leaked secret to fix a leaked secret would defeat
the point.

Only string values sitting directly under a matching dict key are candidates; a
string buried in a list has no key of its own to judge. A malformed config is
SKIP here, deferring the malformed-FAIL to PB-W4-01 so one broken file is not
reported twice.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W4-02", "W4", "no inline credentials in mcp.json"

_CANDIDATES = (".mcp.json", ".vscode/mcp.json", ".cursor/mcp.json")
_SENSITIVE_KEY = re.compile(r"token|key|secret|password|credential", re.IGNORECASE)
_ENV_REF = re.compile(r"^\$\{[^}]+\}$|^\$[A-Za-z_][A-Za-z0-9_]*$|^env:[A-Za-z_][A-Za-z0-9_]*$")


def _is_inline_secret(value: str) -> bool:
    """A non-empty literal that is not an environment reference."""
    stripped = value.strip()
    return bool(stripped) and _ENV_REF.match(stripped) is None


def _collect(node: object, path: str, found: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            sensitive = _SENSITIVE_KEY.search(str(key)) is not None
            if isinstance(value, str) and sensitive and _is_inline_secret(value):
                found.append(child)
            _collect(value, child, found)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _collect(value, f"{path}[{index}]", found)


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    for name in _CANDIDATES:
        path = root / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except ValueError:
            return Verdict(ID, WEEK, TITLE, Status.SKIP, f"{name} does not parse (see PB-W4-01)")

        found: list[str] = []
        _collect(data, "", found)
        if not found:
            return Verdict(ID, WEEK, TITLE, Status.PASS, f"{name}: no inline credentials")
        detail = f"{name}: inline credential(s) at {', '.join(found)}"
        return Verdict(ID, WEEK, TITLE, Status.FAIL, detail)

    return Verdict(ID, WEEK, TITLE, Status.SKIP, "no MCP config found")
