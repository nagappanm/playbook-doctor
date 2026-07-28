# Spec — playbook-doctor

**Status:** authoritative. Implementation follows this document; where code and
spec disagree, the spec is wrong or the code is — resolve it here first.

**Written before implementation.** This is a deliberate Week 6 discipline and a
trust-calibration decision: the contract is human-authored, the check bodies are
agent-written against it.

---

## 1. Purpose

Audit a repository against the AI-engineering playbook and score its
**agent-readiness**. Each check encodes one lesson from the eight-week field
manual.

The failure mode this exists for is **config that looks configured**: an empty
`"Stop": []` hook, a `CLAUDE.md` copied instead of symlinked and since drifted, a
secrets baseline with unaudited entries. Each passes a glance and fails in
practice.

---

## 2. CLI surface

```
playbook-doctor check [PATH] [--json] [--fix]
playbook-doctor init  [PATH] [--force]
```

| Flag | Applies to | Meaning |
|---|---|---|
| `--json` | `check` | Emit machine-readable results to stdout, nothing else |
| `--fix` | `check` | Apply additive repairs only (§6), then re-run and report |
| `--force` | `init` | Overwrite existing files instead of skipping them |

`PATH` defaults to `.`.

---

## 3. The `Verdict` model

Every check returns exactly one `Verdict`:

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | Stable check ID, e.g. `PB-W3-03` |
| `week` | `str` | Source lesson, e.g. `W3`, `M9` |
| `title` | `str` | Short human label, e.g. `CLAUDE.md symlink` |
| `status` | `Status` | One of the four below |
| `detail` | `str \| None` | Why. Required for anything that is not `PASS` |

### Status

| Status | Meaning | Counts toward score | Affects exit code |
|---|---|---|---|
| `PASS` | Artefact present and conformant | yes (numerator) | no |
| `WARN` | Present but weak, or an optional artefact is absent | yes (denominator only) | no |
| `FAIL` | Required artefact missing, or **actively misleading** | yes (denominator only) | **yes** |
| `SKIP` | Not applicable to this repo | no | no |

**`FAIL` is reserved for things worse than absent.** A `CLAUDE.md` that has
diverged from `AGENTS.md` is more dangerous than no `CLAUDE.md` at all, because it
silently feeds a second agent different rules. Anything merely weak, or optional
and absent, is `WARN`.

**`WARN` never blocks.** Teams must be able to adopt this tool incrementally
rather than bouncing off a wall of red on day one.

### Score

`score = count(PASS) / count(PASS + WARN + FAIL)`. `SKIP` is excluded from both
sides — a repo that does not use MCP is not penalised for having no `mcp.json`.

---

## 4. Exit codes

| Code | When |
|---|---|
| `0` | No check returned `FAIL` |
| `1` | At least one check returned `FAIL` |
| `2` | Usage error — bad path, unreadable directory, unknown flag |

Mirrors pre-commit and standard CI convention. `2` is distinguishable so CI can
tell "the repo failed the audit" from "the tool was invoked wrongly".

---

## 5. Check catalog

Detection methods are normative. Where a method is heuristic, it says so and
resolves to `WARN`, never `FAIL` — **a check that cannot be sure must not block a
merge.**

### W2 — context management

**`PB-W2-01` · AGENTS.md within context budget · WARN**
`AGENTS.md` is loaded on every request, so its size is a recurring token cost.
PASS when ≤ 400 lines. WARN above that, reporting the actual count. SKIP when
`AGENTS.md` is absent (`PB-W3-01` owns that).
*Threshold is provisional and needs calibration against real repos.*

### W3 — AGENTS.md and cross-tool config

**`PB-W3-01` · AGENTS.md exists · FAIL**
PASS when `AGENTS.md` exists at the repo root. FAIL otherwise.

