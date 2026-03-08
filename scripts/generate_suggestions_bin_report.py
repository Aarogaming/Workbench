#!/usr/bin/env python3
"""Generate synchronized suggestions-bin status report from markdown source."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


SUGGESTIONS_BIN_DOC = Path("docs/SUGGESTIONS_BIN.md")
DEFAULT_OUTPUT = Path("docs/reports/suggestions_bin.json")

SUGGESTION_RE = re.compile(r"^- `WB-SUG-(\d+)`\s*(.+)$")
STATUS_RE = re.compile(r"^- status:\s*`?([a-z_]+)`?")
ALLOWED_STATUSES = ("new", "reviewing", "approved", "scheduled", "implemented", "rejected")
SCHEMA_VERSION = "cp4b.suggestions_bin_report.v1"


def _status_counts(items: list[dict[str, str]]) -> dict[str, int]:
    counts = {status: 0 for status in ALLOWED_STATUSES}
    for item in items:
        counts[item["status"]] += 1
    return counts


def collect_suggestions(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], [f"missing suggestions doc: {path.as_posix()}"]

    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[dict[str, str]] = []
    issues: list[str] = []
    seen_ids: set[str] = set()

    for idx, line in enumerate(lines):
        match = SUGGESTION_RE.match(line.strip())
        if not match:
            continue

        suggestion_id = f"WB-SUG-{int(match.group(1)):03d}"
        title = match.group(2).strip()
        if suggestion_id in seen_ids:
            issues.append(f"duplicate suggestion id: {suggestion_id}")
            continue
        seen_ids.add(suggestion_id)

        status_value: str | None = None
        cursor = idx + 1
        while cursor < len(lines):
            stripped = lines[cursor].strip()
            if stripped.startswith("## ") or SUGGESTION_RE.match(stripped):
                break
            status_match = STATUS_RE.match(stripped)
            if status_match:
                status_value = status_match.group(1).lower()
                break
            cursor += 1

        if status_value is None:
            issues.append(f"{suggestion_id}: missing status line")
            continue
        if status_value not in ALLOWED_STATUSES:
            issues.append(
                f"{suggestion_id}: invalid status '{status_value}' (allowed: {list(ALLOWED_STATUSES)})"
            )
            continue

        items.append(
            {
                "id": suggestion_id,
                "title": title,
                "status": status_value,
            }
        )

    if not items and not issues:
        issues.append(f"no suggestion entries found in {path.as_posix()}")
    return sorted(items, key=lambda item: item["id"]), issues


def generate_report(root: Path, source_doc: Path = SUGGESTIONS_BIN_DOC) -> tuple[dict[str, Any] | None, list[str]]:
    suggestions_path = (root / source_doc).resolve()
    items, issues = collect_suggestions(suggestions_path)
    if issues:
        return None, issues

    counts = _status_counts(items)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_doc": source_doc.as_posix(),
        "status_values": list(ALLOWED_STATUSES),
        "summary": {
            "total": len(items),
            "implemented": counts["implemented"],
            "status_counts": counts,
        },
        "items": items,
    }
    return report, []


def _normalized_report(report: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(report)
    normalized.pop("generated_utc", None)
    return normalized


def check_report_sync(
    root: Path,
    output_path: Path = DEFAULT_OUTPUT,
    source_doc: Path = SUGGESTIONS_BIN_DOC,
) -> tuple[dict[str, Any] | None, list[str]]:
    expected_report, issues = generate_report(root, source_doc=source_doc)
    if issues:
        return None, issues

    assert expected_report is not None
    target = (root / output_path).resolve()
    if not target.exists():
        return expected_report, [f"missing report file: {output_path.as_posix()}"]

    try:
        existing_report = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return expected_report, [f"invalid json report: {output_path.as_posix()}"]
    if not isinstance(existing_report, dict):
        return expected_report, [f"invalid report object: {output_path.as_posix()}"]

    if _normalized_report(existing_report) != _normalized_report(expected_report):
        return expected_report, [
            f"report out of sync with source doc: {output_path.as_posix()}",
            "run `python3 scripts/generate_suggestions_bin_report.py` to regenerate",
        ]
    return expected_report, []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate synchronized suggestions-bin status report."
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT.as_posix(),
        help="Output JSON path relative to repo root.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that the existing report is synchronized with markdown source.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_path = Path(args.output)
    if args.check:
        report, issues = check_report_sync(root, output_path=output_path)
        if issues:
            print("[fail] suggestions bin report sync check")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        assert report is not None
        print("[ok] suggestions bin report sync check")
        print(f"  - items={report['summary']['total']}")
        print(f"  - implemented={report['summary']['implemented']}")
        print(f"  - {output_path.as_posix()}")
        return 0

    report, issues = generate_report(root)
    if issues:
        print("[fail] suggestions bin report generation")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    assert report is not None  # for type checking
    out_path = (root / output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("[ok] suggestions bin report generated")
    print(f"  - items={report['summary']['total']}")
    print(f"  - implemented={report['summary']['implemented']}")
    print(f"  - {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
