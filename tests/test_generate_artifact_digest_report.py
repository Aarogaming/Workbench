from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "generate_artifact_digest_report.py"
    spec = importlib.util.spec_from_file_location(
        "generate_artifact_digest_report_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("generate_artifact_digest_report_script")
    sys.modules["generate_artifact_digest_report_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("generate_artifact_digest_report_script", None)
        else:
            sys.modules["generate_artifact_digest_report_script"] = original


def test_generate_report_produces_expected_entries(tmp_path: Path):
    module = _load_module()
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("alpha", encoding="utf-8")
    file_b.write_text("beta", encoding="utf-8")

    report, errors = module.generate_report(
        root=tmp_path,
        artifacts=["first=a.txt", "second=b.txt"],
        source="unit-test",
    )
    assert errors == []
    assert report["schema_version"] == "cp2.artifact_digest_report.v1"
    assert report["source"] == "unit-test"
    assert report["summary"]["total"] == 2
    names = [row["name"] for row in report["artifacts"]]
    assert names == ["first", "second"]
    assert all(len(row["sha256"]) == 64 for row in report["artifacts"])


def test_generate_report_reports_missing_file(tmp_path: Path):
    module = _load_module()
    report, errors = module.generate_report(
        root=tmp_path,
        artifacts=["missing=does-not-exist.txt"],
        source="unit-test",
    )
    assert report["summary"]["total"] == 0
    assert any("missing file" in item for item in errors)


def test_parse_artifact_arg_defaults_name_from_stem():
    module = _load_module()
    name, path = module._parse_artifact_arg("docs/reports/eval_report.json")
    assert name == "eval_report"
    assert path == "docs/reports/eval_report.json"
