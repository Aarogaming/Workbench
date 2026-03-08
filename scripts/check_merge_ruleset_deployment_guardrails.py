#!/usr/bin/env python3
"""Validate merge/ruleset/deployment guardrail policy and local ownership contract."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md")
CODEOWNERS_PATH = Path(".github/CODEOWNERS")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
PROMOTION_WATCHTOWER_SCRIPT = Path("scripts/evaluate_promotion_watchtower.py")
RULESET_DRIFT_REPORT = Path("docs/reports/ruleset_drift_audit.json")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Strict Required Status Checks (WB-SUG-057)",
    "## Staging Deployment Requirement (WB-SUG-058)",
    "## Environment Reviewer and Self-Review Guard (WB-SUG-059)",
    "## Custom Deployment Protection Rule Integration (WB-SUG-113)",
    "## Foreman Bench Advisory Protection Service Contract (WB-SUG-134)",
    "## Environment Wait Timer and Required Reviewer Policy (WB-SUG-114)",
    "## Deployment Branch/Tag Allowlist Policy (WB-SUG-115)",
    "## Disable Admin Bypass for Guarded Environments (WB-SUG-116)",
    "## Required Check Source Pinning (WB-SUG-045 and WB-SUG-065)",
    "## Ruleset Required Code-Scanning Results (WB-SUG-060)",
    "## Ruleset Path and File-Size Restrictions (WB-SUG-061)",
    "## Linear History and Merge Method Alignment (WB-SUG-062)",
    "## Signed-Commit Pilot Rollout (WB-SUG-063)",
    "## Self-Hosted Runner Group and Repository Boundary Policy (WB-SUG-064)",
    "## CODEOWNERS Control-Plane Stewardship (WB-SUG-046 and WB-SUG-066)",
    "## Merge-Queue Timeout Triage Playbook (WB-SUG-067)",
    "## Argus Watchtower Multi-Signal Promotion Gate (WB-SUG-125)",
    "## Janus Gate Two-Stage Promotion Policy (WB-SUG-126)",
    "## Merge Queue Build Concurrency Tuning (WB-SUG-044)",
    "## Protected Environment Promotion Gate Contract (WB-SUG-047)",
    "## OIDC Deploy Identity Policy (WB-SUG-048)",
    "## Canary Rollout Policy for Workflow/Gate Changes (WB-SUG-049)",
    "## Steady-State Metrics and Chaos Drill Cadence (WB-SUG-050)",
    "## Merge Queue Timeout SLO Policy (WB-SUG-051)",
    "## Weekly Ruleset Drift Audit (WB-SUG-052)",
    "## Hephaestus Seal Provenance Gate (WB-SUG-053)",
    "## Arsenal Dock Timed Merge Lane (WB-SUG-054)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "`main`",
    "`staging`",
    "prevent self-review",
    "custom protection rules",
    "JetStream advisories",
    "stream health",
    "wait timer",
    "required reviewers",
    "`release-*`",
    "`hotfix-*`",
    "admin bypass",
    "CodeQL Actions Security / analyze",
    "GitHub App source",
    "gh api repos/{owner}/{repo}/rulesets",
    "code-scanning results",
    "path restrictions",
    "file size restrictions",
    "linear history",
    "signed commits",
    "runner groups",
    "private-repo-only",
    "Removed from merge queue",
    "Required Check Sentinel",
    "CI pass",
    "provenance pass",
    "advisory health",
    "argus_watchtower_gate.json",
    "Stage 1 review gate",
    "Stage 2 runtime health gate",
    "janus_gate_evidence.json",
    "build concurrency",
    "OIDC",
    "id-token: write",
    "canary lane",
    "chaos drills",
    "timeout windows",
    "ruleset_drift_audit.json",
    "Hephaestus Seal",
    "timed merge windows",
    CODEOWNERS_PATH.as_posix(),
)

REQUIRED_CODEOWNERS_LINES: tuple[str, ...] = (
    "/.github/workflows/** @Aarogaming",
    "/scripts/check_*.py @Aarogaming",
    "/scripts/run_quality_gates.py @Aarogaming",
)

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Merge Ruleset and Deployment Guardrails",
    "python3 scripts/check_merge_ruleset_deployment_guardrails.py",
    "python3 scripts/evaluate_promotion_watchtower.py --ci-pass true --provenance-pass true --advisory-health healthy --review-approved true --runtime-health healthy",
    "gh api repos/{owner}/{repo}/rulesets --paginate > docs/reports/ruleset_drift_audit.json",
    "cat docs/reports/ruleset_drift_audit.json",
    f"cat {POLICY_DOC.as_posix()}",
)

REQUIRED_WATCHTOWER_SCRIPT_TOKENS: tuple[str, ...] = (
    "evaluate_promotion_readiness",
    "argus_watchtower_pass",
    "janus_gate_pass",
    "promotion_allowed",
    "blocked_reasons",
)

REQUIRED_RULESET_DRIFT_TOKENS: tuple[str, ...] = (
    "\"schema_version\": \"cp4b.ruleset_drift_audit.v1\"",
    "\"drift_detected\"",
    "\"notes\"",
)


def _check_doc(path: Path, required_tokens: tuple[str, ...], issue_prefix: str) -> list[str]:
    if not path.exists():
        return [f"missing required file: {path.as_posix()}"]
    content = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for token in required_tokens:
        if token not in content:
            issues.append(f"{issue_prefix}: missing token '{token}'")
    return issues


def check_guardrails(root: Path) -> list[str]:
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

    codeowners = root / CODEOWNERS_PATH
    if not codeowners.exists():
        issues.append(f"missing codeowners file: {CODEOWNERS_PATH.as_posix()}")
    else:
        codeowners_content = codeowners.read_text(encoding="utf-8")
        for line in REQUIRED_CODEOWNERS_LINES:
            if line not in codeowners_content:
                issues.append(
                    f"missing CODEOWNERS entry in {CODEOWNERS_PATH.as_posix()}: {line}"
                )

    issues.extend(
        _check_doc(
            root / RUNBOOK_DOC,
            REQUIRED_RUNBOOK_TOKENS,
            f"{RUNBOOK_DOC.as_posix()}",
        )
    )
    issues.extend(
        _check_doc(
            root / PROMOTION_WATCHTOWER_SCRIPT,
            REQUIRED_WATCHTOWER_SCRIPT_TOKENS,
            f"{PROMOTION_WATCHTOWER_SCRIPT.as_posix()}",
        )
    )
    issues.extend(
        _check_doc(
            root / RULESET_DRIFT_REPORT,
            REQUIRED_RULESET_DRIFT_TOKENS,
            f"{RULESET_DRIFT_REPORT.as_posix()}",
        )
    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate merge/ruleset/deployment guardrails policy and wiring."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_guardrails(root)
    if issues:
        print("[fail] merge/ruleset/deployment guardrails check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] merge/ruleset/deployment guardrails check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {CODEOWNERS_PATH.as_posix()}")
    print(f"  - {RUNBOOK_DOC.as_posix()}")
    print(f"  - {PROMOTION_WATCHTOWER_SCRIPT.as_posix()}")
    print(f"  - {RULESET_DRIFT_REPORT.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
