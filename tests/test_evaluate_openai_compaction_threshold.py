from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "evaluate_openai_compaction_threshold.py"
    spec = importlib.util.spec_from_file_location(
        "evaluate_openai_compaction_threshold_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("evaluate_openai_compaction_threshold_script")
    sys.modules["evaluate_openai_compaction_threshold_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("evaluate_openai_compaction_threshold_script", None)
        else:
            sys.modules["evaluate_openai_compaction_threshold_script"] = original


def test_evaluate_compaction_triggers_when_ratio_exceeds_threshold():
    module = _load_module()
    payload = module.evaluate_compaction(0.84, 0.8)
    assert payload["compact"] is True
    assert payload["recommended_action"] == "/responses/compact"


def test_evaluate_compaction_skips_when_ratio_below_threshold():
    module = _load_module()
    payload = module.evaluate_compaction(0.5, 0.8)
    assert payload["compact"] is False
    assert payload["recommended_action"] == "continue"
