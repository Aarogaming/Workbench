#!/usr/bin/env python3
"""Validate required CHIMERA V2 packet documents and mandatory sections."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_PACKET_SECTIONS: dict[str, tuple[str, ...]] = {
    "docs/research/CHIMERA_V2_CP2_OPERATOR_OBSERVABILITY_PACKET_2026-02-15.md": (
        "## Function Statement",
        "## CP2 Minimum Standard (Run Summary + Artifact Fetch)",
        "## <=1 Pass Implementation Slice (Delivered in CP2)",
        "## Acceptance Checks (CP2-P0)",
    ),
    "docs/research/CHIMERA_V2_CP4A_OPERATOR_READINESS_STATUS_2026-02-15.md": (
        "## Operator Canary Checklist",
        "## Rollback Communication Template",
        "## Required Local Artifact Links",
        "## Verification Commands and Outcomes",
    ),
    "docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md": (
        "## Objective",
        "## Owner + SLA Tracker",
        "## Escalation Rule",
    ),
    "docs/research/CP_RUNBOOK_COMMANDS.md": (
        "## Canary",
        "## Run Summary",
        "## Artifact Fetch + Index",
        "## Rollback Packet Prep",
    ),
}


def check_packets(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, required_sections in REQUIRED_PACKET_SECTIONS.items():
        packet_path = root / relative_path
        if not packet_path.exists():
            issues.append(f"missing required packet: {relative_path}")
            continue

        content = packet_path.read_text(encoding="utf-8")
        for section in required_sections:
            if section not in content:
                issues.append(f"missing section in {relative_path}: {section}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate required CHIMERA V2 research packet files and sections."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = (
        Path(args.root).resolve()
        if args.root
        else Path(__file__).resolve().parents[1]
    )
    issues = check_packets(root)
    if issues:
        print("[fail] CHIMERA packet check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] CHIMERA packet check")
    for relative_path in REQUIRED_PACKET_SECTIONS:
        print(f"  - {relative_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
