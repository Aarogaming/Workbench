#!/usr/bin/env python3
"""Select a CP2 failure taxonomy from workflow/job context."""

from __future__ import annotations

import argparse
import os


def select_failure_taxonomy(workflow: str, job: str, default: str = "script") -> str:
    text = f"{workflow} {job}".lower()
    if any(token in text for token in ("attestation", "provenance", "supply-chain", "supply chain")):
        return "supply_chain"
    if any(token in text for token in ("policy", "scorecard", "pinning", "ruleset")):
        return "policy"
    if any(token in text for token in ("artifact", "download", "upload")):
        return "artifact"
    if any(token in text for token in ("approval", "reviewer", "manual gate", "human")):
        return "human_gate"
    if any(token in text for token in ("infra", "runner", "network", "timeout")):
        return "infra"
    return default


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Auto-select failure taxonomy from workflow/job names."
    )
    parser.add_argument(
        "--workflow",
        default=os.getenv("GITHUB_WORKFLOW", ""),
        help="Workflow name (default: $GITHUB_WORKFLOW).",
    )
    parser.add_argument(
        "--job",
        default=os.getenv("GITHUB_JOB", ""),
        help="Job id/name (default: $GITHUB_JOB).",
    )
    parser.add_argument(
        "--default",
        choices=["infra", "script", "policy", "artifact", "human_gate", "supply_chain"],
        default="script",
        help="Fallback taxonomy.",
    )
    args = parser.parse_args()

    print(select_failure_taxonomy(args.workflow, args.job, default=args.default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
