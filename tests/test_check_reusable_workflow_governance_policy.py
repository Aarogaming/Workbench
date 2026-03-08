from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_reusable_workflow_governance_policy.py"
    spec = importlib.util.spec_from_file_location(
        "check_reusable_workflow_governance_policy_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_reusable_workflow_governance_policy_script")
    sys.modules["check_reusable_workflow_governance_policy_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_reusable_workflow_governance_policy_script", None)
        else:
            sys.modules["check_reusable_workflow_governance_policy_script"] = original


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

    checklist = root / module.CHECKLIST_TEMPLATE
    checklist.parent.mkdir(parents=True, exist_ok=True)
    checklist.write_text("\n".join(module.CHECKLIST_TOKENS) + "\n", encoding="utf-8")

    inventory_script = root / module.INVENTORY_SCRIPT
    inventory_script.parent.mkdir(parents=True, exist_ok=True)
    inventory_script.write_text("\n".join(module.INVENTORY_SCRIPT_TOKENS) + "\n", encoding="utf-8")

    for relative in module.REQUIRED_FILES:
        target = root / relative
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# placeholder\n", encoding="utf-8")

    for workflow_path, tokens in module.WORKFLOW_TOKENS.items():
        target = root / workflow_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(tokens) + "\n", encoding="utf-8")

    # Depth chain: a -> b -> c (depth 2, within cap)
    workflows = root / ".github" / "workflows"
    (workflows / "a.yml").write_text(
        "jobs:\n  x:\n    uses: ./.github/workflows/b.yml\n",
        encoding="utf-8",
    )
    (workflows / "b.yml").write_text(
        "jobs:\n  x:\n    uses: ./.github/workflows/c.yml\n",
        encoding="utf-8",
    )
    (workflows / "c.yml").write_text("jobs:\n  x:\n    runs-on: ubuntu-latest\n", encoding="utf-8")


def test_check_policy_passes_with_required_contract():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        issues = module.check_policy(root)
        assert issues == []


def test_check_policy_fails_for_broad_self_hosted_selector():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        workflow = root / ".github" / "workflows" / "selfhosted.yml"
        workflow.write_text(
            "jobs:\n  x:\n    runs-on: self-hosted\n",
            encoding="utf-8",
        )
        issues = module.check_policy(root)
        assert any("broad self-hosted selector forbidden" in issue for issue in issues)


def test_check_policy_fails_when_depth_exceeds_cap():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_required_contract(module, root)
        workflows = root / ".github" / "workflows"
        (workflows / "c.yml").write_text(
            "jobs:\n  x:\n    uses: ./.github/workflows/d.yml\n",
            encoding="utf-8",
        )
        (workflows / "d.yml").write_text(
            "jobs:\n  x:\n    uses: ./.github/workflows/e.yml\n",
            encoding="utf-8",
        )
        (workflows / "e.yml").write_text("jobs:\n  x:\n    runs-on: ubuntu-latest\n", encoding="utf-8")
        issues = module.check_policy(root)
        assert any("reusable workflow call depth" in issue for issue in issues)
