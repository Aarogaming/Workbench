from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_workflow_operator_handoff_policy.py"
    spec = importlib.util.spec_from_file_location(
        "check_workflow_operator_handoff_policy_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_workflow_operator_handoff_policy_script")
    sys.modules["check_workflow_operator_handoff_policy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_workflow_operator_handoff_policy_script", None)
        else:
            sys.modules["check_workflow_operator_handoff_policy_script"] = original


def _write_required_contract(module, root: Path) -> None:
    policy = root / module.POLICY_DOC
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        "\n".join((*module.REQUIRED_HEADINGS, *module.REQUIRED_POLICY_SNIPPETS)) + "\n",
        encoding="utf-8",
    )

    for relative in module.REQUIRED_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# placeholder\n", encoding="utf-8")

    run_summary = root / module.RUN_SUMMARY_SCRIPT
    run_summary.write_text("\n".join(module.RUN_SUMMARY_SCRIPT_TOKENS) + "\n", encoding="utf-8")

    quality = root / module.QUALITY_GATES_SCRIPT
    quality.write_text(
        "\n".join(module.QUALITY_GATES_SCRIPT_TOKENS) + "\n",
        encoding="utf-8",
    )

    runbook = root / module.RUNBOOK_DOC
    runbook.parent.mkdir(parents=True, exist_ok=True)
    runbook.write_text("\n".join(module.REQUIRED_RUNBOOK_TOKENS) + "\n", encoding="utf-8")

    health_board = root / module.HEALTH_BOARD_DOC
    health_board.parent.mkdir(parents=True, exist_ok=True)
    health_board.write_text("\n".join(module.HEALTH_BOARD_TOKENS) + "\n", encoding="utf-8")

    for workflow_path, tokens in module.WORKFLOW_TOKENS.items():
        workflow = root / workflow_path
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("\n".join(tokens) + "\n", encoding="utf-8")

    for workflow_path, tokens in module.CLEANUP_WORKFLOW_TOKENS.items():
        workflow = root / workflow_path
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("\n".join(tokens) + "\n", encoding="utf-8")


def test_check_policy_passes_with_required_contract():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        issues = module.check_policy(root)
        assert issues == []


def test_check_policy_fails_when_heading_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        policy = root / module.POLICY_DOC
        policy.write_text(
            policy.read_text(encoding="utf-8").replace(module.REQUIRED_HEADINGS[0], ""),
            encoding="utf-8",
        )
        issues = module.check_policy(root)
        assert any("missing policy heading" in issue for issue in issues)


def test_check_policy_fails_when_run_summary_script_tokens_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        run_summary = root / module.RUN_SUMMARY_SCRIPT
        run_summary.write_text("# missing tokens\n", encoding="utf-8")
        issues = module.check_policy(root)
        assert any("scripts/generate_run_summary.py: missing token" in issue for issue in issues)
