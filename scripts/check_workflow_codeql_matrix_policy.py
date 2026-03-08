#!/usr/bin/env python3
"""Validate workflow CodeQL and matrix guardrails policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
MATRIX_CHECKLIST = Path(".github/workflow-matrix-review-checklist.md")
CODEQL_WORKFLOW = Path(".github/workflows/codeql-actions-security.yml")
TRUST_BOUNDARY_WORKFLOW = Path(".github/workflows/verify-nightly-attestations.yml")
TRUST_BOUNDARY_CHECKLIST = Path(
    "docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md"
)

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## CodeQL Actions Advanced Setup (WB-SUG-096)",
    "## High-Signal Actions Query Gate (WB-SUG-097)",
    "## workflow_run Artifact Trust Boundary Rule (WB-SUG-098)",
    "## Matrix max-parallel Defaults and Review Checklist (WB-SUG-099)",
    "## Explicit Matrix fail-fast and continue-on-error (WB-SUG-100)",
    "## Dedicated CodeQL Merge-Blocker Contract (WB-SUG-117)",
    "## workflow_run Trust-Boundary Checklist Contract (WB-SUG-118)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "actions/untrusted-checkout/high",
    "actions/artifact-poisoning",
    "actions/missing-workflow-permissions",
    "workflow_run",
    "untrusted",
    "provenance",
    "digest verification",
    "max-parallel = 4",
    "max-parallel = 2",
    "max-parallel = 1",
    "fail-fast",
    "continue-on-error",
    "merge-blocking",
    "workflow_run",
    "trust-boundary checklist",
)

REQUIRED_FILES: tuple[Path, ...] = (
    Path("scripts/check_workflow_codeql_matrix_policy.py"),
    Path(".github/workflows/codeql-actions-security.yml"),
    Path(".github/workflow-matrix-review-checklist.md"),
    Path("docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md"),
)

CODEQL_WORKFLOW_TOKENS: tuple[str, ...] = (
    "name: CodeQL Actions Security",
    "language: [actions]",
    "languages: ${{ matrix.language }}",
    "queries: security-extended",
    "github/codeql-action/init@",
    "github/codeql-action/autobuild@",
    "github/codeql-action/analyze@",
    "max-parallel: 1",
    "fail-fast: false",
    "continue-on-error: false",
)

TRUST_BOUNDARY_TOKENS: tuple[str, ...] = (
    "Declare workflow_run trust boundary",
    "Treat downloaded artifacts and extracted workspace as untrusted until provenance and digest verification completes.",
    "python3 scripts/verify_attestations.py",
    "python3 scripts/verify_artifact_digests.py",
)

CHECKLIST_TOKENS: tuple[str, ...] = (
    "CI class default: max-parallel = 4",
    "Nightly class default: max-parallel = 2",
    "Policy class default: max-parallel = 1",
    "`max-parallel` declared explicitly",
    "`fail-fast` declared explicitly",
    "`continue-on-error` declared explicitly",
)

TRUST_BOUNDARY_CHECKLIST_TOKENS: tuple[str, ...] = (
    "workflow_run",
    "untrusted until verification passes",
    "provenance verification",
    "digest verification",
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): (
        "python3 scripts/check_workflow_codeql_matrix_policy.py",
    ),
    Path(".github/workflows/size-check.yml"): (
        "python3 scripts/check_workflow_codeql_matrix_policy.py",
    ),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Workflow CodeQL and Matrix Guardrails",
    "python3 scripts/check_workflow_codeql_matrix_policy.py",
    "cat docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md",
    "cat .github/workflow-matrix-review-checklist.md",
    "cat .github/workflows/codeql-actions-security.yml",
    "cat docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md",
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

    content = policy_path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            issues.append(f"missing policy heading in {POLICY_DOC.as_posix()}: {heading}")
    for snippet in REQUIRED_POLICY_SNIPPETS:
        if snippet not in content:
            issues.append(f"missing policy snippet in {POLICY_DOC.as_posix()}: {snippet}")

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            issues.append(f"missing required file: {relative.as_posix()}")

    issues.extend(
        _check_file_tokens(
            root / CODEQL_WORKFLOW,
            CODEQL_WORKFLOW_TOKENS,
            CODEQL_WORKFLOW.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / TRUST_BOUNDARY_WORKFLOW,
            TRUST_BOUNDARY_TOKENS,
            TRUST_BOUNDARY_WORKFLOW.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / MATRIX_CHECKLIST,
            CHECKLIST_TOKENS,
            MATRIX_CHECKLIST.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / TRUST_BOUNDARY_CHECKLIST,
            TRUST_BOUNDARY_CHECKLIST_TOKENS,
            TRUST_BOUNDARY_CHECKLIST.as_posix(),
        )
    )
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
        description="Validate workflow CodeQL/matrix guardrails policy contract."
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
        print("[fail] workflow codeql/matrix guardrails policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] workflow codeql/matrix guardrails policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {CODEQL_WORKFLOW.as_posix()}")
    print(f"  - {MATRIX_CHECKLIST.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
