from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "campaign_loop.py"
    spec = importlib.util.spec_from_file_location("campaign_loop_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("campaign_loop_script")
    sys.modules["campaign_loop_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("campaign_loop_script", None)
        else:
            sys.modules["campaign_loop_script"] = original


def test_run_shell_reports_ok_and_return_code():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)
        result = module._run_shell("python -c \"print('ok')\"", cwd)
        assert result["ok"] is True
        assert result["returnCode"] == 0
        assert isinstance(result["durationMs"], int)


def test_write_json_writes_payload():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "trace" / "campaign_trace.json"
        module._write_json(path, {"ok": True})
        assert path.exists()
        assert '"ok": true' in path.read_text(encoding="utf-8").lower()
