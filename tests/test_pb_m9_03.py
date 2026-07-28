"""PB-M9-03 — loop works on a branch or worktree."""

from __future__ import annotations

import pytest

from playbook_doctor.checks.pb_m9_03 import check
from playbook_doctor.registry import Status


def _loop(tmp_path, text, name="loop.sh"):
    (tmp_path / name).write_text(text)
    return tmp_path


@pytest.mark.parametrize(
    "line",
    [
        "git worktree add ../wt HEAD\n",
        "git checkout -b run-$(date +%s)\n",
        "git switch -c ralph-loop\n",
    ],
)
def test_pass_on_each_isolation_primitive(tmp_path, line):
    assert check(_loop(tmp_path, line)).status is Status.PASS


def test_warn_when_no_isolation(tmp_path):
    verdict = check(_loop(tmp_path, "#!/bin/bash\nwhile true; do run; done\n"))
    assert verdict.status is Status.WARN
    assert "isolate" in (verdict.detail or "")


def test_skip_when_no_loop_script(tmp_path):
    assert check(tmp_path).status is Status.SKIP
