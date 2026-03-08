#!/usr/bin/env python3
"""Fail when CP4-B tracker items exceed SLA without implemented status."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


ALLOWED_STATUSES = {"planned", "in_progress", "blocked", "implemented"}


def _parse_utc(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def _parse_cell(value: str) -> str:
    cleaned = value.strip()
    if cleaned.startswith("`") and cleaned.endswith("`") and len(cleaned) >= 2:
        return cleaned[1:-1]
    return cleaned


def parse_tracker_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `CP4B-"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 6:
            continue
        rows.append(
            {
                "action_id": _parse_cell(cells[0]),
                "action": _parse_cell(cells[1]),
                "owner": _parse_cell(cells[2]),
                "sla_utc": _parse_cell(cells[3]),
                "status": _parse_cell(cells[4]).lower(),
                "closure_evidence": _parse_cell(cells[5]),
            }
        )
    return rows


def evaluate_rows(rows: list[dict[str, str]], now_utc: dt.datetime) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    overdue_items: list[str] = []
    for row in rows:
        status = row["status"]
        if status not in ALLOWED_STATUSES:
            issues.append(
                f"{row['action_id']}: invalid status '{status}' (allowed: {sorted(ALLOWED_STATUSES)})"
            )
            continue

        if status == "implemented" and not row["closure_evidence"].strip():
            issues.append(f"{row['action_id']}: implemented status requires closure evidence")

        try:
            due = _parse_utc(row["sla_utc"])
        except ValueError:
            issues.append(f"{row['action_id']}: invalid SLA timestamp '{row['sla_utc']}'")
            continue

        if status != "implemented" and now_utc > due:
            overdue_items.append(
                f"{row['action_id']} owner={row['owner']} status={status} due={row['sla_utc']}"
            )
    return issues, overdue_items


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check CP4-B SLA status in tracker packet."
    )
    parser.add_argument(
        "--path",
        default="docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md",
        help="Tracker markdown path.",
    )
    parser.add_argument(
        "--now-utc",
        default=None,
        help="Override current UTC time (RFC3339 UTC).",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    path = (root / args.path).resolve()
    if not path.exists():
        print(f"[fail] missing tracker file: {path}")
        return 1

    now = _parse_utc(args.now_utc) if args.now_utc else dt.datetime.now(dt.timezone.utc)
    rows = parse_tracker_rows(path.read_text(encoding="utf-8"))
    if not rows:
        print(f"[fail] no CP4-B tracker rows found in {path}")
        return 1

    issues, overdue = evaluate_rows(rows, now)
    if issues:
        print(f"[fail] tracker parse issues in {path}")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    if overdue:
        print(f"[fail] overdue CP4-B items: {len(overdue)}")
        for item in overdue:
            print(f"  - {item}")
        return 1

    print(f"[ok] CP4-B SLA check rows={len(rows)} now={now.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
