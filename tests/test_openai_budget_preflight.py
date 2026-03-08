from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "openai_budget_preflight.py"
    spec = importlib.util.spec_from_file_location(
        "openai_budget_preflight_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("openai_budget_preflight_script")
    sys.modules["openai_budget_preflight_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("openai_budget_preflight_script", None)
        else:
            sys.modules["openai_budget_preflight_script"] = original


def test_evaluate_budget_preflight_allows_under_cap():
    module = _load_module()
    payload, code = module.evaluate_budget_preflight("production", 800, 1000, 0.9)
    assert code == 0
    assert payload["hard_block"] is False
    assert payload["alarm"] is False


def test_evaluate_budget_preflight_blocks_over_cap():
    module = _load_module()
    payload, code = module.evaluate_budget_preflight("staging", 1050, 1000, 0.9)
    assert code == 1
    assert payload["hard_block"] is True
    assert payload["status"] == "block"
