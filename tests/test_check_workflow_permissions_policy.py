from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_workflow_permissions_policy.py"
    spec = importlib.util.spec_from_file_location(
        "check_workflow_permissions_policy_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_workflow_permissions_policy_script")
    sys.modules["check_workflow_permissions_policy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_workflow_permissions_policy_script", None)
        else:
            sys.modules["check_workflow_permissions_policy_script"] = original


def test_check_workflow_content_passes_for_expected_workflow_and_job_permissions():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - name: noop
        run: echo ok
""".strip()
    issues = module.check_workflow_content(
        content,
        "example.yml",
        expected_workflow_permissions={"contents": "read"},
        expected_job_permissions={"verify": {"contents": "read", "id-token": "write"}},
    )
    assert issues == []


def test_check_workflow_content_fails_when_top_level_permissions_missing():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
jobs:
  verify:
    runs-on: ubuntu-latest
""".strip()
    issues = module.check_workflow_content(
        content,
        "example.yml",
        expected_workflow_permissions={"contents": "read"},
    )
    assert any("missing top-level permissions block" in issue for issue in issues)


def test_check_workflow_content_fails_for_macro_permissions():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
permissions: read-all
jobs:
  verify:
    runs-on: ubuntu-latest
""".strip()
    issues = module.check_workflow_content(
        content,
        "example.yml",
        expected_workflow_permissions={"contents": "read"},
    )
    assert any("must be a mapping, not scalar" in issue for issue in issues)


def test_check_workflow_content_fails_when_expected_job_permissions_missing():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: echo ok
""".strip()
    issues = module.check_workflow_content(
        content,
        "example.yml",
        expected_workflow_permissions={"contents": "read"},
        expected_job_permissions={"verify": {"contents": "read", "id-token": "write"}},
    )
    assert any("missing permissions block" in issue for issue in issues)
