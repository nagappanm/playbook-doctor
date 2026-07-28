# Personal AI Engineering Playbook

**Nagappan M** · QE / test automation · Week 8 capstone · 2026-07-28

Four sections, as the brief asks. Everything here is something I did during this
course, not something I intend to try.

---

## 1. My top 3 workflows

### Workflow 1 — Spec → guardrails → loop → review

The default for any non-trivial build. The order is the whole point: guardrails go
in **before** the agent runs, so a bad change is caught by a hook rather than by me
reading a diff.

```bash
/ce-plan <the thing>          # decisions, not code — writes docs/plans/*.md
# author the spec by hand, commit it
pre-commit install            # guardrails live BEFORE the first feature commit
/ce-work docs/plans/<plan>.md # agentic execution against the committed spec
/code-review                  # then a real review pass, not just green CI
```

**Why it survives the course:** the spec is the contract the agent codes against.
Writing it by hand is what leaves something independent to check the work — if the
same agent writes the contract and the implementation, nothing is left to verify
against.

### Workflow 2 — Bounded loop with the repo as memory

For work that decomposes into many similar units — sixteen check modules, a suite
of page objects, a batch of migrations.

```bash
# State lives in files, not in the transcript:
#   PROMPT.md               the goal, re-fed verbatim every pass
#   IMPLEMENTATION_PLAN.md  the backlog — ONE task per pass
#   NOTES.md                the journal — what the last pass learned
#   tests                   the only voice allowed to say "done"
while [ $i -lt $MAX_ITERS ]; do ...; done   # capped, exits 0 only on green
```

**Why:** every pass starts with a clean window, so context never rots. `NOTES.md`
is what makes a session disposable — three environment traps I hit once (Black's
target-version inference, `pytest` exiting 5 on an empty suite, a stale secrets
baseline) cost time once and zero times after.

### Workflow 3 — Cross-repo audit before touching anything

```bash
playbook-doctor check .          # what state is this repo actually in?
git log --oneline -20            # what has been happening here?
```

**Why:** the fastest way to orient in an unfamiliar repo, and it is deterministic
— no tokens, no model, no opinion. Before this course my orientation step was
"read some files and hope"; now it is a scored report naming exactly which
guardrails are missing.

---

## 2. My AGENTS.md template

Shipped as `templates/AGENTS.md` in
[playbook-doctor](https://github.com/nagappanm/playbook-doctor) — `playbook-doctor init`
scaffolds it into any repo. Deliberately short: it loads on **every** request, so
every line is a recurring token cost.

```markdown
# AGENTS.md
Guidance for AI coding agents working in this repository.

## Project Overview
<!-- One paragraph: what this is, and the one or two things an agent most
     needs to know before touching it. -->

## Setup
```bash
# install dependencies, prepare the environment
```

## Verification
Run these before considering any change complete:
```bash
# the test, lint, and format commands that gate a change.
# An agent that cannot verify its own work against these is guessing.
```

## Conventions
- <!-- commit style, branching, code layout, what an agent would otherwise
       get wrong -->

## Cautions
- <!-- what NOT to do. The highest-value section: name the irreversible or
       credential-adjacent paths that need a human. -->

## Do not read
- <!-- generated dirs, fixtures, lockfiles. Cheapest token saving available. -->
```

**Design decisions:**

- **Verification is a required section**, not optional. Rules an agent cannot
  check itself against are decoration — this is what `PB-W3-02` enforces.
- **"Cautions" earns its place** by naming what must *not* be done autonomously.
  Cheaper to state once than to review for repeatedly.
- **"Do not read"** is the cheapest token saving available and almost always
  omitted.
- **`CLAUDE.md` is a symlink to this file, never a copy.** A copy drifts and then
  silently feeds a second agent different rules. That is `PB-W3-03`, and it is
  `FAIL` severity because a drifted copy is worse than no copy.

---

## 3. My guardrails checklist

The seven things set up before an agent touches anything non-trivial. Items 1–5
are now **machine-checkable** — `playbook-doctor check .` verifies them, so the
checklist is executable rather than remembered.

| # | Guardrail | Verified by |
|---|---|---|
| 1 | `AGENTS.md` exists and declares verification commands | `PB-W3-01`, `PB-W3-02` |
| 2 | `CLAUDE.md` is a **symlink**, not a copy | `PB-W3-03` |
| 3 | `.pre-commit-config.yaml` with format + lint + **secret scan** | `PB-W5-01`, `PB-W5-02` |
| 4 | `.secrets.baseline` generated **and audited to zero** | `PB-W5-03` |
| 5 | Stop hook that runs something real — never `"Stop": []` | `PB-W5-04` |
| 6 | Work on a branch or worktree, never directly on `main` | rollback is `git reset`, not an outage |
| 7 | A test command that is the **only** signal for "done" | the model never declares completion |

**Item 4 is the one people get wrong.** Generating a baseline is easy; auditing it
is the work. The Week 5 reference config I ported from carried **2 unaudited
entries** — the config transferred, its state did not.

**Item 5 is the one I got wrong.** An empty `"Stop": []` array reads as configured
at a glance and does nothing. That is why `PB-W5-04` reports "configured but
empty" as its own distinct message.

---

## 4. My personal rules

Three commitments specific to QE and test-automation work.

### Rule 1 — A selector cache change is never merged on an agent's say-so

In `klew`, a healed or newly resolved selector arrives as a **delta PR** that a
human merges; the merge *is* the approval. Agents may propose selectors and never
silently mutate the approved cache.

**Why this and not a generic slogan:** a wrong selector does not fail loudly — it
passes against the wrong element. A test suite that is green for the wrong reason
is worse than a red one, because it actively removes the signal. Selector approval
is the one place in my work where autonomy is permanently capped at "propose".

### Rule 2 — Anything credential-adjacent stays human-reviewed, permanently

`PB-W4-02` (inline-credential detection) was the one check I refused to let the
loop write, and `--fix` refuses to prune a secrets baseline at runtime. Marking
something "not a secret" is a human judgement.

**Why:** a false negative here ships a leaked credential. This rung of the trust
ladder does not get climbed on a good track record, because the failure is
unbounded and not reversible by `git reset`.

### Rule 3 — Every number in a report has a command attached, and I re-run it

Any figure I put in front of a reviewer — a pass rate, a coverage number, a score
— carries the command that produces it, and I run that command before publishing.

**Why:** during this build my own evidence document claimed 90%/14% when the tool
actually printed 91%/25%. Correct when written, stale two PRs later. Nobody would
have caught it, and it was found only by re-running instead of trusting. In QE,
where my whole output *is* claims about whether things work, a stale number is the
job done wrong.

---

## What changed for me

Before this course, "AI-assisted" meant a long chat session and a lot of re-
explaining. Now it means **files**: a spec the agent codes against, guardrails that
bite before I review, a journal that survives the session, and a deterministic
gate that decides what merges.

The transferable idea is that trust is **calibrated per task class, never granted
globally**. Sixteen pure-function checks ran autonomously; the one that reasons
about credentials never did. That distinction — not the model, not the tool — is
what made the difference.
