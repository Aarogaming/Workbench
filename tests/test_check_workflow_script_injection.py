from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_workflow_script_injection.py"
    spec = importlib.util.spec_from_file_location(
        "check_workflow_script_injection_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_workflow_script_injection_script")
    sys.modules["check_workflow_script_injection_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_workflow_script_injection_script", None)
        else:
            sys.modules["check_workflow_script_injection_script"] = original


def test_scan_workflow_content_passes_for_safe_contexts():
    module = _load_module()
    content = """
name: Safe
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Safe run
        run: echo "${{ github.workflow }}"
""".strip()
    issues = module.scan_workflow_content(content, "safe.yml")
    assert issues == []


def test_scan_workflow_content_fails_for_untrusted_inline_token():
    module = _load_module()
    content = """
name: Unsafe
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Unsafe run
        run: echo "${{ github.event.pull_request.title }}"
""".strip()
    issues = module.scan_workflow_content(content, "unsafe.yml")
    assert any("untrusted context token" in issue for issue in issues)


def test_scan_workflow_content_fails_for_untrusted_block_token():
    module = _load_module()
    content = """
name: Unsafe
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Unsafe run block
        run: |
          echo "start"
          echo "${{ github.event.issue.body }}"
""".strip()
    issues = module.scan_workflow_content(content, "unsafe-block.yml")
    assert any("run block" in issue for issue in issues)
