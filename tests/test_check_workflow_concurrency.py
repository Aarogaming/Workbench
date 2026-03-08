from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_workflow_concurrency.py"
    spec = importlib.util.spec_from_file_location(
        "check_workflow_concurrency_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_workflow_concurrency_script")
    sys.modules["check_workflow_concurrency_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_workflow_concurrency_script", None)
        else:
            sys.modules["check_workflow_concurrency_script"] = original


def test_check_workflow_content_passes_when_concurrency_wired():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-latest
""".strip()
    issues = module.check_workflow_content(content, "example.yml")
    assert issues == []


def test_check_workflow_content_fails_when_concurrency_missing():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
""".strip()
    issues = module.check_workflow_content(content, "missing.yml")
    assert any("missing top-level concurrency block" in issue for issue in issues)


def test_check_workflow_content_fails_when_group_missing():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
concurrency:
  group: custom-group
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-latest
""".strip()
    issues = module.check_workflow_content(content, "group-missing.yml")
    assert any("missing branch-aware concurrency group" in issue for issue in issues)


def test_check_workflow_content_fails_when_defined_after_jobs():
    module = _load_module()
    content = """
name: Example
on:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
""".strip()
    issues = module.check_workflow_content(content, "misplaced.yml")
    assert any("concurrency block must be defined before jobs" in issue for issue in issues)
