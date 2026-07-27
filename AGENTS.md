# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Overview

`playbook-doctor` audits a repository against the AI-engineering playbook and
scores its **agent-readiness**. Each check encodes one lesson from the eight-week
field manual, so the tool is that course compiled into executable form.

- `playbook_doctor/registry.py` — check discovery and the `Verdict` type.
- `playbook_doctor/checks/` — one module per check ID. Each is a pure function
  taking a repo root and returning a `Verdict`. No shared state between checks.
- `playbook_doctor/report.py` — console and JSON rendering.
- `playbook_doctor/cli.py` — the `check` and `init` commands.
- `templates/` — what `init` scaffolds. These ship as reusable artefacts.
- `specs/playbook-doctor.md` — **the authoritative check catalog.** Read this
  before adding or changing any check.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Verification

Run these before considering any change complete:

```bash
pytest -q                      # test suite must be green
ruff check .                   # lint must be clean
black --check .                # formatting must be clean
playbook-doctor check .        # the tool must pass its own audit
```

The last one is not optional. This repo is gated by its own tool; a change that
makes the self-audit fail is not done.

## Conventions

- **Checks are pure.** A check reads the filesystem and returns a `Verdict`. It
  never mutates the repo under audit. Mutation lives only in `scaffold.py`.
- **One check per module, one module per commit.** Check modules are independent
  by design so they can be built and reviewed one at a time.
- **Severity discipline.** `FAIL` is reserved for artefacts that are missing or
  *actively misleading* — a `CLAUDE.md` that has silently diverged from
  `AGENTS.md` is worse than no `CLAUDE.md` at all. Anything merely weak or
  absent-but-optional is `WARN`. `WARN` never affects the exit code.
- **Never crash on a malformed repo.** Unparseable config, permission errors, and
  symlink loops resolve to a `Verdict` with a readable message, never a traceback.
- **Conventional commits** (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).

## Cautions

- **Do not weaken a check to make the self-audit pass.** If this repo cannot
  satisfy its own check, that is either a real gap here or a bug in the check.
  Fix the right one; do not lower the bar.
- **`--fix` performs additive repairs only.** Creating a missing symlink or
  scaffolding an absent file is safe. Editing `AGENTS.md` content, pruning a
  secrets baseline, or rewriting a loop script is not — refuse with an
  explanation. The tool self-limits to the trust rung it has earned.
- **Credential-adjacent logic stays human-reviewed.** Changes to `PB-W4-02`
  (inline-credential detection) need a human in the loop.

## Do not read

Skip these unless a task explicitly requires them — they are large, generated, or
irrelevant to most changes, and reading them wastes context:

- `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`
- `tests/fixtures/**` — read only the fixture for the check you are working on
- `.secrets.baseline` — machine-generated; regenerate rather than hand-edit
