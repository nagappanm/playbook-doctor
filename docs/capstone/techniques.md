# Part 2 — Advanced techniques applied

**Nagappan M · Week 8 capstone · `playbook-doctor`**

The brief asks for three. All five are documented here because each one produced a
real artefact during the build rather than being staged for the writeup. If three
are wanted, take **1, 2, and 3** — those are the ones where something was actually
caught, refused, or changed course.

Every claim below names a file, a command, or a commit a reviewer can open.

---

## 1. Progressive validation — the guardrails caught three things

Guardrails were installed in the **first commit**, before any feature code
existed. That ordering is why the catches below are real rather than
reconstructed.

### Catch 1 — a planted credential was refused

A fake-but-real-format AWS key pair was committed on purpose to test whether the
ported Week 5 config actually bites in a new repo:

```
black....................................................................Passed
ruff (legacy alias)......................................................Passed
Detect secrets...........................................................Failed
- hook id: detect-secrets

ERROR: Potential secrets about to be committed to git repo!
Secret Type: AWS Access Key             Location: leak_demo.py:2
Secret Type: Base64 High Entropy String Location: leak_demo.py:2
Secret Type: Secret Keyword             Location: leak_demo.py:2
```

The commit was refused. `git log --all -p | grep` confirms the key never entered
history at any point — stopped before object creation, not committed and reverted.

### Catch 2 — the evidence file documenting catch 1 was itself blocked

Even redacted, the `AWS_SECRET_ACCESS_KEY = ...` line tripped the `Secret Keyword`
detector. A true false positive. Resolved with `pragma: allowlist secret` — the
Week 5 Part 3 technique: annotate the one line, in the open, where a reviewer can
challenge it. **The hook was never weakened or skipped.**

### Catch 3 — a CI gate that could not fail

The most valuable catch, and it was my own mistake. The first push went **green**.
It should not have: the self-audit step runs the CLI, which at that point was a
stub exiting 1. GitHub Actions runs steps under `bash -e` but *not* `pipefail`, so
`playbook-doctor check . | tee report` reported `tee`'s exit status and swallowed
the failure whole.

**The gate enforcing the entire dogfooding claim was decorative for one commit.**

Fixed with explicit `shell: bash` + `set -o pipefail`. Both runs remain in CI
history as the before/after:

```
completed  failure  fix(ci): make the self-audit gate actually able to fail
completed  success  docs(spec): author the check catalog...   ← the false green
```

The symmetry is the point: this tool exists to catch *config that looks
configured*, and my own CI was config that looked configured.

**Evidence:** `docs/capstone/evidence/01-progressive-validation.md`, CI runs
`30310493028` (false green) and `30310647062` (honest red).

---

## 2. Trust calibration — autonomy granted per task class, never globally

The build was split by **blast radius**, not by difficulty.

| Task class | Posture | Why |
|---|---|---|
| Check modules (14 of 16) | Autonomous | Pure functions: read the filesystem, return a `Verdict`. Fixture-tested, cheap to revert, cannot mutate the repo under audit. |
| `PB-W4-02` — credential detection | **Human in the loop** | Reasons about what a secret looks like. A false negative here means a leaked credential ships. |
| `--fix` mutation paths | **Human in the loop** | The only code that writes to someone else's repository. |
| The spec | **Human-authored** | The contract the agent codes against. Delegating the contract and the implementation to the same agent means nothing independent is left to check the work. |

Both gated items were marked in the backlog *before* the loop ran, not after:

```markdown
- [x] **`PB-W4-02` no inline credentials — HUMAN REVIEW REQUIRED,
      do not implement autonomously**
- [x] `--fix` wired to additive repairs only, per spec §6 — HUMAN REVIEW REQUIRED
```

**The calibration is encoded in the product, not just the process.** `--fix`
performs additive repairs only and refuses anything else at runtime:

