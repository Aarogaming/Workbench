#!/usr/bin/env python3
"""Run a deterministic Workbench campaign execution loop."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_shell(command: str, cwd: Path) -> dict[str, Any]:
    started = time.time()
    completed = subprocess.run(command, shell=True, cwd=str(cwd), check=False)
    return {
        "command": command,
        "returnCode": int(completed.returncode),
        "ok": completed.returncode == 0,
        "durationMs": int((time.time() - started) * 1000),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _record_outcome(
    *,
    python_exe: str,
    repo_root: Path,
    record_script: Path,
    campaign_id: str,
    owner_lane: str,
    terminal_outcome: str,
    summary: str,
    trace_path: Path,
    json_out: Path,
    md_out: Path,
    required_unblock_inputs: list[str],
) -> int:
    command = [
        python_exe,
        str(record_script),
        "--campaign-id",
        campaign_id,
        "--owner-lane",
        owner_lane,
        "--terminal-outcome",
        terminal_outcome,
        "--summary",
        summary,
        "--trace-path",
        str(trace_path),
        "--json-out",
        str(json_out),
        "--md-out",
        str(md_out),
    ]
    for item in required_unblock_inputs:
        command.extend(["--required-unblock-input", item])
    completed = subprocess.run(command, cwd=str(repo_root), check=False)
    return int(completed.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run campaign commands with retry and deterministic outcomes."
    )
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--owner-lane", default="A0")
    parser.add_argument(
        "--preflight-cmd",
        default="bash scripts/run_preflight_campaign.sh --skip-tests --skip-evals",
    )
    parser.add_argument("--execute-cmd", required=True)
    parser.add_argument("--validate-cmd", default="")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument(
        "--trace-out",
        default="docs/reports/campaigns/CAMPAIGN_TRACE_LATEST.json",
    )
    parser.add_argument(
        "--outcome-json-out",
        default="docs/reports/campaigns/CAMPAIGN_OUTCOME_LATEST.json",
    )
    parser.add_argument(
        "--outcome-md-out",
        default="docs/reports/campaigns/CAMPAIGN_SUMMARY_LATEST.md",
    )
    parser.add_argument(
        "--record-script",
        default="scripts/record_campaign_outcome.py",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    trace_out = (repo_root / args.trace_out).resolve()
    outcome_json_out = (repo_root / args.outcome_json_out).resolve()
    outcome_md_out = (repo_root / args.outcome_md_out).resolve()
    record_script = (repo_root / args.record_script).resolve()

    trace: dict[str, Any] = {
        "schemaName": "WorkbenchCampaignTrace",
        "schemaVersion": "1.0.0",
        "generatedUtc": _utc_now_iso(),
        "campaign": {
            "id": args.campaign_id,
            "owner_lane": args.owner_lane,
        },
        "preflight": None,
        "attempts": [],
    }

    preflight = _run_shell(args.preflight_cmd, repo_root)
    trace["preflight"] = preflight
    if not bool(preflight["ok"]):
        trace["terminalOutcome"] = "hard_block"
        trace["terminalSummary"] = "preflight command failed"
        _write_json(trace_out, trace)
        rc = _record_outcome(
            python_exe=sys.executable,
            repo_root=repo_root,
            record_script=record_script,
            campaign_id=args.campaign_id,
            owner_lane=args.owner_lane,
            terminal_outcome="hard_block",
            summary="preflight command failed",
            trace_path=trace_out,
            json_out=outcome_json_out,
            md_out=outcome_md_out,
            required_unblock_inputs=["fix preflight failures and rerun"],
        )
        return 2 if rc == 0 else rc

    max_attempts = max(1, int(args.max_retries) + 1)
    for attempt in range(1, max_attempts + 1):
        execute_result = _run_shell(args.execute_cmd, repo_root)
        validate_result: dict[str, Any] | None = None
        if args.validate_cmd:
            validate_result = _run_shell(args.validate_cmd, repo_root)

        entry: dict[str, Any] = {
            "attempt": attempt,
            "execute": execute_result,
            "validate": validate_result,
        }
        trace["attempts"].append(entry)

        execute_ok = bool(execute_result["ok"])
        validate_ok = True if validate_result is None else bool(validate_result["ok"])
        if execute_ok and validate_ok:
            trace["terminalOutcome"] = "complete"
            trace["terminalSummary"] = "campaign execution and validation passed"
            _write_json(trace_out, trace)
            rc = _record_outcome(
                python_exe=sys.executable,
                repo_root=repo_root,
                record_script=record_script,
                campaign_id=args.campaign_id,
                owner_lane=args.owner_lane,
                terminal_outcome="complete",
                summary="campaign execution and validation passed",
                trace_path=trace_out,
                json_out=outcome_json_out,
                md_out=outcome_md_out,
                required_unblock_inputs=[],
            )
            return 0 if rc == 0 else rc

        if attempt < max_attempts:
            time.sleep(max(0.0, float(args.sleep_seconds)))

    trace["terminalOutcome"] = "hard_block"
    trace["terminalSummary"] = "campaign exhausted retries"
    _write_json(trace_out, trace)
    rc = _record_outcome(
        python_exe=sys.executable,
        repo_root=repo_root,
        record_script=record_script,
        campaign_id=args.campaign_id,
        owner_lane=args.owner_lane,
        terminal_outcome="hard_block",
        summary="campaign exhausted retries",
        trace_path=trace_out,
        json_out=outcome_json_out,
        md_out=outcome_md_out,
        required_unblock_inputs=["inspect trace artifact and failing command output"],
    )
    return 2 if rc == 0 else rc


if __name__ == "__main__":
    raise SystemExit(main())
