from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_artifact_retention_policy.py"
    spec = importlib.util.spec_from_file_location(
        "check_artifact_retention_policy_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_artifact_retention_policy_script")
    sys.modules["check_artifact_retention_policy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_artifact_retention_policy_script", None)
        else:
            sys.modules["check_artifact_retention_policy_script"] = original


def test_check_workflow_content_passes_for_mapped_artifacts():
    module = _load_module()
    content = """
steps:
  - name: Upload attestation verify report
    uses: actions/upload-artifact@x
    with:
      name: attestation-verify-report
      path: docs/reports/attestation_verify_report.json
      retention-days: 90
  - name: Upload run summary artifact
    uses: actions/upload-artifact@x
    with:
      name: run-summary-smoke
      path: run_summary/run_summary.json
      retention-days: 7
""".strip()
    issues = module.check_workflow_content(content, "example.yml")
    assert issues == []


def test_check_workflow_content_fails_when_retention_missing():
    module = _load_module()
    content = """
steps:
  - name: Upload eval artifacts
    uses: actions/upload-artifact@x
    with:
      name: nightly-eval-report
      path: docs/reports/eval_report.json
""".strip()
    issues = module.check_workflow_content(content, "missing.yml")
    assert any("missing numeric retention-days" in issue for issue in issues)


def test_check_workflow_content_fails_when_retention_wrong():
    module = _load_module()
    content = """
steps:
  - name: Upload policy
    uses: actions/upload-artifact@x
    with:
      name: workflow-policy-reports
      path: docs/reports/workflow_pinning_audit.json
      retention-days: 7
""".strip()
    issues = module.check_workflow_content(content, "wrong.yml")
    assert any("retention-days=7 expected=30" in issue for issue in issues)


def test_check_workflow_content_fails_for_unmapped_artifact():
    module = _load_module()
    content = """
steps:
  - name: Upload other
    uses: actions/upload-artifact@x
    with:
      name: unknown-artifact
      path: out.txt
      retention-days: 7
""".strip()
    issues = module.check_workflow_content(content, "unknown.yml")
    assert any("not mapped to a retention class" in issue for issue in issues)
