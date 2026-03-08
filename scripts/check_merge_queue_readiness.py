#!/usr/bin/env python3
"""Validate merge-queue readiness for required CI checks."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_WORKFLOWS: tuple[str, ...] = (
    ".github/workflows/ci.yml",
    ".github/workflows/size-check.yml",
)

SENTINEL_WORKFLOW = Path(".github/workflows/required-check-sentinel.yml")

REQUIRED_SENTINEL_TOKENS: tuple[str, ...] = (
    "name: Required Check Sentinel",
    "pull_request:",
    "merge_group:",
    "jobs:",
    "sentinel:",
    "Always pass sentinel",
)


def _has_merge_group_trigger(content: str) -> bool:
    return "merge_group:" in content


def check_merge_queue_readiness(root: Path) -> list[str]:
    issues: list[str] = []

    for relative in REQUIRED_WORKFLOWS:
        target = root / relative
        if not target.exists():
            issues.append(f"missing required workflow: {relative}")
            continue
        content = target.read_text(encoding="utf-8")
        if not _has_merge_group_trigger(content):
            issues.append(f"{relative}: missing merge_group trigger")

    sentinel = root / SENTINEL_WORKFLOW
    if not sentinel.exists():
        issues.append(f"missing sentinel workflow: {SENTINEL_WORKFLOW.as_posix()}")
        return issues

    sentinel_content = sentinel.read_text(encoding="utf-8")
    for token in REQUIRED_SENTINEL_TOKENS:
        if token not in sentinel_content:
            issues.append(
                f"{SENTINEL_WORKFLOW.as_posix()}: missing required token '{token}'"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate merge-queue trigger parity and required-check sentinel workflow."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_merge_queue_readiness(root)
    if issues:
        print("[fail] merge queue readiness check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] merge queue readiness check")
    for relative in REQUIRED_WORKFLOWS:
        print(f"  - {relative}")
    print(f"  - {SENTINEL_WORKFLOW.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
