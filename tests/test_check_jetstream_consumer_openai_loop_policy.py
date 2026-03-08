from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_jetstream_consumer_openai_loop_policy.py"
    spec = importlib.util.spec_from_file_location(
        "check_jetstream_consumer_openai_loop_policy_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_jetstream_consumer_openai_loop_policy_script")
    sys.modules["check_jetstream_consumer_openai_loop_policy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_jetstream_consumer_openai_loop_policy_script", None)
        else:
            sys.modules["check_jetstream_consumer_openai_loop_policy_script"] = original


def _write_required_contract(module, root: Path) -> None:
    policy = root / module.POLICY_DOC
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        "\n".join((*module.REQUIRED_HEADINGS, *module.REQUIRED_POLICY_SNIPPETS)) + "\n",
        encoding="utf-8",
    )

    runbook = root / module.RUNBOOK_DOC
    runbook.parent.mkdir(parents=True, exist_ok=True)
    runbook.write_text("\n".join(module.REQUIRED_RUNBOOK_TOKENS) + "\n", encoding="utf-8")

    for relative in module.REQUIRED_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# placeholder\n", encoding="utf-8")

    compaction = root / module.COMPACTION_SCRIPT
    compaction.write_text("\n".join(module.COMPACTION_TOKENS) + "\n", encoding="utf-8")

    budget = root / module.BUDGET_SCRIPT
    budget.write_text("\n".join(module.BUDGET_TOKENS) + "\n", encoding="utf-8")

    slo = root / module.SLO_SCRIPT
    slo.write_text("\n".join(module.SLO_TOKENS) + "\n", encoding="utf-8")

    jetstream_profile = root / module.JETSTREAM_PROFILE_SCRIPT
    jetstream_profile.write_text(
        "\n".join(module.JETSTREAM_PROFILE_TOKENS) + "\n",
        encoding="utf-8",
    )

    advisory = root / module.ADVISORY_TEMPLATE
    advisory.write_text("\n".join(module.ADVISORY_TEMPLATE_TOKENS) + "\n", encoding="utf-8")

    structured = root / module.STRUCTURED_OUTPUT_TEMPLATE
    structured.write_text(
        "\n".join(module.STRUCTURED_OUTPUT_TEMPLATE_TOKENS) + "\n",
        encoding="utf-8",
    )

    baseline_template = root / module.JETSTREAM_BASELINE_TEMPLATE
    baseline_template.write_text(
        "\n".join(module.JETSTREAM_BASELINE_TEMPLATE_TOKENS) + "\n",
        encoding="utf-8",
    )

    prompt_object_template = root / module.PROMPT_OBJECT_TEMPLATE
    prompt_object_template.write_text(
        "\n".join(module.PROMPT_OBJECT_TEMPLATE_TOKENS) + "\n",
        encoding="utf-8",
    )

    compaction_resume_template = root / module.COMPACTION_RESUME_TEMPLATE
    compaction_resume_template.write_text(
        "\n".join(module.COMPACTION_RESUME_TEMPLATE_TOKENS) + "\n",
        encoding="utf-8",
    )

    for workflow_path, tokens in module.WORKFLOW_TOKENS.items():
        target = root / workflow_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(tokens) + "\n", encoding="utf-8")


def test_check_policy_passes_with_required_contract():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        issues = module.check_policy(root)
        assert issues == []


def test_check_policy_fails_when_heading_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        policy = root / module.POLICY_DOC
        policy.write_text(
            policy.read_text(encoding="utf-8").replace(module.REQUIRED_HEADINGS[0], ""),
            encoding="utf-8",
        )
        issues = module.check_policy(root)
        assert any("missing policy heading" in issue for issue in issues)


def test_check_policy_fails_when_budget_script_tokens_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        budget = root / module.BUDGET_SCRIPT
        budget.write_text("# missing\n", encoding="utf-8")
        issues = module.check_policy(root)
        assert any("scripts/openai_budget_preflight.py: missing token" in issue for issue in issues)
