# playbook-doctor

Audit a repository against the AI-engineering playbook and score its
**agent-readiness**.

A playbook is files, not folklore. If a teammate — or an agent — can clone your
repo and inherit the whole system, you have a playbook. If the knowledge lives in
one engineer's head, you have a liability. `playbook-doctor` makes that difference
a deterministic check instead of a matter of memory.

```
$ playbook-doctor check .

W3
  [PASS] PB-W3-01  AGENTS.md exists
  [PASS] PB-W3-02  AGENTS.md declares verification commands
  [PASS] PB-W3-03  CLAUDE.md symlink

W5
  [PASS] PB-W5-01  .pre-commit-config.yaml exists
  [PASS] PB-W5-03  .secrets.baseline has no unaudited entries
  [PASS] PB-W5-04  stop hook configured

W7
  [WARN] PB-W7-01  no token or cost ceiling declared (advisory)

score 91%  (10 pass, 1 warn, 0 fail, 6 skip)
```

Exit `0` when nothing fails, `1` when something does, `2` on a usage error.
`WARN` never blocks.

---

## Why this exists

The failure mode it was built for is **config that looks configured**:

- `"Stop": []` — a hook array that is present, empty, and does nothing
- a `CLAUDE.md` that was copied instead of symlinked, and has since drifted from
  `AGENTS.md`, silently feeding a second agent different rules
- a `.secrets.baseline` that exists but carries unaudited entries
- green CI that scans nothing because the pipeline swallowed a non-zero exit

Each of these passes a glance and fails in practice. None is caught by a test
suite, because none is a test failure.

Every check encodes one lesson from an eight-week AI-engineering course — the
course compiled into executable form.

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```bash
playbook-doctor check .          # audit a repo
playbook-doctor check . --json   # machine-readable, for CI
playbook-doctor init             # scaffold the playbook layout
playbook-doctor check . --fix    # additive repairs only
```

### In CI

```yaml
- name: Self-audit
  shell: bash
  run: |
    set -o pipefail
    playbook-doctor check . --json | tee playbook-doctor-report.json
```

`set -o pipefail` is load-bearing — see design decision 5.

## What it checks

| Week | Checks |
|---|---|
| W2 | `AGENTS.md` within context budget |
| W3 | `AGENTS.md` exists · declares verification commands · `CLAUDE.md` symlinked |
| W4 | `mcp.json` parses · no inline credentials |
| W5 | pre-commit config · format+lint+secrets hooks · baseline audited · stop hook non-empty · CI guardrail scans |
| W6 | spec artefacts present · `SKILL.md` frontmatter valid |
| W7 | token or cost ceiling declared |
| M9 | loop caps iterations · exits 0 only on green · works on a branch |

Week 1 contributes no check — it is orientation and leaves no file artefact to
audit. Stated rather than silently omitted.

---

## Design decisions

### 1. Deterministic, offline, no LLM at runtime

Deterministic asserts are the cheapest and least ambiguous tier of verification,
and a repo auditor sits squarely in that tier. A second model scoring `AGENTS.md`
*quality* is a real idea — it is also noisy, non-reproducible, and expensive to run
on every push.

The consequence is a tool that costs nothing to run, gives the same answer twice,
and works with no API access. **Reproducibility was worth more than nuance.**

### 2. `FAIL` is reserved for things worse than absent

Four states — `PASS`, `WARN`, `FAIL`, `SKIP` — and only `FAIL` affects the exit
code.

The severity rule is not "how important is this" but **"is this actively
misleading?"** A `CLAUDE.md` that has diverged from `AGENTS.md` is `FAIL`, while a
missing `CLAUDE.md` is `SKIP`. The copy is more dangerous than the absence,
because it silently feeds a second agent different rules. A missing stop hook is
only `WARN` — a strong practice, not a hard requirement.

**`WARN` never blocks**, so a team can adopt this incrementally instead of
bouncing off a wall of red on day one. A tool that fails your build the first time
you run it gets uninstalled the first time you run it.

### 3. `SKIP` is excluded from the score entirely

Not counted in the numerator *or* the denominator. A repo that does not use MCP is
not penalised for having no `mcp.json`. Scoring absence-of-a-thing-you-don't-use
as a defect trains people to ignore the score.

### 4. `--fix` performs additive repairs only, and refuses at runtime

Creating an absent `CLAUDE.md` symlink is safe. Replacing an existing regular
`CLAUDE.md` is not — that destroys something a human wrote. Pruning
`.secrets.baseline` is not — marking something "not a secret" is a human
judgement.

```python
return ("refused", f"{dest_rel}: exists; editing it is not an additive repair")
```

This is the trust ladder encoded in the product rather than promised in prose. The
tool self-limits to the rung it has earned, on someone else's repository. A
refusal is not an error and does not change the exit code.

### 5. A check that cannot be sure must never block a merge

Detection methods that are heuristic say so, and resolve to `WARN`. `PB-M9-02`
(loop exits 0 only on green) `FAIL`s only on an unconditional top-level `exit 0`
with no test command present; when a test command exists but the guard cannot be
determined, it `WARN`s.

Same rule for the tool's own bugs: if a check raises an exception, the runner
catches it and returns `WARN`, not `FAIL`. An escaped exception is a bug in *our*
check, not a defect in the audited repo — failing someone else's build over our
crash claims authority the tool has not earned.

---

## What I learned building it

**A gate that cannot fail is not a gate.** The first push to this repo went green
— against a CLI stub that exits 1. GitHub Actions runs steps under `bash -e` but
*not* `pipefail`, so `check . | tee report` reported `tee`'s exit status and
swallowed the failure. The self-audit enforcing the entire dogfooding claim was
decorative for one commit.

That is the tool's own thesis, landing on the tool. Green CI is only evidence if
you have watched it go red.

**Config transfers; its state does not.** The pre-commit config here was ported
verbatim from an earlier project. That project's `.secrets.baseline` carried two
unaudited entries. Copying a guardrail does not copy the discipline of maintaining
it — which is why `PB-W5-03` checks the baseline's contents, not its existence.

**Documented numbers drift.** The cross-repo evidence in this repo claimed 90%/14%
for two PRs after it stopped being true — adding a check changed both
denominators. Found only by re-running the evidence instead of trusting it. Every
number in a report needs a command attached.

**Autonomy is calibrated per task class, not granted globally.** Fourteen of the
sixteen checks were written by an agent working autonomously — pure functions,
fixture-tested, cheap to revert. The credential-detection check and every `--fix`
mutation path stayed human-reviewed, because a false negative there ships a leaked
credential or writes to someone else's repo. Same session, same agent, different
rung.

---

## Repository layout

```
AGENTS.md                  house rules — CLAUDE.md symlinks to it
specs/playbook-doctor.md   the authoritative contract, written before the code
playbook_doctor/checks/    one module per check, independently testable
templates/                 what `init` scaffolds
PROMPT.md                  loop goal, re-fed verbatim each pass
IMPLEMENTATION_PLAN.md     backlog — one task per pass
NOTES.md                   journal — how a fresh session inherits context
docs/capstone/             playbook, techniques, critical review, evidence
```

## License

MIT
