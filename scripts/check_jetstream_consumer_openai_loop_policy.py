#!/usr/bin/env python3
"""Validate JetStream consumer and OpenAI loop policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
COMPACTION_SCRIPT = Path("scripts/evaluate_openai_compaction_threshold.py")
BUDGET_SCRIPT = Path("scripts/openai_budget_preflight.py")
SLO_SCRIPT = Path("scripts/evaluate_background_task_slo.py")
JETSTREAM_PROFILE_SCRIPT = Path("scripts/evaluate_jetstream_consumer_profile.py")
ADVISORY_TEMPLATE = Path("docs/research/templates/JETSTREAM_ADVISORY_WEEKLY_REVIEW_TEMPLATE.md")
STRUCTURED_OUTPUT_TEMPLATE = Path(
    "docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json"
)
JETSTREAM_BASELINE_TEMPLATE = Path(
    "docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md"
)
PROMPT_OBJECT_TEMPLATE = Path(
    "docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md"
)
COMPACTION_RESUME_TEMPLATE = Path(
    "docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md"
)

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Pull Consumer Default for Campaign Workloads (WB-SUG-105)",
    "## Critical AckSync Delivery Policy (WB-SUG-106)",
    "## Poison-Message MaxDeliver Exhaustion Policy (WB-SUG-107)",
    "## OpenAI Background-Mode Terminal-State Contract (WB-SUG-108)",
    "## Automatic Compaction Threshold Trigger (WB-SUG-109)",
    "## Default previous_response_id Chaining (WB-SUG-110)",
    "## OpenAI Budget Alarm + Hard-Cap Preflight (WB-SUG-111)",
    "## JetStream Advisories Ops Stream and Weekly Review (WB-SUG-119)",
    "## Consumer Class Defaults by Workload (WB-SUG-120)",
    "## Redelivery Baseline by Workload Type (WB-SUG-121)",
    "## Structured Outputs for Terminal Reports (WB-SUG-122)",
    "## Automatic Compaction Threshold Contract (WB-SUG-123)",
    "## Background Task Timeout and Cancellation SLO (WB-SUG-124)",
    "## JetStream Baseline Profiles by Workload (WB-SUG-135)",
    "## Explicit Redelivery Backoff Arrays (WB-SUG-136)",
    "## DLQ Contract from MaxDeliver Advisories (WB-SUG-137)",
    "## OpenAI Prompt Object Versioning Contract (WB-SUG-138)",
    "## Prompt Cache Key Contract by Campaign Family (WB-SUG-139)",
    "## Compaction and Resume Playbook Contract (WB-SUG-140)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "pull mode",
    "AckSync",
    "MaxDeliver",
    "quarantine",
    "Background-mode",
    "completed",
    "failed",
    "cancelled",
    "expired",
    "/responses/compact",
    "`previous_response_id`",
    "staging",
    "production",
    "hard caps",
    "retained ops stream",
    "weekly",
    "pull + durable",
    "ordered mode",
    "AckWait",
    "MaxDeliver",
    "Structured Outputs",
    "parallel_tool_calls: false",
    "timeout SLO",
    "cancellation",
    "MaxAckPending",
    "backoff arrays",
    "DLQ",
    "message sequence",
    "prompt object",
    "prompt version",
    "prompt_cache_key",
    "Compaction-and-resume",
    "checkpoint",
)

REQUIRED_FILES: tuple[Path, ...] = (
    Path("scripts/check_jetstream_consumer_openai_loop_policy.py"),
    Path("scripts/evaluate_openai_compaction_threshold.py"),
    Path("scripts/openai_budget_preflight.py"),
    Path("scripts/evaluate_background_task_slo.py"),
    Path("scripts/evaluate_jetstream_consumer_profile.py"),
    Path("docs/research/templates/JETSTREAM_ADVISORY_WEEKLY_REVIEW_TEMPLATE.md"),
    Path("docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json"),
    Path("docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md"),
    Path("docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md"),
    Path("docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md"),
)

COMPACTION_TOKENS: tuple[str, ...] = (
    "evaluate_compaction",
    "/responses/compact",
    "recommended_action",
)

BUDGET_TOKENS: tuple[str, ...] = (
    "evaluate_budget_preflight",
    "project_tier",
    "hard_block",
    "alarm_threshold",
)

SLO_TOKENS: tuple[str, ...] = (
    "evaluate_background_task_slo",
    "timeout_breach",
    "slo_violation",
    "recommended_action",
)

JETSTREAM_PROFILE_TOKENS: tuple[str, ...] = (
    "evaluate_consumer_profile",
    "max_ack_pending",
    "backoff_seconds",
    "dlq_on_max_deliver",
)

ADVISORY_TEMPLATE_TOKENS: tuple[str, ...] = (
    "JetStream Advisory Weekly Review",
    "Ops stream",
    "Critical advisories",
)

STRUCTURED_OUTPUT_TEMPLATE_TOKENS: tuple[str, ...] = (
    "\"parallel_tool_calls\": false",
    "\"response_format\"",
    "\"json_schema\"",
)

JETSTREAM_BASELINE_TEMPLATE_TOKENS: tuple[str, ...] = (
    "Workload class",
    "MaxAckPending",
    "Backoff array",
    "DLQ target stream",
)

PROMPT_OBJECT_TEMPLATE_TOKENS: tuple[str, ...] = (
    "Prompt object id",
    "Prompt version",
    "`prompt_cache_key`",
    "Rollback version",
)

COMPACTION_RESUME_TEMPLATE_TOKENS: tuple[str, ...] = (
    "Compaction Checkpoint",
    "/responses/compact",
    "Resume Contract",
    "`previous_response_id`",
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): (
        "python3 scripts/check_jetstream_consumer_openai_loop_policy.py",
    ),
    Path(".github/workflows/size-check.yml"): (
        "python3 scripts/check_jetstream_consumer_openai_loop_policy.py",
    ),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## JetStream Consumer and OpenAI Loop Policy",
    "python3 scripts/check_jetstream_consumer_openai_loop_policy.py",
    "python3 scripts/evaluate_openai_compaction_threshold.py --current-ratio 0.84 --threshold 0.80",
    "python3 scripts/openai_budget_preflight.py --project-tier production --current-spend 950 --cap 1000 --alarm-threshold 0.9",
    "python3 scripts/evaluate_background_task_slo.py --duration-seconds 450 --timeout-seconds 600 --cancelled false",
    "python3 scripts/evaluate_jetstream_consumer_profile.py --workload critical",
    "cat docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json",
    "cat docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md",
    "cat docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md",
    "cat docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md",
    "cat docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md",
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
            root / COMPACTION_SCRIPT,
            COMPACTION_TOKENS,
            COMPACTION_SCRIPT.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / BUDGET_SCRIPT,
            BUDGET_TOKENS,
            BUDGET_SCRIPT.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / SLO_SCRIPT,
            SLO_TOKENS,
            SLO_SCRIPT.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / JETSTREAM_PROFILE_SCRIPT,
            JETSTREAM_PROFILE_TOKENS,
            JETSTREAM_PROFILE_SCRIPT.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / ADVISORY_TEMPLATE,
            ADVISORY_TEMPLATE_TOKENS,
            ADVISORY_TEMPLATE.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / STRUCTURED_OUTPUT_TEMPLATE,
            STRUCTURED_OUTPUT_TEMPLATE_TOKENS,
            STRUCTURED_OUTPUT_TEMPLATE.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / JETSTREAM_BASELINE_TEMPLATE,
            JETSTREAM_BASELINE_TEMPLATE_TOKENS,
            JETSTREAM_BASELINE_TEMPLATE.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / PROMPT_OBJECT_TEMPLATE,
            PROMPT_OBJECT_TEMPLATE_TOKENS,
            PROMPT_OBJECT_TEMPLATE.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / COMPACTION_RESUME_TEMPLATE,
            COMPACTION_RESUME_TEMPLATE_TOKENS,
            COMPACTION_RESUME_TEMPLATE.as_posix(),
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
        description="Validate JetStream consumer/OpenAI loop policy contract."
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
        print("[fail] jetstream consumer/openai loop policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] jetstream consumer/openai loop policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {COMPACTION_SCRIPT.as_posix()}")
    print(f"  - {BUDGET_SCRIPT.as_posix()}")
    print(f"  - {SLO_SCRIPT.as_posix()}")
    print(f"  - {JETSTREAM_PROFILE_SCRIPT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
