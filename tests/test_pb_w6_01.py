"""PB-W6-01 — specs/ exists and is non-empty."""

from __future__ import annotations

from playbook_doctor.checks.pb_w6_01 import check
from playbook_doctor.registry import Status


def test_pass_with_a_file_in_specs(tmp_path):
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "design.md").write_text("# Spec\n")
    assert check(tmp_path).status is Status.PASS


def test_pass_with_a_nested_docs_specs_directory(tmp_path):
    nested = tmp_path / "docs" / "specs"
    nested.mkdir(parents=True)
    (nested / "api.md").write_text("# API\n")
    assert check(tmp_path).status is Status.PASS


def test_warn_when_specs_dir_is_empty(tmp_path):
    (tmp_path / "specs").mkdir()
    assert check(tmp_path).status is Status.WARN


def test_warn_when_no_specs_dir(tmp_path):
    assert check(tmp_path).status is Status.WARN
