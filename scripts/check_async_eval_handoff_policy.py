#!/usr/bin/env python3
"""Validate async eval routing and campaign handoff policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## OpenAI Batch Queue Routing (WB-SUG-078)",
    "## AI RMF Risk Register Contract (WB-SUG-079)",
    "## Daedalus Diagram Contract (WB-SUG-080)",
    "## Hermes Relay Handoff Packet Standard (WB-SUG-081)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "Batch API",
    "low-priority",
    "`Govern`",
    "`Map`",
    "`Measure`",
    "`Manage`",
    "planned path",
    "fallback branches",
    "escape hatch",
    "source lane",
    "destination lane",
    "acknowledgement",
)

TEMPLATE_REQUIREMENTS: dict[Path, tuple[str, ...]] = {
    Path("docs/research/templates/AI_RMF_RISK_REGISTER_TEMPLATE.md"): (
        "Govern",
        "Map",
        "Measure",
        "Manage",
        "Risk Owner",
    ),
    Path("docs/research/templates/DAEDALUS_DIAGRAM_TEMPLATE.md"): (
        "## Planned Path",
        "## Fallback Branches",
        "## Escape Hatch",
    ),
    Path("docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md"): (
        "## Relay Header",
        "## Current State",
        "## Required Next Commands",
        "## Acknowledgement",
    ),
}

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): ("python3 scripts/check_async_eval_handoff_policy.py",),
    Path(".github/workflows/size-check.yml"): ("python3 scripts/check_async_eval_handoff_policy.py",),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Async Eval and Campaign Handoff",
    "python3 scripts/check_async_eval_handoff_policy.py",
    "cat docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md",
    "cat docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md",
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

    for template_path, tokens in TEMPLATE_REQUIREMENTS.items():
        target = root / template_path
        if not target.exists():
            issues.append(f"missing template file: {template_path.as_posix()}")
            continue
        template_content = target.read_text(encoding="utf-8")
        for token in tokens:
            if token not in template_content:
                issues.append(
                    f"{template_path.as_posix()}: missing token '{token}'"
                )
        if template_path.as_posix() not in policy_content:
            issues.append(
                f"policy doc missing template link/reference: {template_path.as_posix()}"
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
        description="Validate async eval and campaign handoff policy contract."
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
        print("[fail] async eval/handoff policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] async eval/handoff policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    for template_path in TEMPLATE_REQUIREMENTS:
        print(f"  - {template_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
