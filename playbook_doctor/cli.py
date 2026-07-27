"""Command-line entry point.

Stub only: the real engine (registry, verdicts, report) lands in U3. This exists
so the package installs and the console script resolves while the guardrails are
being proven out in U1.
"""

import sys


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    print("playbook-doctor: not implemented yet (engine lands in U3)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
