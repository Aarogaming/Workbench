#!/usr/bin/env python3
"""Validate offline attestation verification wiring in attestation workflow."""

from __future__ import annotations

import argparse
from pathlib import Path


WORKFLOW_PATH = ".github/workflows/verify-nightly-attestations.yml"
OFFLINE_INPUT = "offline_bundle_path:"
PREFLIGHT_STEP = "Offline bundle preflight"
VERIFY_STEP = "Verify artifact attestations"
PREFLIGHT_IF = "if: ${{ github.event_name == 'workflow_dispatch' && inputs.offline_bundle_path != '' }}"
PREFLIGHT_TOKENS: tuple[str, ...] = (
    '[ ! -f "${{ inputs.offline_bundle_path }}" ]',
    "offline bundle file",
)
VERIFY_TOKENS: tuple[str, ...] = (
    "--bundle",
    "inputs.offline_bundle_path",
    '"${BUNDLE_ARGS[@]}"',
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

    if OFFLINE_INPUT not in content:
        issues.append(f"{workflow_label}: missing workflow_dispatch input '{OFFLINE_INPUT}'")

    preflight_blocks = _step_blocks(lines, PREFLIGHT_STEP)
    if not preflight_blocks:
        issues.append(f"{workflow_label}: missing step '{PREFLIGHT_STEP}'")
    else:
        if not any(any(PREFLIGHT_IF in line for line in block) for block in preflight_blocks):
            issues.append(f"{workflow_label}: step '{PREFLIGHT_STEP}' missing expected condition")
        for token in PREFLIGHT_TOKENS:
            if not any(any(token in line for line in block) for block in preflight_blocks):
                issues.append(
                    f"{workflow_label}: step '{PREFLIGHT_STEP}' missing expected token '{token}'"
                )

    verify_blocks = _step_blocks(lines, VERIFY_STEP)
    if not verify_blocks:
        issues.append(f"{workflow_label}: missing step '{VERIFY_STEP}'")
    else:
        for token in VERIFY_TOKENS:
            if not any(any(token in line for line in block) for block in verify_blocks):
                issues.append(
                    f"{workflow_label}: step '{VERIFY_STEP}' missing expected token '{token}'"
                )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check offline attestation verification wiring."
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
