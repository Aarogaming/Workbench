from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "eval_report.py"
    spec = importlib.util.spec_from_file_location("eval_report_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("eval_report_script")
    sys.modules["eval_report_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("eval_report_script", None)
        else:
            sys.modules["eval_report_script"] = original


def test_eval_workflow_pause_resume_passes():
    module = _load_module()
    root = Path(__file__).resolve().parents[1]
    result = module._eval_workflow_pause_resume(root)
    assert result.eval_id == "workflow_pause_resume"
    assert result.passed is True


def test_eval_mcp_auth_invalid_credentials_passes():
    module = _load_module()
    root = Path(__file__).resolve().parents[1]
    result = module._eval_mcp_auth_invalid_credentials(root)
    assert result.eval_id == "mcp_auth_invalid_credentials"
    assert result.passed is True


def test_eval_workflow_pinning_passes():
    module = _load_module()
    root = Path(__file__).resolve().parents[1]
    result = module._eval_workflow_pinning(root)
    assert result.eval_id == "workflow_pinning_audit"
    assert result.passed is True


def test_eval_workflow_pinning_exceptions_passes():
    module = _load_module()
    root = Path(__file__).resolve().parents[1]
    result = module._eval_workflow_pinning_exceptions(root)
    assert result.eval_id == "workflow_pinning_exceptions_review"
    assert result.passed is True
