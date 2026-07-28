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

REPO_ROOT = Path(__file__).resolve().parent.parent


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


def test_cli_exits_one_when_a_check_fails(tmp_path, capsys):
    # A bare directory is missing AGENTS.md and the pre-commit config, so real
    # checks FAIL and the CLI must surface that as exit 1.
    assert main(["check", str(tmp_path)]) == 1
    assert "score" in capsys.readouterr().out


def test_cli_exits_zero_on_this_repo(capsys):
    # End-to-end dogfood: playbook-doctor passes its own audit (no FAIL).
    assert main(["check", str(REPO_ROOT)]) == 0
    assert "score" in capsys.readouterr().out


def test_cli_json_flag_emits_only_json(tmp_path, capsys):
    main(["check", str(tmp_path), "--json"])
    json.loads(capsys.readouterr().out)  # raises if anything else leaked to stdout


def test_cli_bad_path_is_a_usage_error(tmp_path, capsys):
    missing = tmp_path / "nope"
    assert main(["check", str(missing)]) == 2
    assert "not a directory" in capsys.readouterr().err
