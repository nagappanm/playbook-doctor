"""PB-W5-03 — .secrets.baseline has no unaudited entries.

The 'secret' values here are obvious test literals, and the baseline is built in
tmp_path rather than committed, so this repo's own detect-secrets never sees them.
"""

from __future__ import annotations

import json

from playbook_doctor.checks.pb_w5_03 import check
from playbook_doctor.registry import Status


def _baseline(tmp_path, results):
    (tmp_path / ".secrets.baseline").write_text(json.dumps({"results": results}))
    return tmp_path


def test_pass_when_every_entry_is_audited(tmp_path):
    results = {"app.py": [{"type": "Secret Keyword", "is_secret": False}]}
    assert check(_baseline(tmp_path, results)).status is Status.PASS


def test_fail_counts_unaudited_entries(tmp_path):
    results = {
        "app.py": [{"is_secret": None}, {"is_secret": True}],
        "conf.py": [{"type": "Base64"}],  # is_secret absent → unaudited
    }
    verdict = check(_baseline(tmp_path, results))
    assert verdict.status is Status.FAIL
    assert "2 unaudited" in (verdict.detail or "")


def test_fail_when_unparseable(tmp_path):
    (tmp_path / ".secrets.baseline").write_text("{ not valid json")
    verdict = check(tmp_path)
    assert verdict.status is Status.FAIL
    assert "unparseable" in (verdict.detail or "")


def test_warn_when_baseline_absent(tmp_path):
    assert check(tmp_path).status is Status.WARN
