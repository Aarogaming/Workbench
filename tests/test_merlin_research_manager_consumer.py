from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def _script_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    return root / "scripts" / "merlin_research_manager_consumer.py"


def _load_module():
    path = _script_path()
    spec = importlib.util.spec_from_file_location(
        "merlin_research_manager_consumer", path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("merlin_research_manager_consumer")
    sys.modules["merlin_research_manager_consumer"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("merlin_research_manager_consumer", None)
        else:
            sys.modules["merlin_research_manager_consumer"] = original


def test_capability_present_selects_research_manager_flow() -> None:
    module = _load_module()
    payload = {
        "operations": [
            {"name": "merlin.research.manager.session.create"},
            {"name": "merlin.research.manager.session.get"},
            {"name": "merlin.research.manager.brief.get"},
            {"name": "merlin.research.manager.session.signal.add"},
        ]
    }
    decision = module.detect_research_manager_route(payload)
    assert decision["research_manager_enabled"] is True
    assert decision["selected_path"] == "research_manager"
    assert decision["missing_core_operations"] == []


def test_envelope_builders_emit_create_signal_brief_operations() -> None:
    module = _load_module()
    create_env = module.build_session_create_envelope(objective="sync")
    signal_env = module.build_session_signal_add_envelope(
        session_id="sess-001",
        signal_type="observation",
        signal_payload={"source": "workbench"},
    )
    brief_env = module.build_brief_get_envelope(session_id="sess-001")

    assert create_env["operation"] == module.OP_SESSION_CREATE
    assert signal_env["operation"] == module.OP_SESSION_SIGNAL_ADD
    assert brief_env["operation"] == module.OP_BRIEF_GET


def test_read_only_error_selects_non_mutating_fallback() -> None:
    module = _load_module()
    decision = module.map_research_manager_fallback(
        error_payload={"error": {"code": "RESEARCH_MANAGER_READ_ONLY"}},
        requested_operation=module.OP_SESSION_CREATE,
    )
    assert decision["error_code"] == "RESEARCH_MANAGER_READ_ONLY"
    assert decision["selected_path"] == "legacy_non_research_non_mutating"
    assert decision["mutating_allowed"] is False
    assert decision["recommended_read_operation"] == module.OP_BRIEF_GET


def test_validation_error_maps_to_expected_fallback() -> None:
    module = _load_module()
    decision = module.map_research_manager_fallback(
        error_payload={"error": {"code": "VALIDATION_ERROR"}},
        requested_operation="merlin.research.manager.session.get",
    )
    assert decision["error_code"] == "VALIDATION_ERROR"
    assert decision["selected_path"] == "legacy_non_research"
    assert decision["fallback_mode"] == "repair_input_and_retry_legacy"


def test_build_operator_demo_envelopes_emits_create_signal_brief() -> None:
    module = _load_module()
    envelopes = module.build_operator_demo_envelopes(
        objective="cutover-check",
        session_id="sess-operator",
    )
    assert envelopes["create"]["operation"] == module.OP_SESSION_CREATE
    assert envelopes["signal"]["operation"] == module.OP_SESSION_SIGNAL_ADD
    assert envelopes["brief"]["operation"] == module.OP_BRIEF_GET
    assert envelopes["create"]["payload"]["objective"] == "cutover-check"
    assert envelopes["signal"]["payload"]["session_id"] == "sess-operator"
    assert envelopes["brief"]["payload"]["session_id"] == "sess-operator"


def test_emit_envelopes_cli_writes_artifact(tmp_path: Path) -> None:
    out = tmp_path / "envelopes.json"
    command = [
        sys.executable,
        _script_path().as_posix(),
        "--emit-envelopes-json",
        out.as_posix(),
        "--objective",
        "cutover-check",
        "--session-id",
        "sess-operator",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    stdout = json.loads(completed.stdout)
    artifact = json.loads(out.read_text(encoding="utf-8"))

    assert stdout["envelope_preview"]["artifact_path"] == out.as_posix()
    assert stdout["envelope_preview"]["create_operation"] == (
        "merlin.research.manager.session.create"
    )
    assert stdout["envelope_preview"]["signal_operation"] == (
        "merlin.research.manager.session.signal.add"
    )
    assert stdout["envelope_preview"]["brief_operation"] == (
        "merlin.research.manager.brief.get"
    )
    assert artifact["create"]["payload"]["objective"] == "cutover-check"
    assert artifact["signal"]["payload"]["session_id"] == "sess-operator"
    assert artifact["brief"]["payload"]["session_id"] == "sess-operator"


def test_validation_error_fallback_supports_top_level_code() -> None:
    module = _load_module()
    decision = module.map_research_manager_fallback(
        error_payload={"code": "VALIDATION_ERROR"},
        requested_operation=module.OP_SESSION_GET,
    )
    assert decision["error_code"] == "VALIDATION_ERROR"
    assert decision["selected_path"] == "legacy_non_research"
    assert decision["fallback_mode"] == "repair_input_and_retry_legacy"
