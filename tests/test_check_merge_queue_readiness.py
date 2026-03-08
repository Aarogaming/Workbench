from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_merge_queue_readiness.py"
    spec = importlib.util.spec_from_file_location(
        "check_merge_queue_readiness_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_merge_queue_readiness_script")
    sys.modules["check_merge_queue_readiness_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_merge_queue_readiness_script", None)
        else:
            sys.modules["check_merge_queue_readiness_script"] = original


def _write_required_files(module, root: Path, include_merge_group: bool = True) -> None:
    for workflow in module.REQUIRED_WORKFLOWS:
        target = root / workflow
        target.parent.mkdir(parents=True, exist_ok=True)
        on_block = "pull_request:\n  merge_group:\n" if include_merge_group else "pull_request:\n"
        target.write_text(f"name: test\non:\n  {on_block}", encoding="utf-8")

    sentinel = root / module.SENTINEL_WORKFLOW
    sentinel.parent.mkdir(parents=True, exist_ok=True)
    sentinel.write_text("\n".join(module.REQUIRED_SENTINEL_TOKENS) + "\n", encoding="utf-8")


def test_check_merge_queue_readiness_passes_when_contract_satisfied():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_files(module, root, include_merge_group=True)
        issues = module.check_merge_queue_readiness(root)
        assert issues == []


def test_check_merge_queue_readiness_fails_when_merge_group_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_files(module, root, include_merge_group=False)
        issues = module.check_merge_queue_readiness(root)
        assert any("missing merge_group trigger" in issue for issue in issues)


def test_check_merge_queue_readiness_fails_when_sentinel_missing_token():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_files(module, root, include_merge_group=True)
        sentinel = root / module.SENTINEL_WORKFLOW
        sentinel.write_text("name: Required Check Sentinel\n", encoding="utf-8")
        issues = module.check_merge_queue_readiness(root)
        assert any("missing required token" in issue for issue in issues)
