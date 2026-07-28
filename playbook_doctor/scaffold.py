"""Scaffolding for ``init``. Mutation lives here and only here.

Every check in this package is a pure read of the filesystem; ``init`` is the one
place that writes, and it is strictly additive. It creates absent artefacts from
``templates/`` and never edits or deletes anything a human wrote. Without
``force`` it skips every path that already exists; even with ``force`` it only
overwrites the scaffolded files themselves. The CLAUDE.md symlink is never
created over an existing path — replacing a human's regular CLAUDE.md with a
symlink would destroy content, which spec §6 refuses even under force.
"""

from __future__ import annotations

import os
from pathlib import Path

_TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# template filename in templates/  ->  destination path relative to the repo root
_SCAFFOLD = {
    "AGENTS.md": "AGENTS.md",
    "pre-commit-config.yaml": ".pre-commit-config.yaml",
    "claude-settings.json": ".claude/settings.json",
}


def _copy_template(root: Path, template_name: str, dest_rel: str, force: bool) -> tuple[str, str]:
    dest = root / dest_rel
    existed = dest.exists() or dest.is_symlink()
    if existed and not force:
        return ("skip", dest_rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text((_TEMPLATES / template_name).read_text(encoding="utf-8"), encoding="utf-8")
    return ("overwrite" if existed else "create", dest_rel)


def _link_claude_md(root: Path) -> tuple[str, str]:
    claude = root / "CLAUDE.md"
    if claude.exists() or claude.is_symlink():
        # Never replace an existing CLAUDE.md, even with --force: it may be a
        # human-written regular file, and clobbering it destroys content.
        return ("skip", "CLAUDE.md")
    os.symlink("AGENTS.md", claude)
    return ("symlink", "CLAUDE.md")


def init(root: Path, force: bool = False) -> list[tuple[str, str]]:
    """Scaffold the absent playbook artefacts under ``root``.

    Returns an ordered list of ``(action, path)`` where action is one of
    ``create``, ``overwrite``, ``skip``, or ``symlink`` — a record of exactly
    what was and was not touched, for the CLI to print.
    """
    actions = [
        _copy_template(root, template_name, dest_rel, force)
        for template_name, dest_rel in _SCAFFOLD.items()
    ]
    actions.append(_link_claude_md(root))
    return actions
