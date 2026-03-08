from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "evaluate_background_task_slo.py"
    spec = importlib.util.spec_from_file_location(
        "evaluate_background_task_slo_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("evaluate_background_task_slo_script")
    sys.modules["evaluate_background_task_slo_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("evaluate_background_task_slo_script", None)
        else:
            sys.modules["evaluate_background_task_slo_script"] = original


def test_evaluate_background_task_slo_within_limit():
    module = _load_module()
    payload = module.evaluate_background_task_slo(450, 600, False)
    assert payload["timeout_breach"] is False
    assert payload["slo_violation"] is False


def test_evaluate_background_task_slo_violation_when_over_timeout_and_not_cancelled():
    module = _load_module()
    payload = module.evaluate_background_task_slo(700, 600, False)
    assert payload["timeout_breach"] is True
    assert payload["slo_violation"] is True
    assert payload["recommended_action"] == "cancel_and_escalate"
