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
from collections.abc import Iterable
from pathlib import Path

from playbook_doctor.registry import Status, Verdict

_TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# template filename in templates/  ->  destination path relative to the repo root
_SCAFFOLD = {
    "AGENTS.md": "AGENTS.md",
    "pre-commit-config.yaml": ".pre-commit-config.yaml",
    "claude-settings.json": ".claude/settings.json",
}

# Additive repairs: check id -> (template, destination). Applied by `fix` only
# when the destination is ABSENT. If the target already exists, the check flagged
# its *content*, not its absence, and editing content is refused (spec §6).
_REPAIRS = {
    "PB-W3-01": ("AGENTS.md", "AGENTS.md"),
    "PB-W5-01": ("pre-commit-config.yaml", ".pre-commit-config.yaml"),
    "PB-W5-04": ("claude-settings.json", ".claude/settings.json"),
}

# Flagged checks that `fix` cannot repair additively, with the reason it refuses.
# Each names a human-owned edit spec §6 keeps off-limits.
_REFUSALS = {
    "PB-W3-02": "would require editing AGENTS.md content",
    "PB-W5-02": "would require editing .pre-commit-config.yaml content",
}
_LOOP_CHECKS = frozenset({"PB-M9-01", "PB-M9-02", "PB-M9-03"})


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


def _create_absent(root: Path, template_name: str, dest_rel: str) -> tuple[str, str]:
    dest = root / dest_rel
    if dest.exists() or dest.is_symlink():
        return ("refused", f"{dest_rel}: exists; editing it is not an additive repair")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text((_TEMPLATES / template_name).read_text(encoding="utf-8"), encoding="utf-8")
    return ("created", dest_rel)


def fix(root: Path, verdicts: Iterable[Verdict]) -> list[tuple[str, str]]:
    """Apply additive repairs only (spec §6) for the checks that flagged.

    Returns an ordered list of ``(outcome, detail)`` where outcome is ``created``,
    ``symlinked``, or ``refused``. Every repair either creates something absent or
    refuses with a printed reason — it never edits or deletes a human's file. The
    caller re-runs the audit afterwards and exits on *that* status; a refusal is
    not itself an error.
    """
    flagged = {v.id for v in verdicts if v.status in (Status.FAIL, Status.WARN)}
    outcomes: list[tuple[str, str]] = []

    # AGENTS.md is created before the CLAUDE.md symlink so the link has a target.
    for check_id, (template_name, dest_rel) in _REPAIRS.items():
        if check_id in flagged:
            outcomes.append(_create_absent(root, template_name, dest_rel))

    # The CLAUDE.md symlink is driven by filesystem state, not the flagged set:
    # PB-W3-03 SKIPs when CLAUDE.md is absent, yet §6 permits creating it then.
    claude = root / "CLAUDE.md"
    agents = root / "AGENTS.md"
    linked = claude.is_symlink() and claude.exists() and claude.resolve() == agents.resolve()
    if linked:
        pass  # correct symlink already; nothing to do, nothing to say
    elif claude.exists() or claude.is_symlink():
        refusal = "CLAUDE.md: exists; replacing it with a symlink destroys content"
        outcomes.append(("refused", refusal))
    elif agents.exists():
        os.symlink("AGENTS.md", claude)
        outcomes.append(("symlinked", "CLAUDE.md -> AGENTS.md"))

    for check_id, reason in _REFUSALS.items():
        if check_id in flagged:
            outcomes.append(("refused", f"{check_id}: {reason}"))

    if "PB-W5-03" in flagged:
        if (root / ".secrets.baseline").is_file():
            reason = "auditing entries is a human judgement"
        else:
            reason = "needs a detect-secrets scan"
        outcomes.append(("refused", f".secrets.baseline: {reason}"))

    if flagged & _LOOP_CHECKS:
        outcomes.append(("refused", "loop script: rewriting a loop is not additive"))

    return outcomes
