"""PB-W6-01 — spec artefacts present."""

from __future__ import annotations

import pytest

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


@pytest.mark.parametrize("directory", ["spec", "docs/spec", ".specify"])
def test_pass_on_each_widened_directory(tmp_path, directory):
    target = tmp_path / directory
    target.mkdir(parents=True)
    (target / "contract.md").write_text("# Spec\n")
    assert check(tmp_path).status is Status.PASS


@pytest.mark.parametrize("filename", ["SPEC.md", "spec.md", "spec-driven.md", "product-spec.md"])
def test_pass_on_a_root_spec_document(tmp_path, filename):
    (tmp_path / filename).write_text("# The spec\n")
    assert check(tmp_path).status is Status.PASS


def test_warn_when_specs_dir_is_empty(tmp_path):
    (tmp_path / "specs").mkdir()
    assert check(tmp_path).status is Status.WARN


def test_warn_when_no_spec_artefact(tmp_path):
    (tmp_path / "README.md").write_text("# Just a readme\n")
    assert check(tmp_path).status is Status.WARN


def test_an_unrelated_markdown_file_does_not_count(tmp_path):
    (tmp_path / "special.md").write_text("# not a spec\n")
    assert check(tmp_path).status is Status.WARN
