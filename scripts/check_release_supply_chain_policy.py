#!/usr/bin/env python3
"""Validate release and supply-chain policy contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Attestation Lifecycle Pruning (WB-SUG-082)",
    "## Immutable Release Publish Flow (WB-SUG-083)",
    "## Release Integrity Verification Commands (WB-SUG-084)",
    "## Toolsmith Reusable Workflow Sharing Boundary (WB-SUG-085)",
    "## Dependabot Security Update Grouping (WB-SUG-086)",
    "## Org Actions Policy Baseline (WB-SUG-087)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "attestation inventory",
    "immutable releases",
    "draft-first",
    "gh release verify",
    "gh release verify-asset",
    "Toolsmith",
    "log visibility",
    "full-length commit SHA",
    "admin-managed control",
)

REQUIRED_FILES: tuple[Path, ...] = (
    Path(".github/dependabot.yml"),
    Path(".github/workflows/verify-nightly-attestations.yml"),
    Path("docs/research/ATTESTATION_OFFLINE_VERIFICATION_PLAYBOOK.md"),
    Path("scripts/check_release_supply_chain_policy.py"),
)

DEPENDABOT_TOKENS: tuple[str, ...] = (
    "groups:",
    "actions-security:",
    "applies-to: security-updates",
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/verify-nightly-attestations.yml"): (
        "Offline bundle preflight",
        "Verify artifact attestations",
        "Verify artifact digests",
    ),
    Path(".github/workflows/ci.yml"): ("python3 scripts/check_release_supply_chain_policy.py",),
    Path(".github/workflows/size-check.yml"): ("python3 scripts/check_release_supply_chain_policy.py",),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Release and Supply Chain Policy",
    "python3 scripts/check_release_supply_chain_policy.py",
    "cat docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md",
    "gh release verify <tag>",
    "gh release verify-asset <tag> <asset-name>",
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
            root / Path(".github/dependabot.yml"),
            DEPENDABOT_TOKENS,
            ".github/dependabot.yml",
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
        description="Validate release and supply-chain policy contract."
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
        print("[fail] release/supply-chain policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] release/supply-chain policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    for relative in REQUIRED_FILES:
        print(f"  - {relative.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
