from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_plugin_contracts.py"
    spec = importlib.util.spec_from_file_location("check_plugin_contracts_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_plugin_contracts_script")
    sys.modules["check_plugin_contracts_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_plugin_contracts_script", None)
        else:
            sys.modules["check_plugin_contracts_script"] = original


def _write_manifest(plugin_dir: Path, capabilities: list[str], exports: list[str]):
    payload = {
        "schemaName": "PluginManifest",
        "entry": "plugin.py",
        "capabilities": [{"name": name} for name in capabilities],
        "extensions": {"aas": {"exports": exports}},
    }
    (plugin_dir / "manifest.json").write_text(json.dumps(payload), encoding="utf-8")


def test_validate_manifest_accepts_matching_capabilities_and_exports(tmp_path: Path):
    module = _load_module()
    plugin_dir = tmp_path / "demo"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text(
        "class Plugin:\n    def commands(self):\n        return {}\n",
        encoding="utf-8",
    )
    _write_manifest(plugin_dir, capabilities=["cap.alpha"], exports=["cap.alpha"])

    findings = module._validate_manifest(plugin_dir)
    assert findings == []


def test_validate_manifest_flags_export_mismatch(tmp_path: Path):
    module = _load_module()
    plugin_dir = tmp_path / "demo"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text(
        "class Plugin:\n    def commands(self):\n        return {}\n",
        encoding="utf-8",
    )
    _write_manifest(plugin_dir, capabilities=["cap.alpha"], exports=["cap.beta"])

    findings = module._validate_manifest(plugin_dir)
    messages = [item.message for item in findings]
    assert any("capabilities missing from exports" in msg for msg in messages)
    assert any("exports missing from capabilities" in msg for msg in messages)
