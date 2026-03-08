#!/usr/bin/env python3
"""Validate dependency-review policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/DEPENDENCY_REVIEW_SUPPLY_CHAIN_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
CONFIG_FILE = Path(".github/dependency-review-config.yml")
WORKFLOW_FILE = Path(".github/workflows/dependency-review.yml")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Dependency Review Risk Threshold Policy (WB-SUG-112)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "fail-on-severity",
    "fail-on-scopes",
    "deny-group",
    ".github/dependency-review-config.yml",
)

CONFIG_TOKENS: tuple[str, ...] = (
    "fail-on-severity:",
    "fail-on-scopes:",
    "- runtime",
    "deny-packages:",
)

WORKFLOW_TOKENS: tuple[str, ...] = (
    "actions/dependency-review-action@",
    "config-file: .github/dependency-review-config.yml",
)

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Dependency Review Supply-Chain Policy",
    "python3 scripts/check_dependency_review_policy.py",
    "cat .github/dependency-review-config.yml",
    "cat docs/research/DEPENDENCY_REVIEW_SUPPLY_CHAIN_POLICY.md",
)


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
    content = policy_path.read_text(encoding="utf-8")

    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            issues.append(f"missing policy heading in {POLICY_DOC.as_posix()}: {heading}")
    for snippet in REQUIRED_POLICY_SNIPPETS:
        if snippet not in content:
            issues.append(f"missing policy snippet in {POLICY_DOC.as_posix()}: {snippet}")

    issues.extend(_check_file_tokens(root / CONFIG_FILE, CONFIG_TOKENS, CONFIG_FILE.as_posix()))
    issues.extend(
        _check_file_tokens(root / WORKFLOW_FILE, WORKFLOW_TOKENS, WORKFLOW_FILE.as_posix())
    )
    issues.extend(
        _check_file_tokens(root / RUNBOOK_DOC, REQUIRED_RUNBOOK_TOKENS, RUNBOOK_DOC.as_posix())
    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate dependency-review policy contract.")
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_policy(root)
    if issues:
        print("[fail] dependency review policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] dependency review policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {CONFIG_FILE.as_posix()}")
    print(f"  - {WORKFLOW_FILE.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
