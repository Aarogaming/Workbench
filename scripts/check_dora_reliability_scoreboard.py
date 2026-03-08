#!/usr/bin/env python3
"""Validate weekly DORA + reliability scoreboard contract."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


SCOREBOARD_JSON = Path("docs/reports/dora_reliability_scoreboard.json")
SCOREBOARD_MD = Path("docs/reports/dora_reliability_scoreboard.md")

REQUIRED_TOP_LEVEL: tuple[str, ...] = (
    "schema_version",
    "measurement_mode",
    "generated_at",
    "window",
    "metrics",
    "overall_status",
    "notes",
)

REQUIRED_DORA_METRICS: tuple[str, ...] = (
    "deployment_frequency_per_week",
    "lead_time_for_changes_median_hours",
    "change_failure_rate_pct",
    "time_to_restore_service_median_hours",
)

REQUIRED_RELIABILITY_METRICS: tuple[str, ...] = (
    "quality_gate_pass_rate_pct",
    "hard_block_rate_pct",
    "cp4b_sla_breach_count",
    "incident_handoff_completeness_pct",
)

REQUIRED_MD_HEADINGS: tuple[str, ...] = (
    "# DORA + Reliability Weekly Scoreboard",
    "## DORA Metrics",
    "## Reliability Metrics",
    "## Sources",
)

ALLOWED_STATUSES = {"green", "amber", "red"}


def _parse_rfc3339_utc(value: str) -> dt.datetime | None:
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def _parse_iso_date(value: str) -> dt.date | None:
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _validate_metric(
    bucket: dict[str, object],
    metric_name: str,
    *,
    percent: bool = False,
    integer: bool = False,
) -> list[str]:
    issues: list[str] = []
    raw = bucket.get(metric_name)
    if not isinstance(raw, dict):
        return [f"metric '{metric_name}' must be an object"]

    value = raw.get("value")
    if integer:
        if not isinstance(value, int):
            issues.append(f"metric '{metric_name}.value' must be an integer")
        elif value < 0:
            issues.append(f"metric '{metric_name}.value' must be >= 0")
    else:
        if not isinstance(value, (int, float)):
            issues.append(f"metric '{metric_name}.value' must be numeric")
        elif value < 0:
            issues.append(f"metric '{metric_name}.value' must be >= 0")

    if percent and isinstance(value, (int, float)) and not (0 <= float(value) <= 100):
        issues.append(f"metric '{metric_name}.value' must be between 0 and 100")

    status = raw.get("status")
    if not isinstance(status, str) or status not in ALLOWED_STATUSES:
        issues.append(
            f"metric '{metric_name}.status' must be one of {sorted(ALLOWED_STATUSES)}"
        )

    source = raw.get("source")
    if not isinstance(source, str) or not source.strip():
        issues.append(f"metric '{metric_name}.source' must be a non-empty string")

    target_min = raw.get("target_min")
    target_max = raw.get("target_max")
    if target_min is None and target_max is None:
        issues.append(f"metric '{metric_name}' must define target_min or target_max")
    if target_min is not None and not isinstance(target_min, (int, float)):
        issues.append(f"metric '{metric_name}.target_min' must be numeric when present")
    if target_max is not None and not isinstance(target_max, (int, float)):
        issues.append(f"metric '{metric_name}.target_max' must be numeric when present")

    return issues


def check_scoreboard(root: Path) -> list[str]:
    issues: list[str] = []
    scoreboard_json_path = root / SCOREBOARD_JSON
    scoreboard_md_path = root / SCOREBOARD_MD

    if not scoreboard_json_path.exists():
        issues.append(f"missing scoreboard json: {SCOREBOARD_JSON.as_posix()}")
        return issues
    if not scoreboard_md_path.exists():
        issues.append(f"missing scoreboard markdown: {SCOREBOARD_MD.as_posix()}")
        return issues

    try:
        payload = json.loads(scoreboard_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid json in {SCOREBOARD_JSON.as_posix()}: {exc}"]

    if not isinstance(payload, dict):
        return [f"scoreboard payload must be an object: {SCOREBOARD_JSON.as_posix()}"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in payload:
            issues.append(f"missing top-level key '{key}' in {SCOREBOARD_JSON.as_posix()}")

    schema_version = payload.get("schema_version")
    if schema_version != "workbench.dora_reliability.v1":
        issues.append(
            "schema_version must be 'workbench.dora_reliability.v1' "
            f"(got: {schema_version!r})"
        )

    generated_at = payload.get("generated_at")
    if not isinstance(generated_at, str) or _parse_rfc3339_utc(generated_at) is None:
        issues.append("generated_at must be RFC3339 UTC format (YYYY-MM-DDTHH:MM:SSZ)")

    window = payload.get("window")
    if not isinstance(window, dict):
        issues.append("window must be an object")
    else:
        if window.get("cadence") != "weekly":
            issues.append("window.cadence must be 'weekly'")
        start = _parse_iso_date(str(window.get("start_date", "")))
        end = _parse_iso_date(str(window.get("end_date", "")))
        if start is None or end is None:
            issues.append("window.start_date and window.end_date must be YYYY-MM-DD")
        else:
            day_span = (end - start).days
            if day_span < 6 or day_span > 8:
                issues.append("window date span must represent one week (6-8 day difference)")

    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        issues.append("metrics must be an object")
    else:
        dora = metrics.get("dora")
        reliability = metrics.get("reliability")
        if not isinstance(dora, dict):
            issues.append("metrics.dora must be an object")
        else:
            for metric_name in REQUIRED_DORA_METRICS:
                issues.extend(
                    _validate_metric(
                        dora,
                        metric_name,
                        percent=metric_name.endswith("_pct"),
                    )
                )

        if not isinstance(reliability, dict):
            issues.append("metrics.reliability must be an object")
        else:
            for metric_name in REQUIRED_RELIABILITY_METRICS:
                issues.extend(
                    _validate_metric(
                        reliability,
                        metric_name,
                        percent=metric_name.endswith("_pct"),
                        integer=(metric_name == "cp4b_sla_breach_count"),
                    )
                )

    overall_status = payload.get("overall_status")
    if not isinstance(overall_status, str) or overall_status not in ALLOWED_STATUSES:
        issues.append(f"overall_status must be one of {sorted(ALLOWED_STATUSES)}")

    notes = payload.get("notes")
    if not isinstance(notes, list) or not notes:
        issues.append("notes must be a non-empty list")

    md_content = scoreboard_md_path.read_text(encoding="utf-8")
    for heading in REQUIRED_MD_HEADINGS:
        if heading not in md_content:
            issues.append(f"missing heading in {SCOREBOARD_MD.as_posix()}: {heading}")

    for metric_name in (*REQUIRED_DORA_METRICS, *REQUIRED_RELIABILITY_METRICS):
        if metric_name not in json.dumps(payload):
            issues.append(f"missing metric key in json payload: {metric_name}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate DORA + reliability weekly scoreboard files."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_scoreboard(root)
    if issues:
        print("[fail] dora reliability scoreboard check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] dora reliability scoreboard check")
    print(f"  - {SCOREBOARD_JSON.as_posix()}")
    print(f"  - {SCOREBOARD_MD.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
