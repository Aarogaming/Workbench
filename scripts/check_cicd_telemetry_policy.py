#!/usr/bin/env python3
"""Validate CICD telemetry and error taxonomy policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/CICD_TELEMETRY_ERROR_TAXONOMY_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
TAXONOMY_SCRIPT = Path("scripts/select_failure_taxonomy.py")
TEMPLATE_PATH = Path("docs/research/templates/CICD_ERROR_TYPE_TAXONOMY_TEMPLATE.md")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## OpenTelemetry CICD Semantic Conventions (WB-SUG-088)",
    "## CICD Error Taxonomy Contract (WB-SUG-089)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "OpenTelemetry",
    "cicd.run.id",
    "`error.type`",
    "infra",
    "script",
    "policy",
    "artifact",
    "human_gate",
    "supply_chain",
)

REQUIRED_TEMPLATE_TOKENS: tuple[str, ...] = (
    "error.type",
    "`infra`",
    "`script`",
    "`policy`",
    "`artifact`",
    "`human_gate`",
    "`supply_chain`",
)

REQUIRED_TAXONOMY_TOKENS: tuple[str, ...] = (
    "supply_chain",
    "policy",
    "artifact",
    "human_gate",
    "infra",
    "script",
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): ("python3 scripts/check_cicd_telemetry_policy.py",),
    Path(".github/workflows/size-check.yml"): ("python3 scripts/check_cicd_telemetry_policy.py",),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## CICD Telemetry and Error Taxonomy",
    "python3 scripts/check_cicd_telemetry_policy.py",
    "python3 scripts/select_failure_taxonomy.py --workflow \"Workbench CI\" --job \"policy-review\"",
    "cat docs/research/CICD_TELEMETRY_ERROR_TAXONOMY_POLICY.md",
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

    issues.extend(
        _check_file_tokens(
            root / TEMPLATE_PATH,
            REQUIRED_TEMPLATE_TOKENS,
            TEMPLATE_PATH.as_posix(),
        )
    )
    if TEMPLATE_PATH.as_posix() not in content:
        issues.append(f"policy doc missing template link/reference: {TEMPLATE_PATH.as_posix()}")

    issues.extend(
        _check_file_tokens(
            root / TAXONOMY_SCRIPT,
            REQUIRED_TAXONOMY_TOKENS,
            TAXONOMY_SCRIPT.as_posix(),
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
        description="Validate CICD telemetry and error taxonomy policy contract."
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
        print("[fail] cicd telemetry/error taxonomy policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] cicd telemetry/error taxonomy policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {TEMPLATE_PATH.as_posix()}")
    print(f"  - {TAXONOMY_SCRIPT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
