#!/usr/bin/env python3
"""Validate workflow-level branch-aware concurrency in critical workflows."""

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

REQUIRED_GROUP = (
    "group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}"
)
REQUIRED_CANCEL = "cancel-in-progress: true"


def check_workflow_content(content: str, workflow_label: str) -> list[str]:
    issues: list[str] = []
    lines = content.splitlines()
    stripped = [line.strip() for line in lines]

    concurrency_idx = next((idx for idx, line in enumerate(stripped) if line == "concurrency:"), None)
    jobs_idx = next((idx for idx, line in enumerate(stripped) if line == "jobs:"), None)

    if concurrency_idx is None:
        return [f"{workflow_label}: missing top-level concurrency block"]

    if jobs_idx is not None and concurrency_idx > jobs_idx:
        issues.append(f"{workflow_label}: concurrency block must be defined before jobs")

    search_end = jobs_idx if jobs_idx is not None else len(stripped)
    concurrency_region = stripped[concurrency_idx:search_end]

    if REQUIRED_GROUP not in concurrency_region:
        issues.append(
            f"{workflow_label}: missing branch-aware concurrency group '{REQUIRED_GROUP}'"
        )
    if REQUIRED_CANCEL not in concurrency_region:
        issues.append(
            f"{workflow_label}: missing deterministic cancellation policy '{REQUIRED_CANCEL}'"
        )
    return issues


def check_workflow_file(path: Path) -> list[str]:
    if not path.exists():
        return [f"{path}: file not found"]
    return check_workflow_content(path.read_text(encoding="utf-8"), str(path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate workflow-level branch-aware concurrency policy."
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
