from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "compute_littles_law_wip.py"
    spec = importlib.util.spec_from_file_location(
        "compute_littles_law_wip_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("compute_littles_law_wip_script")
    sys.modules["compute_littles_law_wip_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("compute_littles_law_wip_script", None)
        else:
            sys.modules["compute_littles_law_wip_script"] = original


def test_compute_recommended_wip_rounds_buffered_value():
    module = _load_module()
    result = module.compute_recommended_wip(
        throughput_per_day=6,
        lead_time_days=2,
        buffer=1.15,
    )
    assert result["base_wip"] == 12
    assert result["recommended_wip"] == 14


def test_compute_recommended_wip_rejects_non_positive_inputs():
    module = _load_module()
    try:
        module.compute_recommended_wip(throughput_per_day=0, lead_time_days=2)
    except ValueError as exc:
        assert "must be > 0" in str(exc)
    else:
        raise AssertionError("expected ValueError for non-positive throughput")


def test_cli_writes_json_output():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "wip.json"
        result = subprocess.run(
            [
                "python3",
                "scripts/compute_littles_law_wip.py",
                "--throughput-per-day",
                "4",
                "--lead-time-days",
                "3",
                "--buffer",
                "1.0",
                "--json-out",
                str(out_path),
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(out_path.read_text(encoding="utf-8"))
        assert payload["recommended_wip"] == 12
