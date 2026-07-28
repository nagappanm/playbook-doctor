# Implementation plan

The loop's backlog. One task per pass, topmost unchecked task whose dependencies
are satisfied. Check items off as they land.

Spec: `specs/playbook-doctor.md`

---

## U3 — core engine

- [x] `registry.py` — `Status` enum, frozen `Verdict` dataclass, `register` decorator, `run_all()` that isolates per-check exceptions
- [x] `report.py` — console rendering grouped by week, plus `--json` serialisation
- [x] `cli.py` — `check` command, `PATH` argument, `--json` flag, exit codes 0/1/2

## U4 — check modules

Each task: one module under `playbook_doctor/checks/`, one passing fixture, one
failing fixture, one test file. Commit separately.

- [x] `PB-W3-01` AGENTS.md exists
- [x] `PB-W3-02` AGENTS.md declares verification commands
- [x] `PB-W3-03` CLAUDE.md symlinks to AGENTS.md
- [x] `PB-W5-01` .pre-commit-config.yaml exists
- [x] `PB-W5-02` format + lint + secrets hooks present
- [x] `PB-W5-03` .secrets.baseline has no unaudited entries
- [x] `PB-W5-04` stop hook configured and non-empty
- [x] `PB-W2-01` AGENTS.md within context budget
- [x] `PB-W6-01` specs/ exists and non-empty
- [x] `PB-W6-02` every SKILL.md has required frontmatter
- [x] `PB-W7-01` token or cost ceiling declared
- [x] `PB-M9-01` loop caps iterations
- [x] `PB-M9-02` loop exits 0 only on green
- [x] `PB-M9-03` loop works on a branch or worktree
- [x] `PB-W4-01` mcp.json parses
- [ ] **`PB-W4-02` no inline credentials — HUMAN REVIEW REQUIRED, do not implement autonomously**

Ordering note: the W3/W5 checks come first because this repo already satisfies
them, so they can be verified against a known-good subject immediately. `PB-W4-02`
is last and gated.

## U5 — scaffolder

- [x] `templates/` — AGENTS.md, pre-commit config, hooks settings
- [x] `scaffold.py` — `init`, skip-existing, `--force`
- [ ] `--fix` wired to additive repairs only, per spec §6 — **HUMAN REVIEW REQUIRED**

## U6 — dogfood

- [ ] Self-audit green; CI step already wired in `.github/workflows/ci.yml`
- [ ] Run against `agentic-ai-engineering` and confirm it reproduces the three known gaps
