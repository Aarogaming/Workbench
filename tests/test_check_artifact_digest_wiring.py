from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_artifact_digest_wiring.py"
    spec = importlib.util.spec_from_file_location(
        "check_artifact_digest_wiring_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_artifact_digest_wiring_script")
    sys.modules["check_artifact_digest_wiring_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_artifact_digest_wiring_script", None)
        else:
            sys.modules["check_artifact_digest_wiring_script"] = original


def test_check_nightly_workflow_passes_when_wired():
    module = _load_module()
    content = """
steps:
  - name: Generate artifact digest report
    run: |
      python3 scripts/generate_artifact_digest_report.py \
        --artifact eval_report_json=docs/reports/eval_report.json \
        --artifact eval_report_md=docs/reports/eval_report.md \
        --output docs/reports/artifact_digest_report.json
  - name: Upload eval artifacts
    uses: actions/upload-artifact@x
    with:
      path: docs/reports/artifact_digest_report.json
""".strip()
    issues = module.check_nightly_workflow(content, "nightly.yml")
    assert issues == []


def test_check_nightly_workflow_fails_when_digest_report_missing():
    module = _load_module()
    content = """
steps:
  - name: Upload eval artifacts
    uses: actions/upload-artifact@x
    with:
      path: docs/reports/eval_report.json
""".strip()
    issues = module.check_nightly_workflow(content, "nightly.yml")
    assert any("missing step 'Generate artifact digest report'" in issue for issue in issues)


def test_check_verify_workflow_passes_when_wired():
    module = _load_module()
    content = """
steps:
  - name: Verify artifact digests
    run: |
      python3 scripts/verify_artifact_digests.py \
        --report attested_artifacts/artifact_digest_report.json \
        --artifact eval_report_json=attested_artifacts/eval_report.json \
        --artifact eval_report_md=attested_artifacts/eval_report.md \
        --json-out docs/reports/artifact_digest_verify_report.json
  - name: Upload attestation verify report
    uses: actions/upload-artifact@x
    with:
      path: docs/reports/artifact_digest_verify_report.json
""".strip()
    issues = module.check_verify_workflow(content, "verify.yml")
    assert issues == []


def test_check_verify_workflow_fails_when_verify_step_missing():
    module = _load_module()
    content = """
steps:
  - name: Upload attestation verify report
    uses: actions/upload-artifact@x
""".strip()
    issues = module.check_verify_workflow(content, "verify.yml")
    assert any("missing step 'Verify artifact digests'" in issue for issue in issues)
