"""PB-W5-02 — format, lint, and secret-scan hooks all present.

A pre-commit config that exists but wires only a formatter leaves lint and
secret-scanning to chance. This collects every hook id and requires at least one
from each of the three guardrail categories. A present-but-unparseable config is
FAIL, not SKIP: a broken config is a guardrail that silently does not run.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from playbook_doctor.registry import Status, Verdict, register

ID, WEEK, TITLE = "PB-W5-02", "W5", "format, lint, and secret-scan hooks present"

_CATEGORIES = {
    "format": {"black", "ruff-format", "prettier", "gofmt", "rustfmt"},
    "lint": {"ruff", "flake8", "eslint", "pylint", "golangci-lint"},
    "secrets": {"detect-secrets", "gitleaks", "trufflehog"},
}


def _collect_ids(data: object) -> set[str]:
    """Every ``hooks[].id`` in the config, defensively — never assume shape."""
    ids: set[str] = set()
    repos = data.get("repos", []) if isinstance(data, dict) else []
    for repo in repos if isinstance(repos, list) else []:
        hooks = repo.get("hooks", []) if isinstance(repo, dict) else []
        for hook in hooks if isinstance(hooks, list) else []:
            hid = hook.get("id") if isinstance(hook, dict) else None
            if isinstance(hid, str):
                ids.add(hid)
    return ids


@register(ID, WEEK, TITLE)
def check(root: Path) -> Verdict:
    cfg = root / ".pre-commit-config.yaml"
    if not cfg.is_file():
        return Verdict(ID, WEEK, TITLE, Status.SKIP, ".pre-commit-config.yaml absent")

    try:
        data = yaml.safe_load(cfg.read_text(encoding="utf-8", errors="replace"))
    except yaml.YAMLError as exc:
        return Verdict(ID, WEEK, TITLE, Status.FAIL, f"unparseable .pre-commit-config.yaml: {exc}")

    ids = _collect_ids(data)
    missing = [cat for cat, recognised in _CATEGORIES.items() if ids.isdisjoint(recognised)]
    if not missing:
        return Verdict(ID, WEEK, TITLE, Status.PASS)
    return Verdict(ID, WEEK, TITLE, Status.FAIL, f"no {', '.join(missing)} hook found")
