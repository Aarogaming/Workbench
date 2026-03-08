from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_merge_ruleset_deployment_guardrails.py"
    spec = importlib.util.spec_from_file_location(
        "check_merge_ruleset_deployment_guardrails_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_merge_ruleset_deployment_guardrails_script")
    sys.modules["check_merge_ruleset_deployment_guardrails_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_merge_ruleset_deployment_guardrails_script", None)
        else:
            sys.modules["check_merge_ruleset_deployment_guardrails_script"] = original


def _write_required_contract(module, root: Path) -> None:
    policy = root / module.POLICY_DOC
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        "\n".join(
            (
                *module.REQUIRED_HEADINGS,
                *module.REQUIRED_POLICY_SNIPPETS,
            )
        )
        + "\n",
        encoding="utf-8",
    )

    codeowners = root / module.CODEOWNERS_PATH
    codeowners.parent.mkdir(parents=True, exist_ok=True)
    codeowners.write_text(
        "\n".join(module.REQUIRED_CODEOWNERS_LINES) + "\n",
        encoding="utf-8",
    )

    runbook = root / module.RUNBOOK_DOC
    runbook.parent.mkdir(parents=True, exist_ok=True)
    runbook.write_text(
        "\n".join(module.REQUIRED_RUNBOOK_TOKENS) + "\n",
        encoding="utf-8",
    )

    watchtower = root / module.PROMOTION_WATCHTOWER_SCRIPT
    watchtower.parent.mkdir(parents=True, exist_ok=True)
    watchtower.write_text(
        "\n".join(module.REQUIRED_WATCHTOWER_SCRIPT_TOKENS) + "\n",
        encoding="utf-8",
    )

    ruleset_drift = root / module.RULESET_DRIFT_REPORT
    ruleset_drift.parent.mkdir(parents=True, exist_ok=True)
    ruleset_drift.write_text(
        "\n".join(module.REQUIRED_RULESET_DRIFT_TOKENS) + "\n",
        encoding="utf-8",
    )


def test_check_guardrails_passes_with_required_contract():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        issues = module.check_guardrails(root)
        assert issues == []


def test_check_guardrails_fails_when_policy_heading_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        policy = root / module.POLICY_DOC
        policy.write_text(policy.read_text(encoding="utf-8").replace(module.REQUIRED_HEADINGS[0], ""), encoding="utf-8")
        issues = module.check_guardrails(root)
        assert any("missing policy heading" in issue for issue in issues)


def test_check_guardrails_fails_when_codeowners_entry_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        codeowners = root / module.CODEOWNERS_PATH
        codeowners.write_text("# missing entries\n", encoding="utf-8")
        issues = module.check_guardrails(root)
        assert any("missing CODEOWNERS entry" in issue for issue in issues)
