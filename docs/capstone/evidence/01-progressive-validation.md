# Evidence — Progressive validation

**Technique:** Progressive validation — how the guardrails caught something and
redirected the work.

**When:** During U1, before any feature code existed. This ordering was
deliberate: guardrails installed *first* means the catch is real rather than
reconstructed for the writeup.

## What was tried

A file containing a well-known fake AWS credential pair was staged and committed
on purpose, to test whether the ported Week 5 config actually bites in a brand-new
repo:

```python
# leak_demo.py
AWS_ACCESS_KEY_ID = "AKIA...REDACTED..."       # pragma: allowlist secret
AWS_SECRET_ACCESS_KEY = "wJal...REDACTED..."   # pragma: allowlist secret
```

Keys are redacted here; the unredacted terminal output is in the screenshot.

**This file was itself blocked on first commit.** Even redacted, the
`AWS_SECRET_ACCESS_KEY = ...` line tripped the `Secret Keyword` detector — a true
false positive. It is resolved above with `pragma: allowlist secret`, the Week 5
Part 3 technique: annotate the specific false positive, never weaken or skip the
hook. Real secrets in this repo stay blocked; this one line is exempted, in the
open, where a reviewer can see and challenge it.

## What happened

```
black....................................................................Passed
ruff (legacy alias)......................................................Passed
ruff format..............................................................Passed
Detect secrets...........................................................Failed
- hook id: detect-secrets
- exit code: 1

ERROR: Potential secrets about to be committed to git repo!

Secret Type: AWS Access Key            Location: leak_demo.py:2
Secret Type: Base64 High Entropy String Location: leak_demo.py:2
Secret Type: Secret Keyword             Location: leak_demo.py:2

semgrep..................................................................Passed
```

The commit was **refused**. `git log` afterwards still showed only the bootstrap
commit, and `git log --all -p | grep` confirmed the key never entered history at
any point — it was stopped before object creation, not committed and then
reverted.

## How it redirected the work

Three things changed as a result:

1. **The bypass got caught.** The bootstrap commit itself had been made with
   `core.hooksPath=/dev/null` to avoid stalling on a first-run semgrep rule
   download. That shortcut meant the guardrails were configured but unproven.
   Running this test immediately afterwards is what turned "configured" into
   "verified" — and it is the same failure mode `PB-W5-04` exists to catch: config
   that looks active and is not.
2. **It became a product requirement.** This is precisely the class of defect
   `playbook-doctor` audits for, so `PB-W5-03` (baseline has no unaudited entries)
   and `PB-W5-04` (stop hook configured *and non-empty*) were both promoted to
   blocking severity in the spec rather than advisory.
3. **The reference config was found wanting.** Auditing the Week 5 source config
   revealed its own `.secrets.baseline` carries **2 unaudited entries**. The
   config was ported verbatim as planned, but this repo's baseline was
   regenerated and audited to zero — the guardrail was inherited, its state was
   not.

## Verification

```bash
git log --oneline                              # bootstrap commit only
git log --all -p | grep -c AKIA...             # 0
```
