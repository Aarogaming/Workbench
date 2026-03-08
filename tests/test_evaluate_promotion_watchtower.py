from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "evaluate_promotion_watchtower.py"
    spec = importlib.util.spec_from_file_location(
        "evaluate_promotion_watchtower_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("evaluate_promotion_watchtower_script")
    sys.modules["evaluate_promotion_watchtower_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("evaluate_promotion_watchtower_script", None)
        else:
            sys.modules["evaluate_promotion_watchtower_script"] = original


def test_evaluate_promotion_readiness_all_green():
    module = _load_module()
    payload = module.evaluate_promotion_readiness(
        ci_pass=True,
        provenance_pass=True,
        advisory_health="healthy",
        review_approved=True,
        runtime_health="healthy",
    )
    assert payload["argus_watchtower_pass"] is True
    assert payload["janus_gate_pass"] is True
    assert payload["promotion_allowed"] is True
    assert payload["recommended_action"] == "promote"


def test_evaluate_promotion_readiness_blocks_on_advisory_and_review_failure():
    module = _load_module()
    payload = module.evaluate_promotion_readiness(
        ci_pass=True,
        provenance_pass=True,
        advisory_health="degraded",
        review_approved=False,
        runtime_health="healthy",
    )
    assert payload["argus_watchtower_pass"] is False
    assert payload["janus_stage1_review_pass"] is False
    assert payload["promotion_allowed"] is False
    assert payload["recommended_action"] == "hold"
    assert "advisory_unhealthy" in payload["blocked_reasons"]
    assert "review_gate_unapproved" in payload["blocked_reasons"]
