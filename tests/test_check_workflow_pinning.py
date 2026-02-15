from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from datetime import date
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_workflow_pinning.py"
    spec = importlib.util.spec_from_file_location("check_workflow_pinning_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_workflow_pinning_script")
    sys.modules["check_workflow_pinning_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_workflow_pinning_script", None)
        else:
            sys.modules["check_workflow_pinning_script"] = original


def test_validate_uses_value_accepts_pinned_sha():
    module = _load_module()
    reason = module._validate_uses_value(
        "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"
    )
    assert reason is None


def test_validate_uses_value_rejects_version_tag():
    module = _load_module()
    reason = module._validate_uses_value("actions/checkout@v4")
    assert reason == "uses reference is not pinned to a full commit SHA"


def test_validate_uses_value_allows_local_action():
    module = _load_module()
    reason = module._validate_uses_value("./.github/actions/my-action")
    assert reason is None


def test_load_active_exceptions_flags_expired_and_activates_valid_entry():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        policy_path = Path(tmp) / "exceptions.json"
        policy_path.write_text(
            json.dumps(
                {
                    "exceptions": [
                        {
                            "id": "ok",
                            "workflow": ".github/workflows/ci.yml",
                            "uses": "actions/checkout@v4",
                            "reason": "temporary",
                            "review_by": "2099-01-01",
                        },
                        {
                            "id": "old",
                            "workflow": ".github/workflows/ci.yml",
                            "uses": "actions/setup-python@v5",
                            "reason": "legacy",
                            "review_by": "2000-01-01",
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        active, invalid, expired = module._load_active_exceptions(policy_path, date(2026, 2, 15))

    assert invalid == []
    assert len(expired) == 1
    assert (".github/workflows/ci.yml", "actions/checkout@v4") in active


def test_scan_workflow_applies_exception_for_unpinned_reference():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        wf_dir = root / ".github" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        wf_path = wf_dir / "test.yml"
        wf_path.write_text(
            "jobs:\n"
            "  test:\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n",
            encoding="utf-8",
        )
        exception = module.WorkflowPinningException(
            exception_id="x1",
            workflow=".github/workflows/test.yml",
            uses="actions/checkout@v4",
            reason="temp",
            review_by="2099-01-01",
        )
        issues, applied = module._scan_workflow(
            wf_path,
            root,
            {(".github/workflows/test.yml", "actions/checkout@v4"): exception},
        )

    assert issues == []
    assert len(applied) == 1
    assert applied[0]["exception_id"] == "x1"
