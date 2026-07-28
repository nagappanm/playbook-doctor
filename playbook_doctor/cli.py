"""Command-line entry point: ``playbook-doctor check|init [PATH]``.

The engine (registry, checks, report) and scaffolder do the work; this module is
argument parsing, path validation, and exit-code plumbing. Exit codes follow the
spec: 0 clean, 1 at least one FAIL, 2 a usage error (argparse emits 2 on its own
for bad flags and missing commands).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playbook_doctor import registry, report, scaffold


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="playbook-doctor",
        description="Audit a repository against the AI-engineering playbook.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Audit a repository and score it.")
    check.add_argument("path", nargs="?", default=".", help="Repo root (default: .)")
    check.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON to stdout, and nothing else.",
    )
    check.add_argument(
        "--fix",
        action="store_true",
        help="Apply additive repairs only (spec §6), then re-audit and report.",
    )

    init = sub.add_parser("init", help="Scaffold absent playbook artefacts from templates.")
    init.add_argument("path", nargs="?", default=".", help="Repo root (default: .)")
    init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite scaffolded files that already exist (never the CLAUDE.md symlink).",
    )
    return parser


def _apply_fixes(root: Path, as_json: bool) -> None:
    """Run additive repairs and log them. In --json mode the log goes to stderr
    so stdout stays pure JSON; otherwise it prints above the re-audit report."""
    outcomes = scaffold.fix(root, registry.run_all(root))
    stream = sys.stderr if as_json else sys.stdout
    if not outcomes:
        print("repairs: nothing additive to do", file=stream)
        return
    print("repairs:", file=stream)
    for outcome, detail in outcomes:
        print(f"  {outcome:9} {detail}", file=stream)


def _cmd_check(path_arg: str, as_json: bool, as_fix: bool) -> int:
    root = Path(path_arg)
    if not root.is_dir():
        print(f"playbook-doctor: not a directory: {path_arg}", file=sys.stderr)
        return 2

    registry.load_checks()
    if as_fix:
        _apply_fixes(root, as_json)

    verdicts = registry.run_all(root)
    print(report.render_json(verdicts) if as_json else report.render_console(verdicts))
    return registry.exit_code(verdicts)


def _cmd_init(path_arg: str, force: bool) -> int:
    root = Path(path_arg)
    if not root.is_dir():
        print(f"playbook-doctor: not a directory: {path_arg}", file=sys.stderr)
        return 2

    for action, rel in scaffold.init(root, force=force):
        print(f"  {action:9} {rel}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    args = _build_parser().parse_args(argv)
    if args.command == "init":
        return _cmd_init(args.path, args.force)
    return _cmd_check(args.path, args.json, args.fix)


if __name__ == "__main__":
    raise SystemExit(main())
