from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path


def test_generate_run_summary_writes_md_and_json():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "run_summary"
        step_summary = Path(tmp) / "step_summary.md"
        cmd = [
            "python3",
            "scripts/generate_run_summary.py",
            "--output-dir",
            str(out_dir),
            "--repo",
            "owner/repo",
            "--workflow",
            "Workbench CI",
            "--run-id",
            "123456789",
            "--run-attempt",
            "2",
            "--head-sha",
            "abcdef1234",
            "--job-status",
            "failure",
            "--failure-taxonomy",
            "script",
            "--failing-job",
            "python-smoke",
            "--failing-step",
            "Unit tests",
            "--next-owner",
            "lane-workbench",
        ]
        env = os.environ.copy()
        env["GITHUB_STEP_SUMMARY"] = str(step_summary)
        result = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr

        json_path = out_dir / "run_summary.json"
        md_path = out_dir / "run_summary.md"
        assert json_path.exists()
        assert md_path.exists()
        assert step_summary.exists()
        step_summary_content = step_summary.read_text(encoding="utf-8")
        assert "Run Summary Contract (cp2.run_summary.v1)" in step_summary_content
        assert "## Incident Header" in step_summary_content

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "cp2.run_summary.v1"
        assert payload["terminal_class"] == "hard_block"
        assert payload["run_attempt"] == 2
