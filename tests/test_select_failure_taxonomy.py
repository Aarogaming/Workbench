from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "select_failure_taxonomy.py"
    spec = importlib.util.spec_from_file_location("select_failure_taxonomy_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("select_failure_taxonomy_script")
    sys.modules["select_failure_taxonomy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("select_failure_taxonomy_script", None)
        else:
            sys.modules["select_failure_taxonomy_script"] = original


def test_select_failure_taxonomy_detects_supply_chain():
    module = _load_module()
    value = module.select_failure_taxonomy("Verify Nightly Attestations", "verify-attestations")
    assert value == "supply_chain"


def test_select_failure_taxonomy_detects_policy():
    module = _load_module()
    value = module.select_failure_taxonomy("Policy Review", "workflow-policy-review")
    assert value == "policy"


def test_select_failure_taxonomy_defaults_to_script():
    module = _load_module()
    value = module.select_failure_taxonomy("Workbench CI", "python-smoke")
    assert value == "script"
