"""Loop-script discovery, shared by the three M9 checks.

The M9 checks each judge a different property of a loop script, but they agree on
*what a loop script is*: a shell script named ``ralph.sh`` or matching ``*loop*.sh``,
at the repo root or under ``scripts/``. Keeping that definition in one place means
the three checks cannot drift on which files they consider — the helper is pure
and holds no state, so it does not couple the checks' logic.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

_PATTERNS = ("ralph.sh", "*loop*.sh")
_LOCATIONS = ("", "scripts")


def find_loop_scripts(root: Path) -> list[Path]:
    """Every loop script under ``root``, sorted, de-duplicated. Never raises."""
    found: set[Path] = set()
    for location in _LOCATIONS:
        base = root / location if location else root
        if not base.is_dir():
            continue
        try:
            entries = list(base.iterdir())
        except OSError:
            continue
        for path in entries:
            if path.is_file() and any(fnmatch.fnmatch(path.name, pat) for pat in _PATTERNS):
                found.add(path)
    return sorted(found)
