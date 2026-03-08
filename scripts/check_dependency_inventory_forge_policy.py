#!/usr/bin/env python3
"""Validate dependency inventory and reusable forge-gates policy wiring."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Build-Time Dependency Snapshot Submission (WB-SUG-068)",
    "## SBOM Artifact and Snapshot Submission (WB-SUG-069)",
    "## Reusable Forge Gates Workflow Contract (WB-SUG-070)",
    "## Runner Scale-Set Readiness Plan (WB-SUG-071)",
    "## Ephemeral Self-Hosted Runner Baseline (WB-SUG-072)",
    "## Workflow Script-Injection Lint Policy (WB-SUG-073)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "dependency snapshot",
    "dependency graph submission",
    "CycloneDX",
    "SPDX",
    ".github/workflows/reusable-forge-gates.yml",
    "runner scale-set",
    "ephemeral",
    "script-injection",
    "untrusted context",
    "check_workflow_script_injection.py",
    "generate_dependency_inventory.py",
)

REQUIRED_FILES: tuple[Path, ...] = (
    Path(".github/workflows/reusable-forge-gates.yml"),
    Path("scripts/generate_dependency_inventory.py"),
    Path("scripts/check_workflow_script_injection.py"),
    Path("scripts/check_dependency_inventory_forge_policy.py"),
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): (
        "forge-gates:",
        "uses: ./.github/workflows/reusable-forge-gates.yml",
    ),
    Path(".github/workflows/size-check.yml"): (
        "forge-gates:",
        "uses: ./.github/workflows/reusable-forge-gates.yml",
    ),
    Path(".github/workflows/nightly-evals.yml"): (
        "forge-gates:",
        "uses: ./.github/workflows/reusable-forge-gates.yml",
    ),
    Path(".github/workflows/policy-review.yml"): (
        "forge-gates:",
        "uses: ./.github/workflows/reusable-forge-gates.yml",
    ),
    Path(".github/workflows/reusable-forge-gates.yml"): (
        "Workflow script-injection lint",
        "Generate dependency snapshot + SBOM",
        "check_dependency_inventory_forge_policy.py",
        "actions/upload-artifact@",
        "retention-days: 30",
    ),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Dependency Inventory and Forge Gates",
    "python3 scripts/check_dependency_inventory_forge_policy.py",
    "python3 scripts/check_workflow_script_injection.py",
    "python3 scripts/generate_dependency_inventory.py --output-dir docs/reports",
)


def _check_file_tokens(path: Path, tokens: tuple[str, ...], issue_prefix: str) -> list[str]:
    if not path.exists():
        return [f"missing required file: {path.as_posix()}"]
    content = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for token in tokens:
        if token not in content:
            issues.append(f"{issue_prefix}: missing token '{token}'")
    return issues


def check_policy(root: Path) -> list[str]:
    issues: list[str] = []

    policy_path = root / POLICY_DOC
    if not policy_path.exists():
        return [f"missing policy doc: {POLICY_DOC.as_posix()}"]

    policy_content = policy_path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in policy_content:
            issues.append(f"missing policy heading in {POLICY_DOC.as_posix()}: {heading}")
    for snippet in REQUIRED_POLICY_SNIPPETS:
        if snippet not in policy_content:
            issues.append(f"missing policy snippet in {POLICY_DOC.as_posix()}: {snippet}")

    for relative in REQUIRED_FILES:
        target = root / relative
        if not target.exists():
            issues.append(f"missing required file: {relative.as_posix()}")

    for workflow_path, tokens in WORKFLOW_TOKENS.items():
        issues.extend(
            _check_file_tokens(
                root / workflow_path,
                tokens,
                workflow_path.as_posix(),
            )
        )

    issues.extend(
        _check_file_tokens(
            root / RUNBOOK_DOC,
            REQUIRED_RUNBOOK_TOKENS,
            RUNBOOK_DOC.as_posix(),
        )
    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate dependency inventory and reusable forge-gates policy wiring."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_policy(root)
    if issues:
        print("[fail] dependency inventory/forge policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] dependency inventory/forge policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    for relative in REQUIRED_FILES:
        print(f"  - {relative.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
