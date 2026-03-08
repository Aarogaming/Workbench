from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_workflow_run_summary_wiring.py"
    spec = importlib.util.spec_from_file_location(
        "check_workflow_run_summary_wiring_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_workflow_run_summary_wiring_script")
    sys.modules["check_workflow_run_summary_wiring_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_workflow_run_summary_wiring_script", None)
        else:
            sys.modules["check_workflow_run_summary_wiring_script"] = original


def test_check_workflow_content_passes_when_wired():
    module = _load_module()
    content = """
steps:
  - name: Generate run summary
    if: ${{ failure() || cancelled() }}
    run: python3 scripts/generate_run_summary.py --failure-taxonomy "$(python3 scripts/select_failure_taxonomy.py --workflow x --job y)"
  - name: Validate run summary
    if: ${{ failure() || cancelled() }}
    run: python3 scripts/validate_run_summary.py --path run_summary/run_summary.json
  - name: Upload run summary artifact
    if: ${{ failure() || cancelled() }}
    uses: actions/upload-artifact@abc
    with:
      name: run-summary-example
      path: |
        run_summary/run_summary.json
        run_summary/run_summary.md
""".strip()
    issues = module.check_workflow_content(content, "example.yml")
    assert issues == []


def test_check_workflow_content_fails_when_missing_steps():
    module = _load_module()
    content = """
steps:
  - name: Generate run summary
    run: python3 scripts/generate_run_summary.py
""".strip()
    issues = module.check_workflow_content(content, "broken.yml")
    assert any("missing step 'Validate run summary'" in issue for issue in issues)
    assert any("missing step 'Upload run summary artifact'" in issue for issue in issues)


def test_check_workflow_content_fails_when_expected_command_missing():
    module = _load_module()
    content = """
steps:
  - name: Generate run summary
    if: ${{ failure() || cancelled() }}
    run: echo "placeholder"
  - name: Validate run summary
    if: ${{ failure() || cancelled() }}
    run: python3 scripts/validate_run_summary.py --path run_summary/run_summary.json
  - name: Upload run summary artifact
    if: ${{ failure() || cancelled() }}
    uses: actions/upload-artifact@abc
    with:
      name: run-summary-example
      path: |
        run_summary/run_summary.json
        run_summary/run_summary.md
""".strip()
    issues = module.check_workflow_content(content, "missing-command.yml")
    assert any(
        "step 'Generate run summary' missing expected token 'scripts/generate_run_summary.py'"
        in issue
        for issue in issues
    )


def test_check_workflow_content_fails_when_taxonomy_selector_not_in_generate_step():
    module = _load_module()
    content = """
steps:
  - name: Generate run summary
    if: ${{ failure() || cancelled() }}
    run: python3 scripts/generate_run_summary.py --failure-taxonomy script
  - name: Validate run summary
    if: ${{ failure() || cancelled() }}
    run: python3 scripts/validate_run_summary.py --path run_summary/run_summary.json
  - name: Upload run summary artifact
    if: ${{ failure() || cancelled() }}
    uses: actions/upload-artifact@abc
    with:
      name: run-summary-example
      path: |
        run_summary/run_summary.json
        run_summary/run_summary.md
  - name: Unrelated
    run: python3 scripts/select_failure_taxonomy.py --workflow x --job y
""".strip()
    issues = module.check_workflow_content(content, "taxonomy-missing.yml")
    assert any(
        "step 'Generate run summary' missing expected token 'scripts/select_failure_taxonomy.py'"
        in issue
        for issue in issues
    )
