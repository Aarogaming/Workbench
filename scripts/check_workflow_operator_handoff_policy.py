#!/usr/bin/env python3
"""Validate workflow operator handoff and recovery policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md")
HEALTH_BOARD_DOC = Path("docs/research/WORKFLOW_HEALTH_BOARD.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
RUN_SUMMARY_SCRIPT = Path("scripts/generate_run_summary.py")
QUALITY_GATES_SCRIPT = Path("scripts/run_quality_gates.py")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Run Summary Contract Step via GITHUB_STEP_SUMMARY (WB-SUG-127)",
    "## Standardized Annotation Emission for Gate Scripts (WB-SUG-128)",
    "## Rerun Failed with Debug Operator Snippet (WB-SUG-129)",
    "## Pause Switch Policy for Non-Critical Workflows (WB-SUG-130)",
    "## Workflow Health Board Badge Contract (WB-SUG-131)",
    "## Cancellation-Safe Cleanup for Non-Critical Workflows (WB-SUG-132)",
    "## Visualization Graph Triage Checkpoint (WB-SUG-133)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "run_summary.json",
    "run_summary.md",
    "GITHUB_STEP_SUMMARY",
    "cp2.run_summary.v1",
    "::notice",
    "::warning",
    "::error",
    "gh run rerun <run-id> --failed --debug",
    "rerun_debug_cmd",
    "gh workflow disable",
    "gh workflow enable",
    "WORKFLOW_HEALTH_BOARD.md",
    "if: ${{ cancelled() }}",
    "clean_cutover_artifacts.py",
    "visualization graph",
    "upstream failed node",
)

REQUIRED_FILES: tuple[Path, ...] = (
    Path("scripts/check_workflow_operator_handoff_policy.py"),
    Path("scripts/check_workflow_run_summary_wiring.py"),
    Path("scripts/generate_run_summary.py"),
    Path("scripts/run_quality_gates.py"),
    Path("docs/research/CP_RUNBOOK_COMMANDS.md"),
    Path("docs/research/WORKFLOW_HEALTH_BOARD.md"),
    Path(".github/workflows/nightly-evals.yml"),
    Path(".github/workflows/reusable-policy-review.yml"),
    Path(".github/workflows/reusable-scorecards.yml"),
)

RUN_SUMMARY_SCRIPT_TOKENS: tuple[str, ...] = (
    "GITHUB_STEP_SUMMARY",
    "Run Summary Contract (cp2.run_summary.v1)",
    "rerun_debug_cmd",
)

QUALITY_GATES_SCRIPT_TOKENS: tuple[str, ...] = (
    "_emit_annotation(",
    "\"notice\"",
    "\"warning\"",
    "\"error\"",
)

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Rerun Failed with Debug",
    "gh run rerun <run-id> --failed --debug",
    "## Pause Non-Critical Workflows",
    "gh workflow disable \"Nightly Evals\"",
    "gh workflow enable \"Nightly Evals\"",
    "## Visualization Graph First-Pass Triage",
    "gh run view <run-id> --repo <owner/repo> --web",
)

HEALTH_BOARD_TOKENS: tuple[str, ...] = (
    "actions/workflows/ci.yml/badge.svg",
    "actions/workflows/size-check.yml/badge.svg",
    "actions/workflows/nightly-evals.yml/badge.svg",
    "actions/workflows/policy-review.yml/badge.svg",
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): (
        "python3 scripts/check_workflow_operator_handoff_policy.py",
    ),
    Path(".github/workflows/size-check.yml"): (
        "python3 scripts/check_workflow_operator_handoff_policy.py",
    ),
}

CLEANUP_WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/nightly-evals.yml"): (
        "if: ${{ cancelled() }}",
        "python3 scripts/clean_cutover_artifacts.py --retention-class short --dry-run",
    ),
    Path(".github/workflows/reusable-policy-review.yml"): (
        "if: ${{ cancelled() }}",
        "python3 scripts/clean_cutover_artifacts.py --retention-class short --dry-run",
    ),
    Path(".github/workflows/reusable-scorecards.yml"): (
        "if: ${{ cancelled() }}",
        "python3 scripts/clean_cutover_artifacts.py --retention-class short --dry-run",
    ),
}


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
        if not (root / relative).exists():
            issues.append(f"missing required file: {relative.as_posix()}")

    issues.extend(
        _check_file_tokens(
            root / RUN_SUMMARY_SCRIPT,
            RUN_SUMMARY_SCRIPT_TOKENS,
            RUN_SUMMARY_SCRIPT.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / QUALITY_GATES_SCRIPT,
            QUALITY_GATES_SCRIPT_TOKENS,
            QUALITY_GATES_SCRIPT.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / RUNBOOK_DOC,
            REQUIRED_RUNBOOK_TOKENS,
            RUNBOOK_DOC.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / HEALTH_BOARD_DOC,
            HEALTH_BOARD_TOKENS,
            HEALTH_BOARD_DOC.as_posix(),
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
    for workflow_path, tokens in CLEANUP_WORKFLOW_TOKENS.items():
        issues.extend(
            _check_file_tokens(
                root / workflow_path,
                tokens,
                workflow_path.as_posix(),
            )
        )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate workflow operator handoff/recovery policy contract."
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
        print("[fail] workflow operator handoff/recovery policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] workflow operator handoff/recovery policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {HEALTH_BOARD_DOC.as_posix()}")
    print(f"  - {RUN_SUMMARY_SCRIPT.as_posix()}")
    print(f"  - {QUALITY_GATES_SCRIPT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
