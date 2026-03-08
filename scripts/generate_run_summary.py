#!/usr/bin/env python3
"""Generate CP2-compatible run summary artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path

from validate_run_summary import validate_summary


TERMINAL_CLASS_BY_JOB_STATUS = {
    "success": "complete",
    "failure": "hard_block",
    "cancelled": "soft_block",
}


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _format_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_summary(args: argparse.Namespace) -> dict[str, object]:
    generated_at = _utc_now()
    generated_at_utc = _format_utc(generated_at)
    handoff_due_utc = (
        args.requires_handoff_by_utc
        if args.requires_handoff_by_utc
        else _format_utc(generated_at + dt.timedelta(hours=args.handoff_window_hours))
    )

    repo = args.repo or "owner/repo"
    run_id = args.run_id or "0"
    run_attempt = int(args.run_attempt)
    incident_id = args.incident_id or f"CUTOVER-{generated_at.strftime('%Y-%m-%d')}-{run_id}"

    terminal_class = args.terminal_class
    if not terminal_class:
        terminal_class = TERMINAL_CLASS_BY_JOB_STATUS.get(args.job_status.lower(), "soft_block")

    rerun_debug_cmd = args.rerun_debug_cmd or (
        f"gh run rerun {run_id} --repo {repo} --failed --debug"
    )
    artifact_fetch_cmd = args.artifact_fetch_cmd or (
        "bash scripts/fetch_workbench_artifacts.sh "
        f"--run-id {run_id} --repo {repo} "
        f"--incident-id {incident_id} --run-attempt {run_attempt} "
        "--class eval --class attestations --class policy"
    )

    failing_job = args.failing_job
    failing_step = args.failing_step
    if terminal_class == "complete":
        failing_job = failing_job or "n/a"
        failing_step = failing_step or "n/a"
    else:
        failing_job = failing_job or args.workflow or "unknown-job"
        failing_step = failing_step or "see job logs"

    return {
        "schema_version": "cp2.run_summary.v1",
        "cycle_id": args.cycle_id,
        "phase": args.phase,
        "incident_id": incident_id,
        "terminal_class": terminal_class,
        "failure_taxonomy": args.failure_taxonomy,
        "repo": repo,
        "workflow": args.workflow,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "head_sha": args.head_sha,
        "failing_job": failing_job,
        "failing_step": failing_step,
        "rerun_debug_cmd": rerun_debug_cmd,
        "artifact_fetch_cmd": artifact_fetch_cmd,
        "next_owner": args.next_owner,
        "requires_handoff_by_utc": handoff_due_utc,
        "generated_at_utc": generated_at_utc,
        "missing_artifacts": list(args.missing_artifact or []),
    }


def _build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Run Summary",
        "",
        "## Incident Header",
        f"- Incident ID: `{summary['incident_id']}`",
        f"- Repo: `{summary['repo']}`",
        f"- Workflow: `{summary['workflow']}`",
        f"- Run: `{summary['run_id']}` attempt `{summary['run_attempt']}`",
        f"- Head SHA: `{summary['head_sha']}`",
        f"- Generated (UTC): `{summary['generated_at_utc']}`",
        "",
        "## Outcome",
        f"- Terminal class: `{summary['terminal_class']}`",
        f"- Failure taxonomy: `{summary['failure_taxonomy']}`",
        "",
        "## Failure Snapshot",
        f"- Failing job: `{summary['failing_job']}`",
        f"- Failing step: `{summary['failing_step']}`",
        "- Top error lines: see workflow logs for the failing job/step.",
        "",
        "## Artifact Fetch",
        f"- Command: `{summary['artifact_fetch_cmd']}`",
        "",
        "## Next Actions",
        f"- Next owner: `{summary['next_owner']}`",
        f"- Handoff by (UTC): `{summary['requires_handoff_by_utc']}`",
        f"- Rerun (debug): `{summary['rerun_debug_cmd']}`",
    ]
    return "\n".join(lines) + "\n"


def _append_step_summary(markdown: str) -> Path | None:
    step_summary_path = os.getenv("GITHUB_STEP_SUMMARY", "").strip()
    if not step_summary_path:
        return None

    path = Path(step_summary_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("## Run Summary Contract (cp2.run_summary.v1)\n\n")
        handle.write(markdown)
        if not markdown.endswith("\n"):
            handle.write("\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate CP2 run_summary.md/json artifacts.")
    parser.add_argument(
        "--output-dir",
        default="docs/reports/run_summary",
        help="Output directory for run_summary.md/json (default: docs/reports/run_summary).",
    )
    parser.add_argument(
        "--cycle-id",
        default="CHIMERA-V2-RESEARCH-AND-EXECUTION-2026-02-15",
        help="Cycle identifier.",
    )
    parser.add_argument("--phase", default="CP4-A", help="Execution phase label.")
    parser.add_argument("--incident-id", default=None, help="Incident id; auto-generated if omitted.")
    parser.add_argument(
        "--terminal-class",
        default=None,
        choices=["complete", "soft_block", "hard_block"],
        help="Terminal class override. Defaults from --job-status.",
    )
    parser.add_argument(
        "--failure-taxonomy",
        default="script",
        choices=["infra", "script", "policy", "artifact", "human_gate", "supply_chain"],
        help="Failure taxonomy classification.",
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY", ""),
        help="Repository slug owner/name.",
    )
    parser.add_argument(
        "--workflow",
        default=os.getenv("GITHUB_WORKFLOW", "unknown-workflow"),
        help="Workflow name.",
    )
    parser.add_argument(
        "--run-id",
        default=os.getenv("GITHUB_RUN_ID", ""),
        help="Workflow run id.",
    )
    parser.add_argument(
        "--run-attempt",
        type=int,
        default=int(os.getenv("GITHUB_RUN_ATTEMPT", "1")),
        help="Workflow run attempt.",
    )
    parser.add_argument(
        "--head-sha",
        default=os.getenv("GITHUB_SHA", "unknown-sha"),
        help="Git commit SHA.",
    )
    parser.add_argument(
        "--job-status",
        default="failure",
        help="Job status used for terminal-class mapping (success/failure/cancelled).",
    )
    parser.add_argument("--failing-job", default="", help="Failing job name.")
    parser.add_argument("--failing-step", default="", help="Failing step name.")
    parser.add_argument("--next-owner", default="lane-workbench", help="Next handoff owner.")
    parser.add_argument(
        "--requires-handoff-by-utc",
        default=None,
        help="Explicit handoff due timestamp (RFC3339 UTC).",
    )
    parser.add_argument(
        "--handoff-window-hours",
        type=int,
        default=2,
        help="Handoff due time offset from now when --requires-handoff-by-utc is omitted.",
    )
    parser.add_argument(
        "--missing-artifact",
        action="append",
        default=[],
        help="Missing artifact class/item. May be provided multiple times.",
    )
    parser.add_argument(
        "--artifact-fetch-cmd",
        default=None,
        help="Artifact fetch command override.",
    )
    parser.add_argument(
        "--rerun-debug-cmd",
        default=None,
        help="Rerun debug command override.",
    )
    args = parser.parse_args()

    summary = _build_summary(args)
    issues = validate_summary(summary)
    if issues:
        print("[fail] generated summary did not validate")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    root = Path(__file__).resolve().parents[1]
    out_dir = (root / args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "run_summary.json"
    md_path = out_dir / "run_summary.md"

    markdown = _build_markdown(summary)
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    step_summary_path = _append_step_summary(markdown)

    print(f"[ok] {json_path}")
    print(f"[ok] {md_path}")
    if step_summary_path:
        print(f"[ok] {step_summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
