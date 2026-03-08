from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "openai_retry_backoff.py"
    spec = importlib.util.spec_from_file_location(
        "openai_retry_backoff_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("openai_retry_backoff_script")
    sys.modules["openai_retry_backoff_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("openai_retry_backoff_script", None)
        else:
            sys.modules["openai_retry_backoff_script"] = original


def test_compute_backoff_schedule_is_deterministic_with_seed():
    module = _load_module()
    first = module.compute_backoff_schedule(
        5,
        base_delay=1.0,
        max_delay=10.0,
        jitter_ratio=0.2,
        seed=42,
    )
    second = module.compute_backoff_schedule(
        5,
        base_delay=1.0,
        max_delay=10.0,
        jitter_ratio=0.2,
        seed=42,
    )
    assert first == second
    assert len(first) == 5


def test_compute_backoff_schedule_respects_max_delay_bound():
    module = _load_module()
    schedule = module.compute_backoff_schedule(
        6,
        base_delay=2.0,
        max_delay=5.0,
        jitter_ratio=0.0,
        seed=1,
    )
    assert schedule[-1] == 5.0
    assert all(value <= 5.0 for value in schedule)


def test_compute_backoff_schedule_rejects_invalid_params():
    module = _load_module()
    try:
        module.compute_backoff_schedule(
            0,
            base_delay=1.0,
            max_delay=10.0,
            jitter_ratio=0.2,
            seed=1,
        )
        raised = False
    except ValueError:
        raised = True
    assert raised is True
