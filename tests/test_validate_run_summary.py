from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "validate_run_summary.py"
    spec = importlib.util.spec_from_file_location("validate_run_summary_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("validate_run_summary_script")
    sys.modules["validate_run_summary_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("validate_run_summary_script", None)
        else:
            sys.modules["validate_run_summary_script"] = original


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


def test_validate_summary_accepts_valid_payload():
    module = _load_module()
    issues = module.validate_summary(_valid_summary())
    assert issues == []


def test_validate_summary_rejects_noncomplete_missing_failure_fields():
    module = _load_module()
    payload = _valid_summary()
    payload["failing_step"] = ""
    issues = module.validate_summary(payload)
    assert any("failing_step" in issue for issue in issues)


def test_validate_summary_rejects_bad_timestamp_format():
    module = _load_module()
    payload = _valid_summary()
    payload["generated_at_utc"] = "2026-02-15 18:00:00"
    issues = module.validate_summary(payload)
    assert any("generated_at_utc" in issue for issue in issues)


def test_main_returns_nonzero_for_invalid_file(monkeypatch):
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        invalid = Path(tmp) / "run_summary.json"
        invalid.write_text(json.dumps({"schema_version": "bad"}) + "\n", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["validate_run_summary.py", "--path", str(invalid)])
        assert module.main() == 1
