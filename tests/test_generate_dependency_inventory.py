from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "generate_dependency_inventory.py"
    spec = importlib.util.spec_from_file_location(
        "generate_dependency_inventory_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("generate_dependency_inventory_script")
    sys.modules["generate_dependency_inventory_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("generate_dependency_inventory_script", None)
        else:
            sys.modules["generate_dependency_inventory_script"] = original


def test_generate_inventory_writes_snapshot_and_spdx():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "reports"
        outputs = module.generate_inventory(
            output_dir=out_dir,
            freeze_lines=[
                "requests==2.32.3",
                "pytest==9.0.2",
                "requests==2.32.3",
            ],
            generated_at="2026-02-17T00:00:00Z",
        )

        assert outputs["requirements"].exists()
        assert outputs["snapshot"].exists()
        assert outputs["spdx"].exists()

        snapshot = json.loads(outputs["snapshot"].read_text(encoding="utf-8"))
        assert snapshot["schema"] == "workbench.dependency_snapshot.v1"
        assert snapshot["package_count"] == 2
        assert snapshot["packages"] == ["pytest==9.0.2", "requests==2.32.3"]

        spdx = json.loads(outputs["spdx"].read_text(encoding="utf-8"))
        assert spdx["spdxVersion"] == "SPDX-2.3"
        assert len(spdx["packages"]) == 2
        assert spdx["packages"][0]["name"] == "pytest"


def test_parse_name_version_handles_unpinned_values():
    module = _load_module()
    name, version = module._parse_name_version("editable-project")
    assert name == "editable-project"
    assert version == "UNKNOWN"
