"""PB-W5-05 — CI runs guardrail scans."""

from __future__ import annotations

from playbook_doctor.checks.pb_w5_05 import check
from playbook_doctor.registry import Status


def _workflow(tmp_path, text, name="ci.yml"):
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / name).write_text(text)
    return tmp_path


def test_pass_when_ci_runs_semgrep(tmp_path):
    text = "jobs:\n  scan:\n    steps:\n      - uses: returntocorp/semgrep-action@v1\n"
    verdict = check(_workflow(tmp_path, text, name="semgrep.yml"))
    assert verdict.status is Status.PASS
    assert "semgrep" in (verdict.detail or "")


def test_pass_when_ci_runs_lint_or_format(tmp_path):
    text = "jobs:\n  lint:\n    steps:\n      - run: ruff check . && black --check .\n"
    verdict = check(_workflow(tmp_path, text))
    assert verdict.status is Status.PASS
    assert "black" in (verdict.detail or "") and "ruff" in (verdict.detail or "")


def test_warn_when_ci_runs_no_guardrail(tmp_path):
    text = "jobs:\n  test:\n    steps:\n      - run: pytest -q\n      - run: make deploy\n"
    assert check(_workflow(tmp_path, text)).status is Status.WARN


def test_a_word_that_merely_contains_a_tool_name_does_not_count(tmp_path):
    # "blacklist" must not fire the "black" signal.
    text = "jobs:\n  build:\n    steps:\n      - run: update_blacklist.sh\n"
    assert check(_workflow(tmp_path, text)).status is Status.WARN


def test_skip_when_no_ci(tmp_path):
    assert check(tmp_path).status is Status.SKIP


def test_skip_when_workflows_dir_is_empty(tmp_path):
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    assert check(tmp_path).status is Status.SKIP
