from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "evaluate_jetstream_consumer_profile.py"
    spec = importlib.util.spec_from_file_location(
        "evaluate_jetstream_consumer_profile_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("evaluate_jetstream_consumer_profile_script")
    sys.modules["evaluate_jetstream_consumer_profile_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("evaluate_jetstream_consumer_profile_script", None)
        else:
            sys.modules["evaluate_jetstream_consumer_profile_script"] = original


def test_evaluate_consumer_profile_critical_defaults():
    module = _load_module()
    payload = module.evaluate_consumer_profile("critical")
    assert payload["max_ack_pending"] == 32
    assert payload["max_deliver"] == 8
    assert payload["dlq_on_max_deliver"] is True
    assert payload["recommended_action"] == "use_baseline"


def test_evaluate_consumer_profile_override_requires_review():
    module = _load_module()
    payload = module.evaluate_consumer_profile("batch", max_ack_pending_override=300)
    assert payload["max_ack_pending"] == 300
    assert payload["override_applied"] is True
    assert payload["recommended_action"] == "review_override"
