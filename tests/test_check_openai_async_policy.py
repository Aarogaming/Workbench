from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_openai_async_policy.py"
    spec = importlib.util.spec_from_file_location(
        "check_openai_async_policy_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_openai_async_policy_script")
    sys.modules["check_openai_async_policy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_openai_async_policy_script", None)
        else:
            sys.modules["check_openai_async_policy_script"] = original


def test_check_policy_passes_with_required_contract():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / module.POLICY_DOC
        target.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join((*module.REQUIRED_HEADINGS, *module.REQUIRED_SNIPPETS)) + "\n"
        target.write_text(body, encoding="utf-8")

        issues = module.check_policy(root)
        assert issues == []


def test_check_policy_fails_when_heading_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / module.POLICY_DOC
        target.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join((*module.REQUIRED_HEADINGS[:-1], *module.REQUIRED_SNIPPETS)) + "\n"
        target.write_text(body, encoding="utf-8")

        issues = module.check_policy(root)
        assert any("missing policy heading" in issue for issue in issues)


def test_check_policy_fails_when_snippet_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / module.POLICY_DOC
        target.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join((*module.REQUIRED_HEADINGS, *module.REQUIRED_SNIPPETS[:-1])) + "\n"
        target.write_text(body, encoding="utf-8")

        issues = module.check_policy(root)
        assert any("missing policy snippet" in issue for issue in issues)
