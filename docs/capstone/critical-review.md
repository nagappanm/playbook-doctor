# Critical review of the agent's output

**Nagappan M · Week 8 capstone · Part 1, requirement 4 — "review the output
critically before finalising"**

The agent produced ~2,600 lines across four PRs: the engine, sixteen checks, the
`init` scaffolder, and the cross-repo dogfood. All four were CI-green when merged.
**Green CI is a floor, not a review.** This is what a real pass over that work
found.

Reviewed on 2026-07-28 against `specs/playbook-doctor.md`, by re-running every
claim rather than reading the summaries.

---

## Finding 1 — Undocumented behaviour in the authoritative contract

**Severity: medium. Fixed.**

The plan specified that a check raising an exception is recorded as **FAIL**. The
agent implemented **WARN**:

```python
# playbook_doctor/registry.py
except Exception as exc:
    return Verdict(..., Status.WARN, f"check raised {type(exc).__name__}: {exc}")
```

**The agent's call was better than mine.** Its docstring reasons: an escaped
exception is a bug in *our* check, not a defect in the audited repo, so failing
someone else's build on our own bug over-claims authority. That is correct, and it
is consistent with the catalog-wide rule that a check which cannot be sure must
not block.

**But the spec was never updated.** It opens with *"Status: authoritative … where
code and spec disagree, resolve it here first"* — and it was silent on exception
handling entirely. The reasoning lived only in a docstring, one refactor away from
being lost.

**Resolution:** accepted the behaviour, wrote it into spec §3 with the rationale,
and flagged that the clause was written after the fact. The decision was right;
the paper trail was missing.

**Lesson:** an agent that makes a good call and doesn't write it down has still
left you with an undocumented system. Review has to check the contract, not just
the tests.

---

## Finding 2 — Documented numbers had drifted from actual output

**Severity: medium. Fixed.**

`02-cross-repo-dogfood.md` claimed **90% / 14%**. Actual current output is
**91% / 25%**. Both figures were correct when written and went stale two PRs later
— `PB-W5-05` was added and `PB-W6-01` was widened, changing both denominators.

A reviewer running the documented command would have got different numbers than
the document claimed. On a capstone about rigour, that is expensive.

**Resolution:** re-measured, restated, and left a dated note explaining the drift
rather than silently overwriting. Added a warning that the catalog is additive, so
every new check moves both denominators.

**Lesson:** this is the same defect class the tool exists to catch — a claim that
looks verified and isn't. It surfaced only because the evidence was **re-run
instead of trusted**. Every number in a deliverable needs a command attached.

---

## Finding 3 — A gate that could not fail

**Severity: high. Fixed. My defect, not the agent's.**

The first push went green against a stub CLI that exits 1. GitHub Actions runs
steps under `bash -e` but not `pipefail`, so `check . | tee report` reported
`tee`'s status. **The self-audit — the entire dogfooding claim — was decorative.**

**Resolution:** explicit `shell: bash` + `set -o pipefail`. Both runs are left in
CI history as the before/after.

**Lesson:** green CI is only evidence if you have watched it go red. I had not.

---

## Finding 4 — Scope added beyond the spec

**Severity: low. Accepted.**

The agent introduced `PB-W5-05` (credit for CI-side guardrail scans), which I
never specified, and widened `PB-W6-01`'s search paths after a five-repo
calibration.

Both are defensible: `PB-W5-05` stops a repo that guardrails in CI from scoring as
having none, and the `PB-W6-01` widening came from real evidence (spec-kit keeps
specs as a root document, not a `specs/` directory). Unlike finding 1, **the agent
updated the spec for both** — the catalog table, detection method, and severity
are all present.

Accepted as-is. Noted because unrequested scope expansion is worth catching even
when the result is good; the check that mattered was whether it was documented,
and it was.

---

## Finding 5 — Author identity is wrong on four commits

**Severity: low. Not fixed, deliberately.**

The four earliest commits are authored `Apple` — the machine's default git
identity, never configured. Split authorship weakens the git-hygiene evidence.

**Resolution:** identity configured going forward. **Published history left
alone.** Rewriting merged commits to make a capstone look tidier is the wrong
trade — the fix is worse than the defect.

---

## What held up

Not everything needed correcting. Verified independently:

- **111 tests pass, lint clean**, run locally rather than trusting CI.
- **Every check has a passing and a failing fixture.** No check is asserted only
  in the happy direction.
- **The `--fix` refusal boundary is real.** `scaffold.py` genuinely refuses to
  replace an existing regular `CLAUDE.md` or prune `.secrets.baseline`. The
  human-in-the-loop gate is enforced in code, not just promised in prose.
- **The cross-repo findings are true positives.** `agentic-ai-engineering` really
  has no root `AGENTS.md` and no `.pre-commit-config.yaml`; both were confirmed by
  hand against the checkout.
- **The tool does not flatter itself.** Self-audit is 91%, not 100% — it reports
  its own missing token budget as a WARN rather than exempting itself.

---

## The honest summary

Four PRs, all green, and a careful review still found **two documentation defects
and one silently-broken gate**. None would have been caught by the test suite,
because none was a test failure — they were a missing spec clause, a stale number,
and a CI step that reported the wrong exit status.

That is the argument for the review step existing at all, and the reason the
trust ladder is climbed per task class rather than granted globally.
