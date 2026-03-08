from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


def test_fetch_workbench_artifacts_requires_incident_and_run_attempt_together():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            "bash",
            "scripts/fetch_workbench_artifacts.sh",
            "--run-id",
            "12345",
            "--repo",
            "owner/repo",
            "--incident-id",
            "CUTOVER-TEST-001",
            "--dry-run",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "--incident-id and --run-attempt must be provided together" in result.stderr


def test_fetch_workbench_artifacts_writes_index_json_in_dry_run():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "cutover"
        result = subprocess.run(
            [
                "bash",
                "scripts/fetch_workbench_artifacts.sh",
                "--run-id",
                "12345",
                "--repo",
                "owner/repo",
                "--incident-id",
                "CUTOVER-TEST-002",
                "--run-attempt",
                "3",
                "--class",
                "eval",
                "--dry-run",
                "--out-dir",
                str(out_dir),
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        index_path = out_dir / "index.json"
        assert index_path.exists()

        payload = json.loads(index_path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "cp2.fetch_index.v1"
        assert payload["repo"] == "owner/repo"
        assert payload["run_id"] == "12345"
        assert payload["incident_id"] == "CUTOVER-TEST-002"
        assert payload["run_attempt"] == 3
        assert payload["dry_run"] is True
        assert isinstance(payload["artifacts"], list)
        assert payload["artifacts"][0]["class"] == "eval"
