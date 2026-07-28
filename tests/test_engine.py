"""Engine tests for U3: the Verdict model, scoring, isolation, and rendering.

These exercise the framework, not any individual check (those arrive in U4 with
their own fixtures). The invariants under test are the ones the whole catalog
rests on: SKIP is excluded from the score, only FAIL blocks, and a check that
raises is contained rather than aborting the audit.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from playbook_doctor import report
from playbook_doctor.cli import main
from playbook_doctor.registry import Check, Status, Verdict, exit_code, score


def _v(status: Status, check_id: str = "PB-W3-01", week: str = "W3") -> Verdict:
    detail = None if status is Status.PASS else "because"
    return Verdict(check_id, week, "title", status, detail)


def test_score_excludes_skip_from_both_sides():
    verdicts = [_v(Status.PASS), _v(Status.WARN), _v(Status.SKIP)]
    # 1 PASS / (1 PASS + 1 WARN); the SKIP is invisible to the ratio.
    assert score(verdicts) == pytest.approx(0.5)


def test_score_is_none_when_nothing_is_scored():
    assert score([]) is None
    assert score([_v(Status.SKIP), _v(Status.SKIP)]) is None


def test_only_fail_drives_a_nonzero_exit_code():
    assert exit_code([_v(Status.PASS), _v(Status.WARN), _v(Status.SKIP)]) == 0
    assert exit_code([_v(Status.PASS), _v(Status.FAIL)]) == 1


def test_a_raising_check_is_contained_as_a_warn():
    def boom(_root: Path) -> Verdict:
        raise RuntimeError("kaboom")

    verdict = Check("PB-X", "W9", "explodes", boom).run(Path("."))
    assert verdict.status is Status.WARN
    assert verdict.id == "PB-X"
    assert "RuntimeError" in (verdict.detail or "")
    assert "kaboom" in (verdict.detail or "")


def test_json_render_is_valid_and_shaped():
    verdicts = [_v(Status.PASS), _v(Status.FAIL, "PB-W5-01", "W5")]
    doc = json.loads(report.render_json(verdicts))
    assert doc["score"] == pytest.approx(0.5)
    assert doc["summary"]["PASS"] == 1 and doc["summary"]["FAIL"] == 1
    assert [c["id"] for c in doc["checks"]] == ["PB-W3-01", "PB-W5-01"]


def test_console_render_groups_by_week_and_summarises():
    verdicts = [_v(Status.PASS, "PB-M9-01", "M9"), _v(Status.PASS, "PB-W3-01", "W3")]
    out = report.render_console(verdicts)
    # W3 sorts before M9 despite 'M' < 'W' lexically.
    assert out.index("W3") < out.index("M9")
    assert "score 100%" in out


def test_cli_check_on_a_clean_dir_exits_zero(tmp_path, capsys):
    # No checks are registered yet in U3, so an empty audit is a clean audit.
    assert main(["check", str(tmp_path)]) == 0
    assert "score" in capsys.readouterr().out


def test_cli_json_flag_emits_only_json(tmp_path, capsys):
    assert main(["check", str(tmp_path), "--json"]) == 0
    json.loads(capsys.readouterr().out)  # raises if anything else leaked to stdout


def test_cli_bad_path_is_a_usage_error(tmp_path, capsys):
    missing = tmp_path / "nope"
    assert main(["check", str(missing)]) == 2
    assert "not a directory" in capsys.readouterr().err
