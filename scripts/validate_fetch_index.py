#!/usr/bin/env python3
"""Validate CP2 fetch index artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_VERSION = "cp2.fetch_index.v1"
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RFC3339_UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ALLOWED_STATUSES = {"ok", "missing", "dry-run"}


def validate_payload(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required_fields = (
        "schema_version",
        "generated_at_utc",
        "repo",
        "run_id",
        "incident_id",
        "run_attempt",
        "dry_run",
        "artifacts",
    )
    for field in required_fields:
        if field not in payload:
            issues.append(f"missing required field: {field}")

    if issues:
        return issues

    if payload["schema_version"] != EXPECTED_SCHEMA_VERSION:
        issues.append(
            f"schema_version must be '{EXPECTED_SCHEMA_VERSION}' (got '{payload['schema_version']}')"
        )
    if not RFC3339_UTC_PATTERN.match(str(payload["generated_at_utc"])):
        issues.append("generated_at_utc must be RFC3339 UTC (YYYY-MM-DDTHH:MM:SSZ)")
    if not REPO_PATTERN.match(str(payload["repo"])):
        issues.append(f"repo must match owner/repo pattern (got '{payload['repo']}')")
    if not isinstance(payload["run_id"], str) or not payload["run_id"].strip():
        issues.append("run_id must be a non-empty string")

    incident_id = payload["incident_id"]
    if incident_id is not None and (not isinstance(incident_id, str) or not incident_id.strip()):
        issues.append("incident_id must be null or a non-empty string")

    run_attempt = payload["run_attempt"]
    if run_attempt is not None and (
        not isinstance(run_attempt, int) or run_attempt < 1
    ):
        issues.append("run_attempt must be null or an integer >= 1")

    if not isinstance(payload["dry_run"], bool):
        issues.append("dry_run must be a boolean")

    artifacts = payload["artifacts"]
    if not isinstance(artifacts, list):
        issues.append("artifacts must be a list")
    else:
        for idx, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                issues.append(f"artifacts[{idx}] must be an object")
                continue
            for field in ("class", "artifact_name", "status", "dir"):
                if field not in artifact:
                    issues.append(f"artifacts[{idx}] missing required field: {field}")
                    continue
                value = artifact[field]
                if not isinstance(value, str) or not value.strip():
                    issues.append(f"artifacts[{idx}].{field} must be a non-empty string")
            status = artifact.get("status")
            if isinstance(status, str) and status not in ALLOWED_STATUSES:
                issues.append(
                    f"artifacts[{idx}].status must be one of {sorted(ALLOWED_STATUSES)} (got '{status}')"
                )

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

    return validate_payload(payload)


def _discover_paths(root: Path, discover_root: str) -> list[Path]:
    scan_root = (root / discover_root).resolve()
    if not scan_root.exists():
        return []
    return sorted(path for path in scan_root.rglob("index.json") if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate CP2 fetch index artifact(s)."
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Path to index.json. May be provided multiple times.",
    )
    parser.add_argument(
        "--discover-root",
        default="artifacts/cutover",
        help="Directory to recursively discover index.json when --path is omitted.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    paths = [Path(raw) for raw in args.path]
    if not paths:
        paths = _discover_paths(root, args.discover_root)
        if not paths:
            print("[ok] no fetch index artifacts discovered")
            return 0

    any_failures = False
    for path in paths:
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
