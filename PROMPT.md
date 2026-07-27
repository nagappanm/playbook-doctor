# Loop goal

Re-fed verbatim on every iteration. Each pass starts with an empty context
window, so this file plus the repo *is* the entire brief.

---

You are implementing `playbook-doctor`, a repository auditor. The authoritative
contract is `specs/playbook-doctor.md`. Read it before anything else.

## Your task this pass

1. Read `IMPLEMENTATION_PLAN.md` and pick **exactly one** unchecked task — the
   topmost one whose dependencies are already checked.
2. Read `NOTES.md` for what previous passes learned.
3. Implement that one task, following `AGENTS.md` conventions.
4. Run `make test` and `make lint`. **Tests are the only voice allowed to say
   "done".** If they are not green, you are not finished.
5. Commit with a conventional message scoped to that one task.
6. Append what you learned to `NOTES.md` — especially anything that surprised you
   or that the spec got wrong.
7. Check the task off in `IMPLEMENTATION_PLAN.md`.
8. Exit.

## Rules

- **One task per pass.** Do not batch. The next pass gets a fresh window and will
  pick up where you left off.
- **Do not read** `.venv/`, `__pycache__/`, or fixture directories other than the
  one for the check you are building.
- **Do not weaken a check to make tests pass.** If the repo cannot satisfy its own
  check, fix the repo or fix the check — do not lower the bar.
- **Stop and ask** before touching `PB-W4-02` (credential detection) or anything
  under `--fix`. Those paths stay human-reviewed.
- If the spec is ambiguous, write the ambiguity into `NOTES.md` and pick the
  conservative reading (`WARN` over `FAIL`).
