#!/usr/bin/env python3
"""Validate JetStream/OpenAI campaign guardrails policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
BACKOFF_HELPER = Path("scripts/openai_retry_backoff.py")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## JetStream KV Lease Coordination (WB-SUG-090)",
    "## JetStream Dedupe + Double-Ack Delivery (WB-SUG-091)",
    "## OpenAI Webhook Signature Verification (WB-SUG-092)",
    "## Conversation Continuity via previous_response_id (WB-SUG-093)",
    "## Mandatory Exponential Backoff + Jitter Wrapper (WB-SUG-094)",
    "## Project Separation and Budget Caps (WB-SUG-095)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "JetStream Key-Value",
    "`ttl`",
    "Watchers",
    "`Nats-Msg-Id`",
    "`AckSync`",
    "signature verification",
    "`previous_response_id`",
    "exponential backoff",
    "jitter",
    "staging",
    "production",
    "hard caps",
)

REQUIRED_FILES: tuple[Path, ...] = (
    Path("scripts/check_jetstream_openai_campaign_policy.py"),
    Path("scripts/openai_retry_backoff.py"),
)

BACKOFF_HELPER_TOKENS: tuple[str, ...] = (
    "compute_backoff_schedule",
    "random.Random",
    "2 ** attempt",
    "jitter_ratio",
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): (
        "python3 scripts/check_jetstream_openai_campaign_policy.py",
    ),
    Path(".github/workflows/size-check.yml"): (
        "python3 scripts/check_jetstream_openai_campaign_policy.py",
    ),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## JetStream and OpenAI Campaign Guardrails",
    "python3 scripts/check_jetstream_openai_campaign_policy.py",
    "python3 scripts/openai_retry_backoff.py --attempts 5 --base-delay 1 --max-delay 30 --jitter-ratio 0.2 --seed 42",
    "cat docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md",
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

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            issues.append(f"missing required file: {relative.as_posix()}")

    issues.extend(
        _check_file_tokens(
            root / BACKOFF_HELPER,
            BACKOFF_HELPER_TOKENS,
            BACKOFF_HELPER.as_posix(),
        )
    )

    for workflow_path, tokens in WORKFLOW_TOKENS.items():
        issues.extend(
            _check_file_tokens(
                root / workflow_path,
                tokens,
                workflow_path.as_posix(),
            )
        )

    issues.extend(
        _check_file_tokens(
            root / RUNBOOK_DOC,
            REQUIRED_RUNBOOK_TOKENS,
            RUNBOOK_DOC.as_posix(),
        )
    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate JetStream/OpenAI campaign guardrails policy contract."
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
        print("[fail] jetstream/openai campaign policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] jetstream/openai campaign policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {BACKOFF_HELPER.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
