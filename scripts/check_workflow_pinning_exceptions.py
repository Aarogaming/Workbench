#!/usr/bin/env python3
"""Review workflow pinning exception policy for staleness and expiry."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


USES_RE = re.compile(r"^\s*(?:-\s*)?uses\s*:\s*(.+?)\s*(?:#.*)?$")


def _normalize_uses(value: str) -> str:
    return value.strip().strip("'").strip('"')


def _parse_iso_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except Exception:
        return None


def _parse_iso_datetime(value: str) -> dt.datetime | None:
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _workflow_contains_uses(path: Path, uses_value: str) -> bool:
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        match = USES_RE.match(line)
        if not match:
            continue
        if _normalize_uses(match.group(1)) == uses_value:
            return True
    return False


def _load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("exceptions file must contain a JSON object")
    return payload


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review workflow pinning exceptions for validity and freshness."
    )
    parser.add_argument(
        "--exceptions-file",
        default=".github/workflow-pinning-exceptions.json",
        help="Exception policy JSON relative to repo root.",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/workflow_pinning_exceptions_review.json",
        help="Review report output path relative to repo root.",
    )
    parser.add_argument(
        "--warn-days",
        type=int,
        default=30,
        help="Mark review dates inside this horizon as due soon.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Fail if any due-soon exception exists.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    exceptions_path = (root / args.exceptions_file).resolve()
    out_path = (root / args.json_out).resolve()
    today = dt.date.today()
    warn_horizon = today + dt.timedelta(days=max(args.warn_days, 0))

    invalid: list[str] = []
    stale: list[str] = []
    expired: list[str] = []
    due_soon: list[str] = []
    active: list[str] = []
    reviewed: list[dict[str, Any]] = []

    if not exceptions_path.exists():
        invalid.append(f"exceptions file missing: {_display_path(exceptions_path, root)}")
        payload = {"exceptions": []}
    else:
        try:
            payload = _load_payload(exceptions_path)
        except Exception as exc:
            invalid.append(f"invalid exceptions file JSON: {exc}")
            payload = {"exceptions": []}

    rows = payload.get("exceptions", [])
    if not isinstance(rows, list):
        invalid.append("`exceptions` field must be a list")
        rows = []

    seen_ids: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            invalid.append(f"row {idx}: expected object, got {type(row).__name__}")
            continue
        if row.get("enabled", True) is False:
            continue

        exception_id = str(row.get("id", "")).strip()
        workflow = str(row.get("workflow", "")).strip()
        uses = _normalize_uses(str(row.get("uses", "")))
        reason = str(row.get("reason", "")).strip()
        approved_by = str(row.get("approved_by", "")).strip()
        approved_utc = str(row.get("approved_utc", "")).strip()
        review_by = str(row.get("review_by", "")).strip()
        review_date = _parse_iso_date(review_by)
        approved_at = _parse_iso_datetime(approved_utc)

        if not exception_id:
            invalid.append(f"row {idx}: missing id")
            continue
        if exception_id in seen_ids:
            invalid.append(f"row {idx}: duplicate id `{exception_id}`")
            continue
        seen_ids.add(exception_id)

        if not workflow or not uses or not reason or not approved_by:
            invalid.append(
                f"row {idx} (`{exception_id}`): requires workflow/uses/reason/approved_by"
            )
            continue
        if approved_at is None:
            invalid.append(
                f"row {idx} (`{exception_id}`): approved_utc must be ISO datetime"
            )
            continue
        if review_date is None:
            invalid.append(
                f"row {idx} (`{exception_id}`): review_by must be ISO date (YYYY-MM-DD)"
            )
            continue

        workflow_path = (root / workflow).resolve()
        if not _workflow_contains_uses(workflow_path, uses):
            stale.append(
                f"id `{exception_id}` points to missing workflow reference `{workflow}` `{uses}`"
            )
            status = "stale"
        elif review_date < today:
            expired.append(
                f"id `{exception_id}` review date {review_by} is in the past"
            )
            status = "expired"
        elif review_date <= warn_horizon:
            due_soon.append(
                f"id `{exception_id}` review date {review_by} is within {args.warn_days} days"
            )
            status = "due_soon"
        else:
            active.append(
                f"id `{exception_id}` review date {review_by} remains active"
            )
            status = "active"

        reviewed.append(
            {
                "id": exception_id,
                "workflow": workflow,
                "uses": uses,
                "review_by": review_by,
                "status": status,
            }
        )

    report: dict[str, Any] = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "exceptions_file": _display_path(exceptions_path, root),
        "warn_days": int(args.warn_days),
        "summary": {
            "reviewed_count": len(reviewed),
            "invalid_count": len(invalid),
            "stale_count": len(stale),
            "expired_count": len(expired),
            "due_soon_count": len(due_soon),
            "active_count": len(active),
        },
        "invalid": invalid,
        "stale": stale,
        "expired": expired,
        "due_soon": due_soon,
        "active": active,
        "reviewed": reviewed,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Exceptions file: {_display_path(exceptions_path, root)}")
    print(f"Reviewed: {len(reviewed)}")
    print(f"Invalid: {len(invalid)}")
    print(f"Stale: {len(stale)}")
    print(f"Expired: {len(expired)}")
    print(f"Due soon: {len(due_soon)}")
    print(f"Active: {len(active)}")
    print(f"JSON report: {out_path}")

    for row in invalid:
        print(f"- invalid: {row}")
    for row in stale:
        print(f"- stale: {row}")
    for row in expired:
        print(f"- expired: {row}")
    for row in due_soon:
        print(f"- due_soon: {row}")

    fail = bool(invalid or stale or expired)
    if args.fail_on_warning and due_soon:
        fail = True
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
