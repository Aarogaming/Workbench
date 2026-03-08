from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "run_merlin_cp6_local_checks.py"
    spec = importlib.util.spec_from_file_location("run_merlin_cp6_local_checks", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_required_commands_matches_cp6_required_set() -> None:
    module = _load_module()
    commands = module.build_required_commands()
    assert len(commands) == 5
    assert commands[0] == "python3 -m pytest -q tests/test_merlin_research_manager_consumer.py"
    assert (
        commands[1]
        == "python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k test_envelope_builders_emit_create_signal_brief_operations"
    )
    assert (
        commands[2]
        == 'python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k "test_read_only_error_selects_non_mutating_fallback or test_validation_error_maps_to_expected_fallback"'
    )
    assert "requests.get('http://localhost:8001/merlin/operations/capabilities'" in commands[3]
    assert (
        commands[4]
        == "python3 scripts/merlin_research_manager_consumer.py --capabilities-json artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json"
    )
