"""PB-W5-05 — CI runs guardrail scans.

Local pre-commit (PB-W5-01/02) is the hard requirement because it bites *before*
a commit. CI scanning is a weaker second line — it only bites after a push — but
it is real defense-in-depth, and a repo that has it should get credit rather than
be scored as having no guardrails at all. So this is WARN-max, never FAIL: the
absence of *local* hooks is already PB-W5-01's concern. A repo can FAIL W5-01 and
PASS W5-05 at once, which is an accurate picture, not a contradiction — exactly
the case a cross-repo audit surfaced (semgrep in CI, no local pre-commit).
"""

from __future__ import annotations

import re
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W5-05", "W5", "CI runs guardrail scans"

_SIGNALS = (
    # secret scanning
    "detect-secrets",
    "gitleaks",
    "trufflehog",
    # SAST
    "semgrep",
    "codeql",
    "bandit",
    "snyk",
    # lint / format
    "ruff",
    "black",
    "flake8",
    "eslint",
    "prettier",
    "pylint",
    "golangci-lint",
    # running the local hooks in CI
    "pre-commit",
)
# Whole-word match so "black" does not fire on "blacklist", etc.
_SIGNAL_RE = re.compile(r"\b(" + "|".join(re.escape(s) for s in _SIGNALS) + r")\b", re.IGNORECASE)


def _workflow_text(root: Path) -> str | None:
    """Concatenated text of every workflow file, or None when there is no CI."""
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return None
    try:
        files = [p for p in workflows.iterdir() if p.is_file() and p.suffix in (".yml", ".yaml")]
    except OSError:
        return None
    if not files:
        return None
    chunks = []
    for path in files:
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return "\n".join(chunks)


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    text = _workflow_text(root)
    if text is None:
        return Verdict(ID, WEEK, TITLE, Status.SKIP, "no .github/workflows to judge")

    found = sorted({match.lower() for match in _SIGNAL_RE.findall(text)})
    if found:
        return Verdict(ID, WEEK, TITLE, Status.PASS, f"CI runs guardrail scans: {', '.join(found)}")
    detail = "CI workflows present but none run a guardrail scan"
    return Verdict(ID, WEEK, TITLE, Status.WARN, detail)
