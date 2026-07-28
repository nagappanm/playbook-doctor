"""PB-M9-01 — loop caps its iterations."""

from __future__ import annotations

from playbook_doctor.checks.pb_m9_01 import check
from playbook_doctor.registry import Status


def _loop(tmp_path, text, name="loop.sh"):
    (tmp_path / name).write_text(text)
    return tmp_path


def test_pass_with_max_iter(tmp_path):
    script = (
        "#!/bin/bash\nMAX_ITER=20\n"
        "while true; do run; ((i++)); [ $i -ge $MAX_ITER ] && break; done\n"
    )
    assert check(_loop(tmp_path, script)).status is Status.PASS


def test_pass_with_seq_driven_for(tmp_path):
    assert check(_loop(tmp_path, "for i in $(seq 1 10); do run; done\n")).status is Status.PASS


def test_fail_on_bare_infinite_loop(tmp_path):
    verdict = check(_loop(tmp_path, "#!/bin/bash\nwhile true; do run; done\n"))
    assert verdict.status is Status.FAIL
    assert "no iteration cap" in (verdict.detail or "")


def test_warn_when_undetermined(tmp_path):
    verdict = check(_loop(tmp_path, "#!/bin/bash\nwhile read line; do run; done < input\n"))
    assert verdict.status is Status.WARN


def test_skip_when_no_loop_script(tmp_path):
    assert check(tmp_path).status is Status.SKIP


def test_discovers_scripts_under_scripts_dir(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ralph.sh").write_text("while true; do run; done\n")
    assert check(tmp_path).status is Status.FAIL
