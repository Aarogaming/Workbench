#!/usr/bin/env python3
"""Detect risky untrusted-context interpolation in workflow run shells."""

from __future__ import annotations

import argparse
from pathlib import Path


WORKFLOW_ROOT = Path(".github/workflows")

UNTRUSTED_CONTEXT_TOKENS: tuple[str, ...] = (
    "${{ github.event.pull_request.title",
    "${{ github.event.pull_request.body",
    "${{ github.event.issue.title",
    "${{ github.event.issue.body",
    "${{ github.event.comment.body",
    "${{ github.event.head_commit.message",
)


def _indent(raw_line: str) -> int:
    return len(raw_line) - len(raw_line.lstrip(" "))


def _contains_untrusted_context(line: str) -> str | None:
    for token in UNTRUSTED_CONTEXT_TOKENS:
        if token in line:
            return token
    return None


def scan_workflow_content(content: str, workflow_label: str) -> list[str]:
    issues: list[str] = []
    lines = content.splitlines()
    in_run_block = False
    run_block_indent = 0

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        indent = _indent(raw)

        if in_run_block and stripped and indent <= run_block_indent:
            in_run_block = False

        if in_run_block:
            token = _contains_untrusted_context(raw)
            if token:
                issues.append(
                    f"{workflow_label}:{line_no}: untrusted context token '{token}' used in run block"
                )

        if "run:" not in stripped:
            continue

        token = _contains_untrusted_context(raw)
        if token:
            issues.append(
                f"{workflow_label}:{line_no}: untrusted context token '{token}' used in run step"
            )

        if stripped.startswith("run: |") or stripped.startswith("run: >"):
            in_run_block = True
            run_block_indent = indent

    return issues


def scan_workflows(root: Path) -> list[str]:
    issues: list[str] = []
    workflow_dir = root / WORKFLOW_ROOT
    if not workflow_dir.exists():
        return [f"missing workflow directory: {WORKFLOW_ROOT.as_posix()}"]

    for workflow in sorted(workflow_dir.glob("*.yml")):
        issues.extend(scan_workflow_content(workflow.read_text(encoding="utf-8"), workflow.as_posix()))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check GitHub workflow files for script-injection patterns."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = scan_workflows(root)
    if issues:
        print("[fail] workflow script-injection check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    workflow_count = len(list((root / WORKFLOW_ROOT).glob("*.yml")))
    print(f"[ok] workflow script-injection check workflows={workflow_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
