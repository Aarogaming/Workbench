from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_campaign_wave_policy.py"
    spec = importlib.util.spec_from_file_location(
        "check_campaign_wave_policy_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_campaign_wave_policy_script")
    sys.modules["check_campaign_wave_policy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_campaign_wave_policy_script", None)
        else:
            sys.modules["check_campaign_wave_policy_script"] = original


def _write_required_templates(module, root: Path) -> None:
    for template_path, sections in module.TEMPLATE_REQUIREMENTS.items():
        target = root / template_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(sections) + "\n", encoding="utf-8")


def _valid_policy_body(module) -> str:
    return "\n".join(
        (
            *module.REQUIRED_POLICY_HEADINGS,
            *module.REQUIRED_POLICY_SNIPPETS,
            *(path.as_posix() for path in module.TEMPLATE_REQUIREMENTS),
        )
    ) + "\n"


def test_check_campaign_wave_policy_passes_with_required_contract():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        policy = root / module.POLICY_DOC
        policy.parent.mkdir(parents=True, exist_ok=True)
        policy.write_text(_valid_policy_body(module), encoding="utf-8")
        _write_required_templates(module, root)

        issues = module.check_campaign_wave_policy(root)
        assert issues == []


def test_check_campaign_wave_policy_fails_when_policy_heading_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        policy = root / module.POLICY_DOC
        policy.parent.mkdir(parents=True, exist_ok=True)
        content = _valid_policy_body(module).replace("## Lane WIP Limits", "")
        policy.write_text(content, encoding="utf-8")
        _write_required_templates(module, root)

        issues = module.check_campaign_wave_policy(root)
        assert any("missing policy heading" in issue for issue in issues)


def test_check_campaign_wave_policy_fails_when_template_section_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        policy = root / module.POLICY_DOC
        policy.parent.mkdir(parents=True, exist_ok=True)
        policy.write_text(_valid_policy_body(module), encoding="utf-8")
        _write_required_templates(module, root)

        ariadne = root / Path("docs/research/templates/ARIADNE_THREAD_AFTER_ACTION_TEMPLATE.md")
        ariadne.write_text("## Planned Path\n", encoding="utf-8")

        issues = module.check_campaign_wave_policy(root)
        assert any("missing template section" in issue for issue in issues)
