from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_attestation_preflight_wiring.py"
    spec = importlib.util.spec_from_file_location(
        "check_attestation_preflight_wiring_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_attestation_preflight_wiring_script")
    sys.modules["check_attestation_preflight_wiring_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_attestation_preflight_wiring_script", None)
        else:
            sys.modules["check_attestation_preflight_wiring_script"] = original


def test_check_workflow_content_passes_when_wired():
    module = _load_module()
    content = """
steps:
  - name: GH CLI minimum version preflight
    if: ${{ github.event.repository.private == false }}
    run: python3 scripts/check_gh_cli_version.py --min-version 2.50.0
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
    assert any("missing step 'GH CLI minimum version preflight'" in issue for issue in issues)


def test_check_workflow_content_fails_when_condition_missing():
    module = _load_module()
    content = """
steps:
  - name: GH CLI minimum version preflight
    run: python3 scripts/check_gh_cli_version.py --min-version 2.50.0
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing expected condition" in issue for issue in issues)


def test_check_workflow_content_fails_when_min_version_token_missing():
    module = _load_module()
    content = """
steps:
  - name: GH CLI minimum version preflight
    if: ${{ github.event.repository.private == false }}
    run: python3 scripts/check_gh_cli_version.py
""".strip()
    issues = module.check_workflow_content(content, "workflow.yml")
    assert any("missing expected token '--min-version 2.50.0'" in issue for issue in issues)
