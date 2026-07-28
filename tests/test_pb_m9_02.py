"""PB-M9-02 — loop exits 0 only on a green test signal."""

from __future__ import annotations

from playbook_doctor.checks.pb_m9_02 import check
from playbook_doctor.registry import Status


def _loop(tmp_path, text, name="loop.sh"):
    (tmp_path / name).write_text(text)
    return tmp_path


def test_pass_when_exit_is_guarded_by_a_test(tmp_path):
    assert check(_loop(tmp_path, "pytest -q && exit 0\n")).status is Status.PASS


def test_pass_when_test_guards_via_if(tmp_path):
    assert check(_loop(tmp_path, "if pytest -q; then break; fi\n")).status is Status.PASS


def test_fail_on_unconditional_exit_with_no_test(tmp_path):
    verdict = check(_loop(tmp_path, "#!/bin/bash\ndo_work\nexit 0\n"))
    assert verdict.status is Status.FAIL
    assert "without running tests" in (verdict.detail or "")


def test_warn_when_test_present_but_guard_unclear(tmp_path):
    verdict = check(_loop(tmp_path, "#!/bin/bash\npytest -q\nexit 0\n"))
    assert verdict.status is Status.WARN


def test_skip_when_no_loop_script(tmp_path):
    assert check(tmp_path).status is Status.SKIP
