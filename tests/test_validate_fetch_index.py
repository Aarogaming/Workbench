from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "validate_fetch_index.py"
    spec = importlib.util.spec_from_file_location("validate_fetch_index_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("validate_fetch_index_script")
    sys.modules["validate_fetch_index_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("validate_fetch_index_script", None)
        else:
            sys.modules["validate_fetch_index_script"] = original


def _valid_payload() -> dict[str, object]:
    return {
        "schema_version": "cp2.fetch_index.v1",
        "generated_at_utc": "2026-02-17T02:49:44Z",
        "repo": "owner/repo",
        "run_id": "246813579",
        "incident_id": "CUTOVER-2026-02-15-IMPLEMENT",
        "run_attempt": 2,
        "dry_run": True,
        "artifacts": [
            {
                "class": "eval",
                "artifact_name": "nightly-eval-report",
                "status": "dry-run",
                "dir": "artifacts/cutover/x/y/eval",
            }
        ],
    }


def test_validate_payload_accepts_valid_index():
    module = _load_module()
    issues = module.validate_payload(_valid_payload())
    assert issues == []


def test_validate_payload_rejects_bad_status():
    module = _load_module()
    payload = _valid_payload()
    artifacts = payload["artifacts"]
    assert isinstance(artifacts, list)
    assert isinstance(artifacts[0], dict)
    artifacts[0]["status"] = "unknown"
    issues = module.validate_payload(payload)
    assert any("status must be one of" in issue for issue in issues)


def test_main_no_discovered_paths_passes(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_discover_paths", lambda root, discover_root: [])
    monkeypatch.setattr(sys, "argv", ["validate_fetch_index.py"])
    assert module.main() == 0


def test_validate_path_invalid_json_fails():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "index.json"
        path.write_text("{not-json}\n", encoding="utf-8")
        issues = module.validate_path(path)
        assert any("invalid JSON" in issue for issue in issues)


def test_validate_path_reads_file():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "index.json"
        path.write_text(json.dumps(_valid_payload()) + "\n", encoding="utf-8")
        assert module.validate_path(path) == []
