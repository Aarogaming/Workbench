from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_scorecard_threshold.py"
    spec = importlib.util.spec_from_file_location("check_scorecard_threshold_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_scorecard_threshold_script")
    sys.modules["check_scorecard_threshold_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_scorecard_threshold_script", None)
        else:
            sys.modules["check_scorecard_threshold_script"] = original


def test_evaluate_payload_passes_policy():
    module = _load_module()
    policy = module.ScorecardPolicy(
        min_score=6.0,
        min_checks={"Dangerous-Workflow": 10.0, "Pinned-Dependencies": 8.0},
    )
    payload = {
        "score": 8.8,
        "checks": [
            {"name": "Dangerous-Workflow", "score": 10},
            {"name": "Pinned-Dependencies", "score": 9},
        ],
    }
    evaluation = module._evaluate_payload(payload, policy)
    assert evaluation.passed is True
    assert evaluation.reasons == []


def test_evaluate_payload_fails_policy():
    module = _load_module()
    policy = module.ScorecardPolicy(
        min_score=7.0,
        min_checks={"Dangerous-Workflow": 10.0},
    )
    payload = {"score": 5.5, "checks": [{"name": "Pinned-Dependencies", "score": 9}]}
    evaluation = module._evaluate_payload(payload, policy)
    assert evaluation.passed is False
    assert any("overall score" in reason for reason in evaluation.reasons)
    assert any("required check missing" in reason for reason in evaluation.reasons)


def test_cli_allow_unavailable_passes_with_missing_input_json(tmp_path):
    root = Path(__file__).resolve().parents[1]
    policy_path = tmp_path / "policy.json"
    report_path = tmp_path / "report.json"
    missing_input = tmp_path / "missing.json"
    policy_path.write_text(json.dumps({"min_score": 1.0, "min_checks": {}}) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/check_scorecard_threshold.py",
            "--project",
            "github.com/example/repo",
            "--policy-file",
            str(policy_path),
            "--input-json",
            str(missing_input),
            "--allow-unavailable",
            "--json-out",
            str(report_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["available"] is False
    assert report["gate"]["pass"] is True
