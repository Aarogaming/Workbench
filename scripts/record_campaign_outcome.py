#!/usr/bin/env python3
"""Record deterministic Workbench campaign terminal outcome artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


TERMINAL_OUTCOMES = ("complete", "hard_block", "cancelled")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _render_summary(payload: dict) -> str:
    lines = [
        "# Campaign Outcome",
        "",
        f"- campaign_id: `{payload['campaign']['id']}`",
        f"- owner_lane: `{payload['campaign']['owner_lane']}`",
        f"- terminal_outcome: `{payload['terminal_outcome']}`",
        f"- generated_utc: `{payload['generated_utc']}`",
        "",
        "## Summary",
        payload["summary"],
        "",
    ]

    unblock_inputs = payload.get("hard_block", {}).get("required_unblock_inputs", [])
    if unblock_inputs:
        lines.append("## Required Unblock Inputs")
        for item in unblock_inputs:
            lines.append(f"- {item}")
        lines.append("")

    changed_paths = payload.get("changed_paths", [])
    if changed_paths:
        lines.append("## Changed Paths")
        for path in changed_paths:
            lines.append(f"- `{path}`")
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record campaign terminal outcome with deterministic schema."
    )
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--owner-lane", required=True)
    parser.add_argument("--terminal-outcome", choices=TERMINAL_OUTCOMES, required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--trace-path", default="")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--required-unblock-input", action="append", default=[])
    parser.add_argument(
        "--json-out",
        default="docs/reports/campaigns/CAMPAIGN_OUTCOME_LATEST.json",
    )
    parser.add_argument(
        "--md-out",
        default="docs/reports/campaigns/CAMPAIGN_SUMMARY_LATEST.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.terminal_outcome == "hard_block" and not args.required_unblock_input:
        raise SystemExit(
            "hard_block outcome requires at least one --required-unblock-input"
        )

    payload = {
        "schemaName": "WorkbenchCampaignOutcome",
        "schemaVersion": "1.0.0",
        "generated_utc": _utc_now_iso(),
        "campaign": {
            "id": args.campaign_id,
            "owner_lane": args.owner_lane,
            "trace_path": args.trace_path,
        },
        "terminal_outcome": args.terminal_outcome,
        "summary": args.summary,
        "changed_paths": list(args.changed_path),
        "hard_block": {
            "required_unblock_inputs": list(args.required_unblock_input),
        },
    }

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(_render_summary(payload), encoding="utf-8")

    print(str(json_out))
    print(str(md_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
