#!/usr/bin/env python3
"""Validate CP2 run-summary JSON artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_VERSION = "cp2.run_summary.v1"
TERMINAL_CLASSES = {"complete", "soft_block", "hard_block"}
FAILURE_TAXONOMY = {
    "infra",
    "script",
    "policy",
    "artifact",
    "human_gate",
    "supply_chain",
}
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RFC3339_UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

REQUIRED_FIELDS = (
    "schema_version",
    "cycle_id",
    "phase",
    "incident_id",
    "terminal_class",
    "failure_taxonomy",
    "repo",
    "workflow",
    "run_id",
    "run_attempt",
    "head_sha",
    "failing_job",
    "failing_step",
    "rerun_debug_cmd",
    "artifact_fetch_cmd",
    "next_owner",
    "requires_handoff_by_utc",
    "generated_at_utc",
    "missing_artifacts",
)


def validate_summary(summary: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in summary:
            issues.append(f"missing required field: {field}")

    if issues:
        return issues

    if summary["schema_version"] != EXPECTED_SCHEMA_VERSION:
        issues.append(
            f"schema_version must be '{EXPECTED_SCHEMA_VERSION}' (got '{summary['schema_version']}')"
        )

    terminal_class = str(summary["terminal_class"])
    if terminal_class not in TERMINAL_CLASSES:
        issues.append(
            f"terminal_class must be one of {sorted(TERMINAL_CLASSES)} (got '{terminal_class}')"
        )

    failure_taxonomy = str(summary["failure_taxonomy"])
    if failure_taxonomy not in FAILURE_TAXONOMY:
        issues.append(
            f"failure_taxonomy must be one of {sorted(FAILURE_TAXONOMY)} (got '{failure_taxonomy}')"
        )

    repo = str(summary["repo"])
    if not REPO_PATTERN.match(repo):
        issues.append(f"repo must match owner/repo pattern (got '{repo}')")

    run_attempt = summary["run_attempt"]
    if not isinstance(run_attempt, int) or run_attempt < 1:
        issues.append("run_attempt must be an integer >= 1")

    for field in (
        "cycle_id",
        "phase",
        "incident_id",
        "workflow",
        "run_id",
        "head_sha",
        "rerun_debug_cmd",
        "artifact_fetch_cmd",
        "next_owner",
    ):
        value = summary[field]
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{field} must be a non-empty string")

    for field in ("requires_handoff_by_utc", "generated_at_utc"):
        value = str(summary[field])
        if not RFC3339_UTC_PATTERN.match(value):
            issues.append(f"{field} must be RFC3339 UTC (YYYY-MM-DDTHH:MM:SSZ)")

    if terminal_class != "complete":
        for field in ("failing_job", "failing_step"):
            value = summary[field]
            if not isinstance(value, str) or not value.strip():
                issues.append(f"{field} must be a non-empty string for non-complete terminal_class")

    missing_artifacts = summary["missing_artifacts"]
    if not isinstance(missing_artifacts, list):
        issues.append("missing_artifacts must be a list")
    else:
        for idx, entry in enumerate(missing_artifacts):
            if not isinstance(entry, str):
                issues.append(f"missing_artifacts[{idx}] must be a string")

    return issues


def validate_path(path: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"file not found: {path}"]
    except json.JSONDecodeError as exc:
        return [f"invalid JSON ({path}): {exc}"]

    if not isinstance(payload, dict):
        return [f"root JSON value must be an object ({path})"]

    return validate_summary(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CP2 run-summary JSON artifact(s).")
    parser.add_argument(
        "--path",
        action="append",
        required=True,
        help="Path to run_summary.json. May be specified multiple times.",
    )
    args = parser.parse_args()

    any_failures = False
    for raw_path in args.path:
        path = Path(raw_path)
        issues = validate_path(path)
        if issues:
            any_failures = True
            print(f"[fail] {path}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[ok] {path}")

    return 1 if any_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
