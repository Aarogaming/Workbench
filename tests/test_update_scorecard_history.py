from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_update_history_appends_entries_and_renders_markdown(tmp_path):
    root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "scorecard_threshold_audit.json"
    history_json = tmp_path / "scorecard_history.json"
    history_md = tmp_path / "scorecard_history.md"

    audit_path.write_text(
        json.dumps(
            {
                "generated_utc": "2026-02-15T00:00:00Z",
                "project": "github.com/example/repo",
                "available": True,
                "gate": {"pass": True, "reasons": []},
                "scorecard": {
                    "score": 8.2,
                    "check_scores": {"Dangerous-Workflow": 10.0},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/update_scorecard_history.py",
            "--audit-json",
            str(audit_path),
            "--history-json",
            str(history_json),
            "--history-md",
            str(history_md),
            "--max-entries",
            "10",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    payload = json.loads(history_json.read_text(encoding="utf-8"))
    assert len(payload["entries"]) == 1
    assert payload["entries"][0]["project"] == "github.com/example/repo"
    md = history_md.read_text(encoding="utf-8")
    assert "Scorecard History" in md
    assert "8.20" in md


def test_update_history_dedupes_by_generated_and_project(tmp_path):
    root = Path(__file__).resolve().parents[1]
    audit_path = tmp_path / "scorecard_threshold_audit.json"
    history_json = tmp_path / "scorecard_history.json"
    history_md = tmp_path / "scorecard_history.md"

    audit_path.write_text(
        json.dumps(
            {
                "generated_utc": "2026-02-15T00:00:00Z",
                "project": "github.com/example/repo",
                "available": False,
                "gate": {"pass": True, "reasons": []},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    history_json.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "generated_utc": "2026-02-15T00:00:00Z",
                        "project": "github.com/example/repo",
                        "available": True,
                        "gate_pass": False,
                        "score": 1.0,
                        "check_scores": {},
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/update_scorecard_history.py",
            "--audit-json",
            str(audit_path),
            "--history-json",
            str(history_json),
            "--history-md",
            str(history_md),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    payload = json.loads(history_json.read_text(encoding="utf-8"))
    assert len(payload["entries"]) == 1
    assert payload["entries"][0]["available"] is False
