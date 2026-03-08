from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_operations_nist_mapping.py"
    spec = importlib.util.spec_from_file_location(
        "check_operations_nist_mapping_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_operations_nist_mapping_script")
    sys.modules["check_operations_nist_mapping_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_operations_nist_mapping_script", None)
        else:
            sys.modules["check_operations_nist_mapping_script"] = original


def test_check_operations_doc_passes_with_required_sections_and_commands():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / module.OPERATIONS_DOC
        target.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join((*module.REQUIRED_SECTIONS, *module.REQUIRED_COMMAND_SNIPPETS)) + "\n"
        target.write_text(body, encoding="utf-8")

        issues = module.check_operations_doc(root)
        assert issues == []


def test_check_operations_doc_fails_when_section_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / module.OPERATIONS_DOC
        target.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join((*module.REQUIRED_SECTIONS[:-1], *module.REQUIRED_COMMAND_SNIPPETS)) + "\n"
        target.write_text(body, encoding="utf-8")

        issues = module.check_operations_doc(root)
        assert any("missing lifecycle section" in issue for issue in issues)


def test_check_operations_doc_fails_when_command_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / module.OPERATIONS_DOC
        target.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join((*module.REQUIRED_SECTIONS, *module.REQUIRED_COMMAND_SNIPPETS[:-1])) + "\n"
        target.write_text(body, encoding="utf-8")

        issues = module.check_operations_doc(root)
        assert any("missing lifecycle command snippet" in issue for issue in issues)
