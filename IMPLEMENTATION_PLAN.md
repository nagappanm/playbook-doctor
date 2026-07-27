# Implementation plan

The loop's backlog. One task per pass, topmost unchecked task whose dependencies
are satisfied. Check items off as they land.

Spec: `specs/playbook-doctor.md`

---

## U3 — core engine

- [ ] `registry.py` — `Status` enum, frozen `Verdict` dataclass, `register` decorator, `run_all()` that isolates per-check exceptions
- [ ] `report.py` — console rendering grouped by week, plus `--json` serialisation
- [ ] `cli.py` — `check` command, `PATH` argument, `--json` flag, exit codes 0/1/2

## U4 — check modules

Each task: one module under `playbook_doctor/checks/`, one passing fixture, one
failing fixture, one test file. Commit separately.

- [ ] `PB-W3-01` AGENTS.md exists
- [ ] `PB-W3-02` AGENTS.md declares verification commands
- [ ] `PB-W3-03` CLAUDE.md symlinks to AGENTS.md
- [ ] `PB-W5-01` .pre-commit-config.yaml exists
- [ ] `PB-W5-02` format + lint + secrets hooks present
- [ ] `PB-W5-03` .secrets.baseline has no unaudited entries
- [ ] `PB-W5-04` stop hook configured and non-empty
- [ ] `PB-W2-01` AGENTS.md within context budget
- [ ] `PB-W6-01` specs/ exists and non-empty
- [ ] `PB-W6-02` every SKILL.md has required frontmatter
- [ ] `PB-W7-01` token or cost ceiling declared
- [ ] `PB-M9-01` loop caps iterations
- [ ] `PB-M9-02` loop exits 0 only on green
- [ ] `PB-M9-03` loop works on a branch or worktree
- [ ] `PB-W4-01` mcp.json parses
- [ ] **`PB-W4-02` no inline credentials — HUMAN REVIEW REQUIRED, do not implement autonomously**

Ordering note: the W3/W5 checks come first because this repo already satisfies
them, so they can be verified against a known-good subject immediately. `PB-W4-02`
is last and gated.

## U5 — scaffolder

- [ ] `templates/` — AGENTS.md, pre-commit config, hooks settings
- [ ] `scaffold.py` — `init`, skip-existing, `--force`
- [ ] `--fix` wired to additive repairs only, per spec §6 — **HUMAN REVIEW REQUIRED**

## U6 — dogfood

- [ ] Self-audit green; CI step already wired in `.github/workflows/ci.yml`
- [ ] Run against `agentic-ai-engineering` and confirm it reproduces the three known gaps
