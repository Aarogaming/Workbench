from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_attestation_offline_wiring.py"
    spec = importlib.util.spec_from_file_location(
        "check_attestation_offline_wiring_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_attestation_offline_wiring_script")
    sys.modules["check_attestation_offline_wiring_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_attestation_offline_wiring_script", None)
        else:
            sys.modules["check_attestation_offline_wiring_script"] = original


def test_check_workflow_content_passes_when_wired():
    module = _load_module()
    content = """
on:
  workflow_dispatch:
    inputs:
      offline_bundle_path:
        required: false
        default: ""
        type: string
jobs:
  verify:
    steps:
      - name: Offline bundle preflight
        if: ${{ github.event_name == 'workflow_dispatch' && inputs.offline_bundle_path != '' }}
        run: |
          if [ ! -f "${{ inputs.offline_bundle_path }}" ]; then
            echo "[fail] offline bundle file not found"
            exit 1
          fi
          echo "[ok] offline bundle file"
      - name: Verify artifact attestations
        run: |
          BUNDLE_ARGS=()
          if [ "${{ github.event_name }}" = "workflow_dispatch" ] && [ -n "${{ inputs.offline_bundle_path }}" ]; then
            BUNDLE_ARGS+=(--bundle "${{ inputs.offline_bundle_path }}")
          fi
          python3 scripts/verify_attestations.py "${BUNDLE_ARGS[@]}"
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert issues == []


def test_check_workflow_content_fails_when_input_missing():
    module = _load_module()
    content = """
jobs:
  verify:
    steps:
      - name: Offline bundle preflight
        if: ${{ github.event_name == 'workflow_dispatch' && inputs.offline_bundle_path != '' }}
        run: echo ok
      - name: Verify artifact attestations
        run: echo ok
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing workflow_dispatch input" in issue for issue in issues)


def test_check_workflow_content_fails_when_preflight_condition_missing():
    module = _load_module()
    content = """
on:
  workflow_dispatch:
    inputs:
      offline_bundle_path:
        required: false
        default: ""
        type: string
jobs:
  verify:
    steps:
      - name: Offline bundle preflight
        run: echo ok
      - name: Verify artifact attestations
        run: |
          python3 scripts/verify_attestations.py --bundle path
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing expected condition" in issue for issue in issues)


def test_check_workflow_content_fails_when_bundle_usage_missing_in_verify_step():
    module = _load_module()
    content = """
on:
  workflow_dispatch:
    inputs:
      offline_bundle_path:
        required: false
        default: ""
        type: string
jobs:
  verify:
    steps:
      - name: Offline bundle preflight
        if: ${{ github.event_name == 'workflow_dispatch' && inputs.offline_bundle_path != '' }}
        run: |
          if [ ! -f "${{ inputs.offline_bundle_path }}" ]; then
            echo missing
            exit 1
          fi
          echo offline bundle file
      - name: Verify artifact attestations
        run: python3 scripts/verify_attestations.py
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing expected token '--bundle'" in issue for issue in issues)
