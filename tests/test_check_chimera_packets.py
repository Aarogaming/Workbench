from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_chimera_packets.py"
    spec = importlib.util.spec_from_file_location("check_chimera_packets_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_chimera_packets_script")
    sys.modules["check_chimera_packets_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_chimera_packets_script", None)
        else:
            sys.modules["check_chimera_packets_script"] = original


def test_check_packets_passes_when_required_docs_have_required_sections():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for relative_path, sections in module.REQUIRED_PACKET_SECTIONS.items():
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("\n".join(sections) + "\n", encoding="utf-8")

        issues = module.check_packets(root)
        assert issues == []


def test_check_packets_fails_when_section_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for relative_path, sections in module.REQUIRED_PACKET_SECTIONS.items():
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if "CP2_OPERATOR_OBSERVABILITY_PACKET" in relative_path:
                target.write_text("\n".join(sections[:-1]) + "\n", encoding="utf-8")
            else:
                target.write_text("\n".join(sections) + "\n", encoding="utf-8")

        issues = module.check_packets(root)
        assert any("missing section" in issue for issue in issues)


def test_required_packets_include_cp_runbook():
    module = _load_module()
    assert "docs/research/CP_RUNBOOK_COMMANDS.md" in module.REQUIRED_PACKET_SECTIONS
