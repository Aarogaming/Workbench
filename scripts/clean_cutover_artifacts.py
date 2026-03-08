#!/usr/bin/env python3
"""Clean old cutover artifacts based on retention class."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path


DEFAULT_RETENTION_DAYS = {
    "short": 3,
    "standard": 14,
    "forensic": 90,
}


def _parse_utc(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def _run_directories(root: Path) -> list[Path]:
    if not root.exists():
        return []
    runs: list[Path] = []
    for incident_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        for run_dir in sorted(path for path in incident_dir.iterdir() if path.is_dir()):
            runs.append(run_dir)
    return runs


def _age_days(now: dt.datetime, path: Path) -> float:
    modified = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)
    return (now - modified).total_seconds() / 86400.0


def _maybe_delete(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    shutil.rmtree(path, ignore_errors=False)


def _remove_empty_incident_dirs(root: Path, dry_run: bool) -> int:
    removed = 0
    for incident_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        if any(incident_dir.iterdir()):
            continue
        if dry_run:
            print(f"[dry-run-rmdir] {incident_dir}")
        else:
            incident_dir.rmdir()
            print(f"[rmdir] {incident_dir}")
        removed += 1
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clean cutover artifacts older than retention thresholds."
    )
    parser.add_argument(
        "--root",
        default="artifacts/cutover",
        help="Cutover artifact root (default: artifacts/cutover).",
    )
    parser.add_argument(
        "--retention-class",
        choices=["short", "standard", "forensic"],
        default="standard",
        help="Retention class (default: standard).",
    )
    parser.add_argument("--short-days", type=int, default=DEFAULT_RETENTION_DAYS["short"])
    parser.add_argument("--standard-days", type=int, default=DEFAULT_RETENTION_DAYS["standard"])
    parser.add_argument("--forensic-days", type=int, default=DEFAULT_RETENTION_DAYS["forensic"])
    parser.add_argument(
        "--now-utc",
        default=None,
        help="Override current UTC time (RFC3339 UTC, e.g. 2026-02-17T03:00:00Z).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview deletions only.")
    args = parser.parse_args()

    root = (Path(__file__).resolve().parents[1] / args.root).resolve()
    now = _parse_utc(args.now_utc) if args.now_utc else dt.datetime.now(dt.timezone.utc)
    retention_days = {
        "short": args.short_days,
        "standard": args.standard_days,
        "forensic": args.forensic_days,
    }[args.retention_class]

    if retention_days < 0:
        print("Error: retention days must be >= 0")
        return 2

    if not root.exists():
        print(f"[ok] root does not exist: {root}")
        return 0

    cutoff_age = float(retention_days)
    run_dirs = _run_directories(root)
    deleted = 0
    kept = 0
    for run_dir in run_dirs:
        age_days = _age_days(now, run_dir)
        if age_days >= cutoff_age:
            if args.dry_run:
                print(f"[dry-run-delete] {run_dir} age_days={age_days:.2f}")
            else:
                _maybe_delete(run_dir, dry_run=False)
                print(f"[delete] {run_dir} age_days={age_days:.2f}")
            deleted += 1
        else:
            print(f"[keep] {run_dir} age_days={age_days:.2f}")
            kept += 1

    removed_incident_dirs = _remove_empty_incident_dirs(root, dry_run=args.dry_run)
    print(
        "[summary] "
        f"class={args.retention_class} days={retention_days} deleted={deleted} "
        f"kept={kept} removed_incident_dirs={removed_incident_dirs}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
