from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_committed_run_summaries.py"
    spec = importlib.util.spec_from_file_location("check_committed_run_summaries_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_committed_run_summaries_script")
    sys.modules["check_committed_run_summaries_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_committed_run_summaries_script", None)
        else:
            sys.modules["check_committed_run_summaries_script"] = original


def test_committed_run_summary_paths_filters_tracked_files():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        paths = module.committed_run_summary_paths(
            root,
            tracked_files=[
                "docs/reports/run_summary/run_summary.json",
                "docs/reports/eval_report.json",
                "artifacts/cutover/a/run_summary.json",
            ],
        )
        assert len(paths) == 2
        assert str(paths[0]).endswith("artifacts/cutover/a/run_summary.json")
        assert str(paths[1]).endswith("docs/reports/run_summary/run_summary.json")
