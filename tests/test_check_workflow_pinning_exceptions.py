from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_exceptions_review_passes_for_empty_policy(tmp_path):
    root = Path(__file__).resolve().parents[1]
    exceptions_path = tmp_path / "exceptions.json"
    report_path = tmp_path / "review.json"
    exceptions_path.write_text(
        json.dumps({"schema_version": 1, "exceptions": []}) + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/check_workflow_pinning_exceptions.py",
            "--exceptions-file",
            str(exceptions_path),
            "--json-out",
            str(report_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["reviewed_count"] == 0
    assert payload["summary"]["invalid_count"] == 0


def test_exceptions_review_fails_for_stale_entry(tmp_path):
    root = Path(__file__).resolve().parents[1]
    exceptions_path = tmp_path / "exceptions.json"
    report_path = tmp_path / "review.json"
    exceptions_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "exceptions": [
                    {
                        "id": "stale-checkout-tag",
                        "workflow": ".github/workflows/ci.yml",
                        "uses": "actions/checkout@v4",
                        "reason": "temporary migration",
                        "approved_by": "owner@example.com",
                        "approved_utc": "2026-02-15T00:00:00Z",
                        "review_by": "2099-01-01",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/check_workflow_pinning_exceptions.py",
            "--exceptions-file",
            str(exceptions_path),
            "--json-out",
            str(report_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["stale_count"] == 1
