#!/usr/bin/env python3
"""Validate event resilience and flow control policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Transactional Outbox Semantics (WB-SUG-074)",
    "## Consumer Idempotency Ledger (WB-SUG-075)",
    "## Circuit Breaker Wrapper Policy (WB-SUG-076)",
    "## Little's Law WIP Calibration (WB-SUG-077)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "write + publish",
    "`operation_id`",
    "replay-safe",
    "`closed`",
    "`open`",
    "`half-open`",
    "WIP = throughput * lead_time",
    "buffer",
)

REQUIRED_TEMPLATES: dict[Path, tuple[str, ...]] = {
    Path("docs/research/templates/OUTBOX_EVENT_RECORD_TEMPLATE.json"): (
        '"schema": "workbench.outbox_event.v1"',
        '"operation_id"',
        '"publish_state"',
    ),
    Path("docs/research/templates/IDEMPOTENCY_LEDGER_ENTRY_TEMPLATE.json"): (
        '"schema": "workbench.idempotency_ledger_entry.v1"',
        '"operation_id"',
        '"status"',
    ),
}

REQUIRED_FILES: tuple[Path, ...] = (
    Path("scripts/compute_littles_law_wip.py"),
    Path("scripts/check_event_resilience_policy.py"),
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): ("python3 scripts/check_event_resilience_policy.py",),
    Path(".github/workflows/size-check.yml"): ("python3 scripts/check_event_resilience_policy.py",),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Event Resilience and Flow Control",
    "python3 scripts/check_event_resilience_policy.py",
    "python3 scripts/compute_littles_law_wip.py --throughput-per-day 6 --lead-time-days 2 --buffer 1.15",
    "cat docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md",
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

    policy_content = policy_path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in policy_content:
            issues.append(f"missing policy heading in {POLICY_DOC.as_posix()}: {heading}")
    for snippet in REQUIRED_POLICY_SNIPPETS:
        if snippet not in policy_content:
            issues.append(f"missing policy snippet in {POLICY_DOC.as_posix()}: {snippet}")

    for template_path, tokens in REQUIRED_TEMPLATES.items():
        issues.extend(
            _check_file_tokens(
                root / template_path,
                tokens,
                template_path.as_posix(),
            )
        )
        if template_path.as_posix() not in policy_content:
            issues.append(
                f"policy doc missing template link/reference: {template_path.as_posix()}"
            )

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            issues.append(f"missing required file: {relative.as_posix()}")

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
        description="Validate event resilience and flow control policy contract."
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
        print("[fail] event resilience policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] event resilience policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    for template_path in REQUIRED_TEMPLATES:
        print(f"  - {template_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
