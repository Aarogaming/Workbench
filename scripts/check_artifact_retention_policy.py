#!/usr/bin/env python3
"""Validate artifact retention defaults for upload-artifact steps."""

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

RETENTION_DEFAULTS = {
    "short": 7,
    "standard": 30,
    "forensic": 90,
}

EXPLICIT_ARTIFACT_RETENTION: dict[str, int] = {
    "nightly-eval-report": RETENTION_DEFAULTS["standard"],
    "forge-gates-reports": RETENTION_DEFAULTS["standard"],
    "workflow-policy-reports": RETENTION_DEFAULTS["standard"],
    "scorecard-results": RETENTION_DEFAULTS["standard"],
    "attestation-verify-report": RETENTION_DEFAULTS["forensic"],
}


def _step_blocks(content: str) -> list[list[str]]:
    lines = content.splitlines()
    name_indexes = [
        idx for idx, line in enumerate(lines) if line.lstrip().startswith("- name:")
    ]
    blocks: list[list[str]] = []
    for idx in name_indexes:
        next_indexes = [value for value in name_indexes if value > idx]
        end = next_indexes[0] if next_indexes else len(lines)
        blocks.append(lines[idx:end])
    return blocks


def _parse_artifact_name(block: list[str]) -> str | None:
    for line in block:
        stripped = line.strip()
        if stripped.startswith("- name:"):
            continue
        if stripped.startswith("name:"):
            value = stripped.split(":", 1)[1].strip()
            if value:
                return value
    return None


def _parse_retention_days(block: list[str]) -> int | None:
    for line in block:
        stripped = line.strip()
        if stripped.startswith("retention-days:"):
            raw = stripped.split(":", 1)[1].strip()
            if raw.isdigit():
                return int(raw)
            return None
    return None


def expected_retention_days(artifact_name: str) -> int | None:
    if artifact_name.startswith("run-summary-"):
        return RETENTION_DEFAULTS["short"]
    return EXPLICIT_ARTIFACT_RETENTION.get(artifact_name)


def check_workflow_content(content: str, workflow_label: str) -> list[str]:
    issues: list[str] = []
    blocks = _step_blocks(content)

    upload_blocks = [
        block for block in blocks if any("uses: actions/upload-artifact@" in line for line in block)
    ]
    if not upload_blocks:
        issues.append(f"{workflow_label}: no upload-artifact steps found")
        return issues

    for block in upload_blocks:
        step_header = block[0].strip() if block else "- name: <unknown>"
        artifact_name = _parse_artifact_name(block)
        if not artifact_name:
            issues.append(f"{workflow_label}: {step_header} missing artifact name in with: block")
            continue

        expected = expected_retention_days(artifact_name)
        if expected is None:
            issues.append(
                f"{workflow_label}: artifact '{artifact_name}' is not mapped to a retention class"
            )
            continue

        actual = _parse_retention_days(block)
        if actual is None:
            issues.append(
                f"{workflow_label}: artifact '{artifact_name}' missing numeric retention-days"
            )
            continue
        if actual != expected:
            issues.append(
                f"{workflow_label}: artifact '{artifact_name}' retention-days={actual} expected={expected}"
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check upload-artifact retention-days policy defaults."
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
        workflow = root / relative
        if not workflow.exists():
            issue = f"{relative}: file not found"
            all_issues.append(issue)
            print(f"[fail] {relative}")
            print(f"  - {issue}")
            continue
        issues = check_workflow_content(workflow.read_text(encoding="utf-8"), relative)
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
