from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "generate_reusable_workflow_inventory.py"
    spec = importlib.util.spec_from_file_location(
        "generate_reusable_workflow_inventory_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("generate_reusable_workflow_inventory_script")
    sys.modules["generate_reusable_workflow_inventory_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("generate_reusable_workflow_inventory_script", None)
        else:
            sys.modules["generate_reusable_workflow_inventory_script"] = original


def test_collect_reusable_workflow_consumers_detects_local_and_remote_uses():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        workflows = root / ".github" / "workflows"
        workflows.mkdir(parents=True, exist_ok=True)
        (workflows / "consumer.yml").write_text(
            "\n".join(
                [
                    "jobs:",
                    "  local:",
                    "    uses: ./.github/workflows/reusable-policy-review.yml",
                    "  remote:",
                    "    uses: org/repo/.github/workflows/reusable.yml@main",
                    "  action:",
                    "    steps:",
                    "      - uses: actions/checkout@deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        entries = module.collect_reusable_workflow_consumers(root)
        assert len(entries) == 2
        scopes = sorted(entry["scope"] for entry in entries)
        assert scopes == ["local", "remote"]


def test_write_json_and_markdown_reports():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        json_out = root / "inventory.json"
        md_out = root / "inventory.md"
        entries = [
            {
                "consumer_workflow": ".github/workflows/a.yml",
                "line": 10,
                "scope": "local",
                "target_workflow": "./.github/workflows/reusable.yml",
                "ref": "local",
            }
        ]
        module._write_json(json_out, entries)
        module._write_markdown(md_out, entries)

        payload = json.loads(json_out.read_text(encoding="utf-8"))
        assert payload["schema"] == "workbench.reusable_workflow_inventory.v1"
        assert payload["entry_count"] == 1
        assert "Reusable Workflow Consumer Inventory" in md_out.read_text(encoding="utf-8")
