# playbook-doctor

Audit a repository against the AI-engineering playbook and score its
**agent-readiness**.

A playbook is files, not folklore. If a teammate — or an agent — can clone your
repo and inherit the whole system, you have a playbook. If the knowledge lives in
one engineer's head, you have a liability. `playbook-doctor` makes that
difference a deterministic check instead of a matter of memory.

```
$ playbook-doctor check .

  W3  AGENTS.md .................. PASS
  W3  CLAUDE.md symlink .......... FAIL
      └ regular file, not → AGENTS.md (drift risk)
  W5  .secrets.baseline .......... FAIL
      └ 2 unaudited entries
  W5  stop hook .................. WARN
      └ configured but empty

  Score 6/9 — exit 1
```

## Why

Config that *looks* configured is the failure mode this tool exists for. An empty
`"Stop": []` hook, a `CLAUDE.md` that was copied instead of symlinked and has
since drifted, a secrets baseline with unaudited entries — each passes a glance
and fails in practice.

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

Exit `0` when no check fails, `1` otherwise. `WARN` never blocks.

---

*Design decisions and what building this taught me: see the Design Notes section
(added in U8).*

## License

MIT
