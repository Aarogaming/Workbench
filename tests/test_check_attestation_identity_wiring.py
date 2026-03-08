from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_attestation_identity_wiring.py"
    spec = importlib.util.spec_from_file_location(
        "check_attestation_identity_wiring_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_attestation_identity_wiring_script")
    sys.modules["check_attestation_identity_wiring_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_attestation_identity_wiring_script", None)
        else:
            sys.modules["check_attestation_identity_wiring_script"] = original


def test_check_workflow_content_passes_when_wired():
    module = _load_module()
    content = """
steps:
  - name: Verify artifact attestations
    run: |
      python3 scripts/verify_attestations.py \
        --repo "${{ github.repository }}" \
        --signer-workflow "${{ github.repository }}/.github/workflows/nightly-evals.yml" \
        --predicate-type "https://slsa.dev/provenance/v1"
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert issues == []


def test_check_workflow_content_fails_when_step_missing():
    module = _load_module()
    content = """
steps:
  - name: Other Step
    run: echo "x"
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing step 'Verify artifact attestations'" in issue for issue in issues)


def test_check_workflow_content_fails_when_signer_workflow_missing():
    module = _load_module()
    content = """
steps:
  - name: Verify artifact attestations
    run: |
      python3 scripts/verify_attestations.py \
        --repo "${{ github.repository }}" \
        --predicate-type "https://slsa.dev/provenance/v1"
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing expected token '--signer-workflow" in issue for issue in issues)


def test_check_workflow_content_fails_when_predicate_type_missing():
    module = _load_module()
    content = """
steps:
  - name: Verify artifact attestations
    run: |
      python3 scripts/verify_attestations.py \
        --repo "${{ github.repository }}" \
        --signer-workflow "${{ github.repository }}/.github/workflows/nightly-evals.yml"
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing expected token '--predicate-type" in issue for issue in issues)
