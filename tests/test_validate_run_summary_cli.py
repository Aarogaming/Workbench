from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


def _valid_summary() -> dict[str, object]:
    return {
        "schema_version": "cp2.run_summary.v1",
        "cycle_id": "CHIMERA-V2-RESEARCH-AND-EXECUTION-2026-02-15",
        "phase": "CP4-A",
        "incident_id": "CUTOVER-2026-02-15-001",
        "terminal_class": "hard_block",
        "failure_taxonomy": "policy",
        "repo": "owner/repo",
        "workflow": "Workbench CI",
        "run_id": "123456789",
        "run_attempt": 1,
        "head_sha": "abc123",
        "failing_job": "python-smoke",
        "failing_step": "Workflow pinning audit",
        "rerun_debug_cmd": "gh run rerun 123456789 --repo owner/repo --failed --debug",
        "artifact_fetch_cmd": "bash scripts/fetch_workbench_artifacts.sh --run-id 123456789 --repo owner/repo",
        "next_owner": "lane-workbench",
        "requires_handoff_by_utc": "2026-02-15T18:30:00Z",
        "generated_at_utc": "2026-02-15T18:00:00Z",
        "missing_artifacts": [],
    }


def test_validate_run_summary_cli_multi_path_all_valid():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        valid1 = Path(tmp) / "run_summary_1.json"
        valid2 = Path(tmp) / "run_summary_2.json"
        valid1.write_text(json.dumps(_valid_summary()) + "\n", encoding="utf-8")
        valid2.write_text(json.dumps(_valid_summary()) + "\n", encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                "scripts/validate_run_summary.py",
                "--path",
                str(valid1),
                "--path",
                str(valid2),
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert f"[ok] {valid1}" in result.stdout
        assert f"[ok] {valid2}" in result.stdout


def test_validate_run_summary_cli_multi_path_mixed_failure():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        valid = Path(tmp) / "run_summary_valid.json"
        invalid = Path(tmp) / "run_summary_invalid.json"
        valid.write_text(json.dumps(_valid_summary()) + "\n", encoding="utf-8")
        invalid_payload = _valid_summary()
        invalid_payload["schema_version"] = "bad.schema"
        invalid.write_text(json.dumps(invalid_payload) + "\n", encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                "scripts/validate_run_summary.py",
                "--path",
                str(valid),
                "--path",
                str(invalid),
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert f"[ok] {valid}" in result.stdout
        assert f"[fail] {invalid}" in result.stdout
