"""PB-W6-01 — spec artefacts present.

Week 6 is spec-driven development: a human-authored contract the agent builds
against. Its absence is WARN, not FAIL — plenty of healthy repos have no specs,
and this is an encouragement, not a gate.

The search is deliberately broad. A cross-repo audit found spec-driven repos that
keep their specs outside a `specs/` directory — as a root-level `spec-driven.md`,
or under `.specify/` — so this accepts either a conventional spec directory or a
root-level spec document. Widening a WARN-only check costs little; under-crediting
a repo that clearly does spec-driven work is the worse error.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W6-01", "W6", "spec artefacts present"

_DIR_CANDIDATES = ("specs", "spec", "docs/specs", "docs/spec", ".specify")
_FILE_PATTERNS = ("spec.md", "specs.md", "spec-*.md", "*-spec.md")


def _has_file(directory: Path) -> bool:
    try:
        return any(p.is_file() for p in directory.rglob("*"))
    except OSError:
        return False


def _spec_document(root: Path) -> str | None:
    try:
        entries = list(root.iterdir())
    except OSError:
        return None
    for entry in entries:
        name = entry.name.lower()
        if entry.is_file() and any(fnmatch.fnmatch(name, pat) for pat in _FILE_PATTERNS):
            return entry.name
    return None


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    for name in _DIR_CANDIDATES:
        directory = root / name
        if directory.is_dir() and _has_file(directory):
            return Verdict(ID, WEEK, TITLE, Status.PASS, f"{name}/ present")

    document = _spec_document(root)
    if document is not None:
        return Verdict(ID, WEEK, TITLE, Status.PASS, f"{document} present")

    searched = ", ".join(f"{c}/" for c in _DIR_CANDIDATES)
    detail = f"no spec directory ({searched}) or root spec document"
    return Verdict(ID, WEEK, TITLE, Status.WARN, detail)
