#!/usr/bin/env python3
"""Validate artifact digest capture and verification workflow wiring."""

from __future__ import annotations

import argparse
from pathlib import Path


NIGHTLY_WORKFLOW = ".github/workflows/nightly-evals.yml"
VERIFY_WORKFLOW = ".github/workflows/verify-nightly-attestations.yml"


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


def _check_block_tokens(
    content: str,
    workflow_label: str,
    step_name: str,
    tokens: tuple[str, ...],
) -> list[str]:
    issues: list[str] = []
    lines = content.splitlines()
    blocks = _step_blocks(lines, step_name)
    if not blocks:
        return [f"{workflow_label}: missing step '{step_name}'"]
    for token in tokens:
        if not any(any(token in line for line in block) for block in blocks):
            issues.append(
                f"{workflow_label}: step '{step_name}' missing expected token '{token}'"
            )
    return issues


def check_nightly_workflow(content: str, workflow_label: str) -> list[str]:
    issues: list[str] = []
    issues.extend(
        _check_block_tokens(
            content,
            workflow_label,
            "Generate artifact digest report",
            (
                "scripts/generate_artifact_digest_report.py",
                "--artifact eval_report_json=docs/reports/eval_report.json",
                "--artifact eval_report_md=docs/reports/eval_report.md",
                "--output docs/reports/artifact_digest_report.json",
            ),
        )
    )
    issues.extend(
        _check_block_tokens(
            content,
            workflow_label,
            "Upload eval artifacts",
            ("docs/reports/artifact_digest_report.json",),
        )
    )
    return issues


def check_verify_workflow(content: str, workflow_label: str) -> list[str]:
    issues: list[str] = []
    issues.extend(
        _check_block_tokens(
            content,
            workflow_label,
            "Verify artifact digests",
            (
                "scripts/verify_artifact_digests.py",
                "--report attested_artifacts/artifact_digest_report.json",
                "--artifact eval_report_json=attested_artifacts/eval_report.json",
                "--artifact eval_report_md=attested_artifacts/eval_report.md",
                "--json-out docs/reports/artifact_digest_verify_report.json",
            ),
        )
    )
    issues.extend(
        _check_block_tokens(
            content,
            workflow_label,
            "Upload attestation verify report",
            ("docs/reports/artifact_digest_verify_report.json",),
        )
    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check artifact digest workflow wiring."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    checks = (
        (NIGHTLY_WORKFLOW, check_nightly_workflow),
        (VERIFY_WORKFLOW, check_verify_workflow),
    )

    all_issues: list[str] = []
    for relative, checker in checks:
        path = root / relative
        if not path.exists():
            issue = f"{relative}: file not found"
            all_issues.append(issue)
            print(f"[fail] {relative}")
            print(f"  - {issue}")
            continue
        issues = checker(path.read_text(encoding="utf-8"), relative)
        if issues:
            all_issues.extend(issues)
            print(f"[fail] {relative}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[ok] {relative}")

    if all_issues:
        print(f"[summary] workflows={len(checks)} failed={len(all_issues)}")
        return 1

    print(f"[summary] workflows={len(checks)} failed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
