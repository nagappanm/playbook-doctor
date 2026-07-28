"""Check discovery, the Verdict model, and the audit engine.

A check is a pure function ``(repo_root: Path) -> Verdict``. It reads the
filesystem and returns a single Verdict; it never mutates the repo under audit
and shares no state with other checks. Modules under ``playbook_doctor.checks``
register themselves here via the ``register`` decorator; ``load_checks`` imports
them so the registry is populated before an audit runs.

Scoring and exit-code rules live here because they are engine semantics, not
presentation. See specs/playbook-doctor.md §3–§4.
"""

from __future__ import annotations

import dataclasses
import enum
import importlib
import pkgutil
from collections.abc import Callable, Iterable
from pathlib import Path


class Status(enum.Enum):
    """The four verdict outcomes. See specs/playbook-doctor.md §3."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"

    @property
    def blocks(self) -> bool:
        """Whether this status drives a non-zero exit code."""
        return self is Status.FAIL

    @property
    def scored(self) -> bool:
        """Whether this status counts toward the score denominator."""
        return self is not Status.SKIP


@dataclasses.dataclass(frozen=True)
class Verdict:
    """One check's result. ``detail`` is required for anything but PASS."""

    id: str
    week: str
    title: str
    status: Status
    detail: str | None = None


CheckFn = Callable[[Path], Verdict]


@dataclasses.dataclass(frozen=True)
class Check:
    """A registered check: its stable identity plus the function that runs it."""

    id: str
    week: str
    title: str
    fn: CheckFn

    def run(self, root: Path) -> Verdict:
        """Run the check, converting any escaped exception into a verdict.

        A check is contracted never to crash (AGENTS.md: "Never crash on a
        malformed repo"). If one does anyway that is a bug in the check, not a
        defect in the audited repo -- so it surfaces as WARN, visible but
        non-blocking, rather than failing someone else's build on our own bug.
        """
        try:
            return self.fn(root)
        except Exception as exc:
            return Verdict(
                self.id,
                self.week,
                self.title,
                Status.WARN,
                f"check raised {type(exc).__name__}: {exc}",
            )


_REGISTRY: list[Check] = []


def register(check_id: str, week: str, title: str) -> Callable[[CheckFn], CheckFn]:
    """Register a check function under its stable ID.

    The metadata is held on the ``Check`` so the engine can name a check even
    when the function itself raises before returning a Verdict.
    """

    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY.append(Check(check_id, week, title, fn))
        return fn

    return decorator


def checks() -> list[Check]:
    """The registered checks, in registration order."""
    return list(_REGISTRY)


def load_checks() -> list[Check]:
    """Import every module under ``playbook_doctor.checks`` so they register.

    Idempotent: re-importing an already-imported module does not re-run its
    body, so each check registers exactly once no matter how often this is
    called.
    """
    from playbook_doctor import checks as checks_pkg

    for info in pkgutil.iter_modules(checks_pkg.__path__, f"{checks_pkg.__name__}."):
        importlib.import_module(info.name)
    return checks()


def run_all(root: Path) -> list[Verdict]:
    """Run every registered check against ``root``, isolating per-check failures."""
    return [check.run(root) for check in checks()]


def score(verdicts: Iterable[Verdict]) -> float | None:
    """PASS / (PASS + WARN + FAIL). SKIP is excluded from both sides.

    Returns ``None`` when nothing is scored (an empty or all-SKIP audit), which
    the report renders as "n/a" rather than inventing a 0% or dividing by zero.
    """
    scored = [v for v in verdicts if v.status.scored]
    if not scored:
        return None
    passed = sum(1 for v in scored if v.status is Status.PASS)
    return passed / len(scored)


def exit_code(verdicts: Iterable[Verdict]) -> int:
    """0 when no check blocks, 1 when any does. Usage errors (2) belong to the CLI."""
    return 1 if any(v.status.blocks for v in verdicts) else 0
