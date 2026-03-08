#!/usr/bin/env python3
"""Validate campaign wave operations policy and templates."""

from __future__ import annotations

import argparse
from pathlib import Path


POLICY_DOC = Path("docs/research/CAMPAIGN_WAVE_OPERATIONS_POLICY.md")

REQUIRED_POLICY_HEADINGS: tuple[str, ...] = (
    "## Lane WIP Limits",
    "## Ariadne Thread After-Action Template",
    "## Three-Phase Checklist",
    "## Start-Small Pilot Rollout Rule",
    "## Continuous Monitoring Loop",
    "## Blameless Postmortem Trigger Policy",
    "## Cursus Publicus Relay Model",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "| `A0` |",
    "| `A1` |",
    "| `A2` |",
    "| `A3` |",
    "| `A4` |",
    "| `A5` |",
    "| `A6` |",
    "| `A7` |",
    "| `A8` |",
    "single responsible conductor",
    "`sign-in`",
    "`time-out`",
    "`sign-out`",
    "mutationes",
    "mansiones",
)

TEMPLATE_REQUIREMENTS: dict[Path, tuple[str, ...]] = {
    Path("docs/research/templates/ARIADNE_THREAD_AFTER_ACTION_TEMPLATE.md"): (
        "## Planned Path",
        "## Actual Path",
        "## Deviations",
        "## Recovery Thread",
    ),
    Path("docs/research/templates/BLAMELESS_POSTMORTEM_TEMPLATE.md"): (
        "## Trigger",
        "## Impact Summary",
        "## Timeline",
        "## Action Items",
        "## Follow-Up Verification",
    ),
    Path("docs/research/templates/CURSUS_PUBLICUS_RELAY_TEMPLATE.md"): (
        "## Mutationes Quick Relay",
        "## Mansiones Full Checkpoint",
        "## Handoff Acknowledgement",
    ),
}


def check_campaign_wave_policy(root: Path) -> list[str]:
    issues: list[str] = []
    policy_path = root / POLICY_DOC
    if not policy_path.exists():
        return [f"missing policy doc: {POLICY_DOC.as_posix()}"]

    content = policy_path.read_text(encoding="utf-8")
    for heading in REQUIRED_POLICY_HEADINGS:
        if heading not in content:
            issues.append(f"missing policy heading in {POLICY_DOC.as_posix()}: {heading}")

    for snippet in REQUIRED_POLICY_SNIPPETS:
        if snippet not in content:
            issues.append(f"missing policy snippet in {POLICY_DOC.as_posix()}: {snippet}")

    for template_path, required_sections in TEMPLATE_REQUIREMENTS.items():
        target = root / template_path
        if not target.exists():
            issues.append(f"missing template file: {template_path.as_posix()}")
            continue
        template_content = target.read_text(encoding="utf-8")
        for section in required_sections:
            if section not in template_content:
                issues.append(
                    f"missing template section in {template_path.as_posix()}: {section}"
                )
        if template_path.as_posix() not in content:
            issues.append(
                f"policy doc missing template link/reference: {template_path.as_posix()}"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate campaign wave operations policy coverage."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_campaign_wave_policy(root)
    if issues:
        print("[fail] campaign wave policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] campaign wave policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    for template_path in TEMPLATE_REQUIREMENTS:
        print(f"  - {template_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
