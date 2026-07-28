# Evidence — Cross-repo dogfood

**Technique:** Dogfooding — run the finished auditor against the course's own
working repo and confirm it reproduces that repo's real agent-readiness gaps.

**When:** U6, after all fifteen non-gated checks and the `init` scaffolder were
complete and the tool passed its own audit.

## The two subjects

| Repo | Role | Self-audit score | Exit |
|---|---|---|---|
| `playbook-doctor` (this repo) | the "after" — built to the playbook | **91%** (10 PASS, 1 WARN, 0 FAIL, 6 SKIP) | 0 |
| `nagappanm/agentic-ai-engineering` | the "before" — the course working repo | **25%** (2 PASS, 4 WARN, 2 FAIL, 9 SKIP) | 1 |

> **Scores restated 2026-07-28.** This table first recorded 90% / 14%. Those were
> correct when written and went stale two PRs later — adding `PB-W5-05` and
> widening `PB-W6-01` changed both denominators. The figures above are re-measured
> against the current catalog. Recorded rather than quietly overwritten: a
> documented number that drifts from what the command actually prints is the same
> class of defect this tool exists to catch, and it surfaced only because the
> evidence was re-run instead of trusted.

Same tool, same catalog, run against both. The gap between the scores *is* the
result: the auditor cleanly separates a repo built to the playbook from one that
predates it.

## What it found in `agentic-ai-engineering`

```
FAIL PB-W3-01  AGENTS.md is missing from the repo root
FAIL PB-W5-01  .pre-commit-config.yaml is missing from the repo root
WARN PB-W5-03  no .secrets.baseline (a repo may scan without one)
WARN PB-W5-04  no Stop hook in .claude/settings.json
WARN PB-W6-01  no spec directory (specs/, spec/, docs/specs/, docs/spec/,
               .specify/) or root spec document
WARN PB-W7-01  no token or cost ceiling declared (advisory)
PASS PB-W5-05  CI runs guardrail scans: codeql, ruff, semgrep
PASS PB-W6-02  every SKILL.md carries required frontmatter
```

### The three substantive gaps

Every finding was verified by hand against the checkout — none is a false
positive. Three are the real agent-readiness gaps worth calling out:

1. **No `AGENTS.md` (FAIL).** The repo has a `.claude/` directory with agents and
   two well-formed skills — `PB-W6-02` PASSes on their frontmatter — but no
   portable, cross-tool operating manual. The agent config exists in one vendor's
   dialect and nowhere a second tool would read it.

2. **No local guardrails (FAIL).** There is no `.pre-commit-config.yaml`. The repo
   *does* ship `.github/workflows/semgrep.yml`, so scanning runs in CI — but
   nothing bites *before* a commit. This is the exact "config that looks
   configured" failure the tool exists for: a reviewer sees green CI and assumes
   local guardrails they do not have. `PB-W5-01` catches the absence that a CI
   badge hides.

3. **No stop hook (WARN).** `.claude/` has agents and skills but no
   `settings.json`, so nothing makes the agent run verification before declaring a
   task done. WARN, not FAIL — a strong practice, not a hard requirement — but
   surfaced where it was otherwise invisible.

The remaining WARNs (no secrets baseline, no `specs/`, no declared budget) are
honest absences the tool reports without over-claiming: each is `WARN`, none
blocks, and the score reflects them without pretending they are defects.

## Why this is the capstone claim

The tool is the eight-week course compiled into executable form. Pointing it at
the repo the course was *taught in* is the sharpest possible test: if the catalog
encodes the lessons faithfully, the pre-playbook repo should score low and for
reasons that map one-to-one onto the lessons. It does — and the two FAILs are
`W3` (AGENTS.md) and `W5` (guardrails), the two weeks whose absence most directly
breaks an agent's ability to work safely and verifiably.

## Verification

```bash
playbook-doctor check .                         # this repo  -> 91%, exit 0
playbook-doctor check ../agentic-ai-engineering # course repo -> 25%, exit 1
```

Re-run these before citing the numbers. The catalog is additive, so every new
check moves both denominators — which is exactly how the 90/14 figures above went
stale.
