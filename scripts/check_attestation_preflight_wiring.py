#!/usr/bin/env python3
"""Validate GH CLI version preflight wiring for attestation workflow."""

from __future__ import annotations

import argparse
from pathlib import Path


WORKFLOW_PATH = ".github/workflows/verify-nightly-attestations.yml"
REQUIRED_STEP = "GH CLI minimum version preflight"
REQUIRED_IF = "if: ${{ github.event.repository.private == false }}"
REQUIRED_TOKENS: tuple[str, ...] = (
    "scripts/check_gh_cli_version.py",
    "--min-version 2.50.0",
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
    issues: list[str] = []
    lines = content.splitlines()
    blocks = _step_blocks(lines, REQUIRED_STEP)
    if not blocks:
        return [f"{workflow_label}: missing step '{REQUIRED_STEP}'"]

    if not any(any(REQUIRED_IF in line for line in block) for block in blocks):
        issues.append(f"{workflow_label}: step '{REQUIRED_STEP}' missing expected condition")

    for token in REQUIRED_TOKENS:
        if not any(any(token in line for line in block) for block in blocks):
            issues.append(
                f"{workflow_label}: step '{REQUIRED_STEP}' missing expected token '{token}'"
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check attestation workflow GH CLI preflight step wiring."
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
