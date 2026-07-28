"""PB-W3-02 — AGENTS.md declares verification commands.

Rules an agent cannot verify against are decoration. This checks that AGENTS.md
carries a verification section *and* at least one fenced code block to run — it
deliberately does not judge whether the commands are the right ones (spec §7).
"""

from __future__ import annotations

import re
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W3-02", "W3", "AGENTS.md declares verification commands"

_HEADING = re.compile(r"^#{1,6}\s+.*\b(verif\w*|test\w*|check\w*)", re.IGNORECASE | re.MULTILINE)
_FENCE = re.compile(r"^```", re.MULTILINE)


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return Verdict(ID, WEEK, TITLE, Status.SKIP, "AGENTS.md absent (PB-W3-01 owns that)")

    text = agents.read_text(encoding="utf-8", errors="replace")
    has_heading = _HEADING.search(text) is not None
    # An opening and a closing fence -- two or more fence markers.
    has_fence = len(_FENCE.findall(text)) >= 2

    if has_heading and has_fence:
        return Verdict(ID, WEEK, TITLE, Status.PASS)

    missing = []
    if not has_heading:
        missing.append("a verification/test/check heading")
    if not has_fence:
        missing.append("a fenced code block of commands")
    return Verdict(ID, WEEK, TITLE, Status.FAIL, f"AGENTS.md lacks {' and '.join(missing)}")
