#!/usr/bin/env python3
"""Validate OpenAI async execution policy document contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/OPENAI_ASYNC_EXECUTION_POLICY.md")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Background-Mode Webhook Worker Pattern",
    "## Webhook Signature Verification",
    "## Prompt-Caching Design Policy",
    "## Flex Processing Routing Policy",
    "## Retry and Terminal-State Handling",
    "## Required Local Artifacts",
)

REQUIRED_SNIPPETS: tuple[str, ...] = (
    "idempotency key",
    "terminal state",
    "`prompt_cache_key`",
    "flex routing",
    "exponential backoff",
    "completed",
    "failed",
    "cancelled",
    "expired",
)


def check_policy(root: Path) -> list[str]:
    issues: list[str] = []
    path = root / POLICY_DOC
    if not path.exists():
        return [f"missing policy doc: {POLICY_DOC.as_posix()}"]

    content = path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            issues.append(f"missing policy heading in {POLICY_DOC.as_posix()}: {heading}")
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in content:
            issues.append(f"missing policy snippet in {POLICY_DOC.as_posix()}: {snippet}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate OpenAI async execution policy coverage."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_policy(root)
    if issues:
        print("[fail] openai async policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] openai async policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
