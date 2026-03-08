from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "verify_artifact_digests.py"
    spec = importlib.util.spec_from_file_location(
        "verify_artifact_digests_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("verify_artifact_digests_script")
    sys.modules["verify_artifact_digests_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("verify_artifact_digests_script", None)
        else:
            sys.modules["verify_artifact_digests_script"] = original


def _write_report(tmp_path: Path, name: str, target: Path, module) -> Path:
    report = {
        "schema_version": "cp2.artifact_digest_report.v1",
        "artifacts": [
            {
                "name": name,
                "path": str(target),
                "sha256": module._sha256(target),
                "size_bytes": target.stat().st_size,
            }
        ],
    }
    report_path = tmp_path / "digest_report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return report_path


def test_verify_digests_passes_when_hash_matches(tmp_path: Path):
    module = _load_module()
    subject = tmp_path / "subject.bin"
    subject.write_text("payload", encoding="utf-8")
    report_path = _write_report(tmp_path, "subject", subject, module)

    report, errors = module.verify_digests(
        root=tmp_path,
        report_path=report_path,
        artifacts=["subject=subject.bin"],
    )
    assert errors == []
    assert report["gate"]["pass"] is True
    assert report["summary"]["ok"] == 1


def test_verify_digests_fails_when_hash_mismatch(tmp_path: Path):
    module = _load_module()
    subject = tmp_path / "subject.bin"
    subject.write_text("payload", encoding="utf-8")
    report_path = _write_report(tmp_path, "subject", subject, module)
    subject.write_text("mutated", encoding="utf-8")

    report, errors = module.verify_digests(
        root=tmp_path,
        report_path=report_path,
        artifacts=["subject=subject.bin"],
    )
    assert report["gate"]["pass"] is False
    assert any("digest mismatch artifacts" in item for item in errors)


def test_verify_digests_fails_on_missing_expected_entry(tmp_path: Path):
    module = _load_module()
    subject = tmp_path / "subject.bin"
    subject.write_text("payload", encoding="utf-8")
    report_path = _write_report(tmp_path, "subject", subject, module)

    report, errors = module.verify_digests(
        root=tmp_path,
        report_path=report_path,
        artifacts=["other=subject.bin"],
    )
    assert report["gate"]["pass"] is False
    assert any("missing expected digest entries" in item for item in errors)