**`PB-W3-02` · AGENTS.md declares verification commands · FAIL**
Rules an agent cannot verify against are decoration. PASS when `AGENTS.md`
contains a heading matching `verif|test|check` (case-insensitive) **and** at
least one fenced code block. FAIL otherwise. SKIP when `AGENTS.md` is absent.
*Heuristic — deliberately shallow, since it cannot judge whether the commands are
the right ones.*

**`PB-W3-03` · CLAUDE.md symlinks to AGENTS.md · FAIL**

| State | Verdict |
|---|---|
| `CLAUDE.md` absent | SKIP |
| symlink resolving to `AGENTS.md` | PASS |
| symlink resolving elsewhere, or broken | FAIL |
| regular file | FAIL — **even when content is currently identical** |

Content equality today is not equality tomorrow. The copy is the defect.

### W4 — MCP

Searched in order: `.mcp.json`, `.vscode/mcp.json`, `.cursor/mcp.json`.

**`PB-W4-01` · mcp.json parses · FAIL**
SKIP when no MCP config exists — not every repo uses MCP. PASS when it parses as
JSON. FAIL when present and malformed.

**`PB-W4-02` · No inline credentials in mcp.json · FAIL**
Walk every string value. A value is a **finding** when its key matches
`token|key|secret|password|credential` (case-insensitive) and the value is a
non-empty literal that is not an environment reference (`${VAR}`, `$VAR`, or
`env:VAR`). PASS when there are no findings. FAIL listing the offending key
paths, never the values. SKIP when no MCP config exists.

### W5 — guardrails

**`PB-W5-01` · .pre-commit-config.yaml exists · FAIL**
PASS when present at repo root. FAIL otherwise.

**`PB-W5-02` · Format, lint, and secret-scan hooks all present · FAIL**
Parse the YAML and collect every `hooks[].id`. Require at least one from each
category:

| Category | Recognised ids |
|---|---|
| format | `black`, `ruff-format`, `prettier`, `gofmt`, `rustfmt` |
| lint | `ruff`, `flake8`, `eslint`, `pylint`, `golangci-lint` |
| secrets | `detect-secrets`, `gitleaks`, `trufflehog` |

PASS when all three are covered. FAIL naming the missing categories. SKIP when
the config is absent. FAIL when present and unparseable.

**`PB-W5-03` · .secrets.baseline has no unaudited entries · FAIL**
An entry under `results[*]` is **unaudited** when its `is_secret` key is absent or
`null`. WARN when the baseline is absent (a repo may scan without one). PASS at
zero unaudited. FAIL reporting the count. FAIL when present and unparseable.

**`PB-W5-04` · Stop hook configured and non-empty · WARN**
Read `hooks.Stop` from `.claude/settings.json`, then `.claude/settings.local.json`.

| State | Verdict |
|---|---|
| key absent | WARN — no stop hook |
| `[]` | WARN — **"configured but empty"** |
| entries present, none carrying a non-empty `hooks` array | WARN — "declared but runs nothing" |
| at least one entry with a command | PASS |

The empty-array case is called out separately in `detail` because it is the one
that reads as configured at a glance. Never `FAIL` — a stop hook is a strong
practice, not a hard requirement.

### W6 — spec-driven development

**`PB-W6-01` · spec artefacts present · WARN**
PASS when the repo carries a spec artefact, found as either:

- a non-empty directory among `specs/`, `spec/`, `docs/specs/`, `docs/spec/`,
  `.specify/`; or
- a root-level spec document matching `spec.md`, `specs.md`, `spec-*.md`, or
  `*-spec.md` (case-insensitive, so `SPEC.md` and `spec-driven.md` both count).

WARN otherwise. *Search paths were widened after a cross-repo audit found
spec-driven repos (e.g. spec-kit) keeping their specs outside a `specs/`
directory — as a root `spec-driven.md` and under `.specify/`. The original
`specs/`-only search under-credited them.*

**`PB-W6-02` · Every SKILL.md carries required frontmatter · FAIL**
Glob `**/SKILL.md`, excluding `.venv/`, `node_modules/`, `.git/`. Each must have
YAML frontmatter containing non-empty `name` and `description`. SKIP when the
repo has no `SKILL.md`. FAIL naming the file and missing field.