```python
# playbook_doctor/scaffold.py
return ("refused", f"{dest_rel}: exists; editing it is not an additive repair")
```

It will create an absent `CLAUDE.md` symlink. It will **not** replace an existing
regular `CLAUDE.md` — that destroys something a human wrote. It will **not** prune
`.secrets.baseline`, because marking something "not a secret" is a human
judgement. The tool self-limits to the trust rung it has earned, on someone else's
repo.

**Evidence:** `specs/playbook-doctor.md` §6, `playbook_doctor/scaffold.py`,
`IMPLEMENTATION_PLAN.md`.

---

## 3. Context handoff — the repo is the memory, not the transcript

Each loop pass starts with an empty context window. Everything needed to resume
lives in four files, re-read every pass:

| File | Role |
|---|---|
| `PROMPT.md` | The goal, re-fed verbatim each iteration |
| `IMPLEMENTATION_PLAN.md` | The backlog — pick **one** task per pass |
| `NOTES.md` | The journal — what the last pass learned |
| `AGENTS.md` | House rules and verification commands |

`NOTES.md` is what makes a session disposable. Concrete example — a later pass
never re-derived any of this:

> - Black inferred a `py3.15` target against a 3.14 interpreter and failed its
>   AST-equivalence safety check. Fixed by pinning `target-version = ["py310"]`.
> - `pytest` exits **5** on an empty suite, which fails the stop hook every turn.
> - The reference `.secrets.baseline` carries **2 unaudited entries**. The config
>   transferred; its state did not.

Three environment traps that each cost real time to find once, and zero time
after. The orientation command is `git log --oneline -20` plus `NOTES.md` — history
and journal, not a codebase tour.

**Evidence:** `PROMPT.md`, `NOTES.md`, `IMPLEMENTATION_PLAN.md`.

---

## 4. Token efficiency — an explicit do-not-read list

`AGENTS.md` names what to skip, so context is not spent on generated noise:

```markdown
## Do not read

- `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`
- `tests/fixtures/**` — read only the fixture for the check you are working on
```

The fixtures line matters most: 16 checks each carry passing and failing fixtures,
so a naive "read the tests directory" burns the window on 30+ irrelevant files.

Reinforced structurally — **one check per pass**. Each check is an independent pure
function, so a pass reads one spec entry, one module, one fixture pair. The
architecture is what makes the small context window sufficient; the instruction
alone would not be.

**Evidence:** `AGENTS.md` § Do not read, `PROMPT.md` rule 1.

---

## 5. Git hygiene — atomic commits as agent-navigable history

Every commit is one logical change with a conventional prefix and a body
explaining *why*:

```
7c8a373 feat: add PB-W5-05 — credit CI-side guardrail scans (#4)
0a43e7b feat: widen PB-W6-01 spec-artefact search (cross-repo calibration) (#3)
db7cd9b feat: wire check --fix to additive repairs only (spec §6) (#2)
9ea207e playbook-doctor: engine, full check catalog, init scaffolder (U3–U6) (#1)
a1fad23 fix(ci): make the self-audit gate actually able to fail
22385d5 docs(spec): author the check catalog and loop state before implementation
609daf6 chore: add Makefile and U1 invariant tests
131bad6 docs(capstone): capture progressive-validation evidence
af083b3 chore: bootstrap playbook-doctor with guardrails live from commit one
```

The order is the argument: guardrails (`af083b3`) before spec (`22385d5`) before
engine (`9ea207e`). `git log --reverse` reads as the method. Agent work landed as
**four reviewable PRs**, each independently CI-green, so the diff was inspectable
per unit instead of as one 2,600-line drop.

**One honest defect:** the four earliest commits are authored `Apple` — the
machine's default git identity, never configured. Caught while preparing the
submission and fixed going forward (`git config --global user.name`), but the
existing commits are left as-is. Rewriting published history to make a capstone
look tidier is the wrong trade.

**Evidence:** `git log --oneline`, PRs #1–#4.
