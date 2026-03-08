#!/usr/bin/env python3
"""Validate attestation identity-policy wiring in attestation workflow."""

from __future__ import annotations

import argparse
from pathlib import Path


WORKFLOW_PATH = ".github/workflows/verify-nightly-attestations.yml"
REQUIRED_STEP = "Verify artifact attestations"
REQUIRED_TOKENS: tuple[str, ...] = (
    "scripts/verify_attestations.py",
    '--repo "${{ github.repository }}"',
    '--signer-workflow "${{ github.repository }}/.github/workflows/nightly-evals.yml"',
    '--predicate-type "https://slsa.dev/provenance/v1"',
)


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
    lines = content.splitlines()
    blocks = _step_blocks(lines, REQUIRED_STEP)
    if not blocks:
        return [f"{workflow_label}: missing step '{REQUIRED_STEP}'"]

    issues: list[str] = []
    for token in REQUIRED_TOKENS:
        if not any(any(token in line for line in block) for block in blocks):
            issues.append(
                f"{workflow_label}: step '{REQUIRED_STEP}' missing expected token '{token}'"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check attestation identity-policy wiring in verify workflow."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    workflow = root / WORKFLOW_PATH
    if not workflow.exists():
        print(f"[fail] missing workflow file: {workflow}")
        return 1

    issues = check_workflow_content(workflow.read_text(encoding="utf-8"), WORKFLOW_PATH)
    if issues:
        print(f"[fail] {WORKFLOW_PATH}")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(f"[ok] {WORKFLOW_PATH}")
    print("[summary] workflows=1 failed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
