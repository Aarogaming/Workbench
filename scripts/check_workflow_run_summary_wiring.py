#!/usr/bin/env python3
"""Validate run-summary failure wiring in critical workflows."""

from __future__ import annotations

import argparse
from pathlib import Path


CRITICAL_WORKFLOWS: tuple[str, ...] = (
    ".github/workflows/ci.yml",
    ".github/workflows/size-check.yml",
    ".github/workflows/codeql-actions-security.yml",
    ".github/workflows/nightly-evals.yml",
    ".github/workflows/reusable-forge-gates.yml",
    ".github/workflows/reusable-policy-review.yml",
    ".github/workflows/reusable-scorecards.yml",
    ".github/workflows/verify-nightly-attestations.yml",
)

REQUIRED_STEPS: tuple[str, ...] = (
    "Generate run summary",
    "Validate run summary",
    "Upload run summary artifact",
)

REQUIRED_IF = "if: ${{ failure() || cancelled() }}"
STEP_REQUIRED_TOKENS: dict[str, tuple[str, ...]] = {
    "Generate run summary": ("scripts/generate_run_summary.py", "--failure-taxonomy"),
    "Validate run summary": ("scripts/validate_run_summary.py",),
    "Upload run summary artifact": ("actions/upload-artifact@",),
}
STEP_OPTIONAL_TOKENS: dict[str, tuple[str, ...]] = {
    "Generate run summary": ("scripts/select_failure_taxonomy.py",),
}


def _step_line_indexes(lines: list[str], step_name: str) -> list[int]:
    needle = f"- name: {step_name}"
    return [idx for idx, line in enumerate(lines) if line.strip() == needle]


def _step_blocks(lines: list[str], step_name: str) -> list[list[str]]:
    indexes = _step_line_indexes(lines, step_name)
    name_indexes = [
        idx for idx, line in enumerate(lines) if line.lstrip().startswith("- name:")
    ]
    blocks: list[list[str]] = []
    for idx in indexes:
        next_indexes = [value for value in name_indexes if value > idx]
        end = next_indexes[0] if next_indexes else len(lines)
        blocks.append(lines[idx:end])
    return blocks


def check_workflow_content(content: str, workflow_label: str) -> list[str]:
    issues: list[str] = []
    lines = content.splitlines()

    for step_name in REQUIRED_STEPS:
        blocks = _step_blocks(lines, step_name)
        if not blocks:
            issues.append(f"{workflow_label}: missing step '{step_name}'")
            continue
        if not any(any(REQUIRED_IF in line for line in block) for block in blocks):
            issues.append(
                f"{workflow_label}: step '{step_name}' missing failure/cancelled condition"
            )
        required_tokens = STEP_REQUIRED_TOKENS.get(step_name, ())
        for token in required_tokens:
            if not any(any(token in line for line in block) for block in blocks):
                issues.append(
                    f"{workflow_label}: step '{step_name}' missing expected token '{token}'"
                )
        optional_tokens = STEP_OPTIONAL_TOKENS.get(step_name, ())
        for token in optional_tokens:
            if not any(any(token in line for line in block) for block in blocks):
                issues.append(
                    f"{workflow_label}: step '{step_name}' missing expected token '{token}'"
                )

    if "run_summary/run_summary.json" not in content:
        issues.append(f"{workflow_label}: missing run_summary JSON artifact path")
    if "run_summary/run_summary.md" not in content:
        issues.append(f"{workflow_label}: missing run_summary markdown artifact path")
    if "name: run-summary-" not in content:
        issues.append(f"{workflow_label}: missing run-summary artifact naming")

    return issues


def check_workflow_file(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: file not found"]
    return check_workflow_content(path.read_text(encoding="utf-8"), str(path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate run-summary failure wiring in critical workflow files."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    all_issues: list[str] = []
    for relative in CRITICAL_WORKFLOWS:
        workflow_path = root / relative
        issues = check_workflow_file(workflow_path)
        if issues:
            all_issues.extend(issues)
            print(f"[fail] {relative}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[ok] {relative}")

    if all_issues:
        print(f"[summary] workflows={len(CRITICAL_WORKFLOWS)} failed={len(all_issues)}")
        return 1

    print(f"[summary] workflows={len(CRITICAL_WORKFLOWS)} failed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