### W7 — cost control

**`PB-W7-01` · Token or cost ceiling declared · WARN**
PASS when `.claude/settings.json` declares an `env` key matching
`TOKEN|BUDGET|MAX_.*TOKENS|COST`, **or** `AGENTS.md` contains a line matching
`budget|token ceiling|max tokens|cost cap` (case-insensitive). WARN otherwise.
*The weakest check in the catalog: there is no standard for declaring a budget,
so this is advisory by construction and can never block.*

### M9 — the loop

Loop scripts are located at repo root or `scripts/`, matching `ralph.sh`,
`loop.sh`, or `*loop*.sh`. All three checks SKIP when no loop script exists.

**`PB-M9-01` · Loop caps its iterations · FAIL**
PASS when a script contains a bounded construct — `MAX_ITER`, `--max-iters`,
`for … in $(seq`, or a `while` whose condition tests a counter. FAIL when it
contains `while :` or `while true` with no counter-driven `break`. WARN when the
script parses but no determination can be made.

**`PB-M9-02` · Loop exits 0 only on a green test signal · FAIL**
The model must never be the voice that says "done". PASS when the script invokes
a test command (`pytest`, `npm test`, `go test`, `playwright`, `make test`) and
its success exit is guarded by that command's status (`&&`, `if`, or an explicit
`$?` test). FAIL when a top-level unconditional `exit 0` exists with no test
command anywhere in the script. WARN when a test command is present but the guard
cannot be determined.

**`PB-M9-03` · Loop works on a branch or worktree · WARN**
A bad night's work should be a `git reset`, not an outage. PASS when the script
mentions `git worktree`, `git checkout -b`, or `git switch -c`. WARN otherwise.

### Not covered

**Week 1** contributes no check. It is orientation — how the tools work and
getting set up — and leaves no file artefact to audit. Stated here rather than
silently omitted.

---

## 6. The `--fix` safety boundary

`--fix` performs **additive repairs only**. This is the trust ladder encoded in
the product: the tool self-limits to the rung it has earned, and it is operating
on someone else's repository.

**Permitted** — creating something that is absent:

- Create `CLAUDE.md` as a symlink to `AGENTS.md`, **only when `CLAUDE.md` does not exist**
- Scaffold an absent `AGENTS.md`, `.pre-commit-config.yaml`, or `.claude/settings.json` from `templates/`

**Refused**, with a printed explanation and no change:

- Replacing an existing regular `CLAUDE.md` with a symlink — that destroys content a human wrote
- Editing the contents of any existing file
- Pruning or auto-auditing `.secrets.baseline` — marking something "not a secret" is a human judgement
- Rewriting a loop script

A refusal is not an error. `--fix` exits on the re-run's own status; refusing to
repair something does not itself change the exit code.

---

## 7. Non-goals

- **LLM-judged checks.** Deterministic asserts are the cheapest and least
  ambiguous tier of verification; a repo auditor belongs there. A second model
  scoring `AGENTS.md` *quality* is a real idea, but it makes results noisy,
  non-reproducible, and expensive in CI.
- **Auto-remediating unsafe findings.** See §6.
- **Judging whether the declared commands are the right ones.** `PB-W3-02` checks
  that verification exists, not that it is good. That is a human review question.
- **Language- or framework-specific checks.** The catalog is about the playbook,
  not about Python or TypeScript.

---

## 8. Deferred

1. Calibrate the `PB-W2-01` line threshold against real repositories.
2. Decide whether `PB-W6-02` stays `FAIL` once more repos with skills are audited.
3. Per-repo severity overrides via config — some teams will not want
   `PB-W6-02` blocking.

**Done:** `PB-W6-01` search paths were calibrated against a five-repo audit (see
`NOTES.md`, cross-repo audit) — spec-kit kept its specs as a root `spec-driven.md`
and was under-credited. Widened to accept more spec directories and root spec
documents.
