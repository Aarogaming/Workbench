#!/usr/bin/env python3
"""Validate suggestions-bin status coverage and report sync contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SUGGESTIONS_BIN_DOC = Path("docs/SUGGESTIONS_BIN.md")
SUGGESTIONS_BIN_REPORT = Path("docs/reports/suggestions_bin.json")

SUGGESTION_RE = re.compile(r"^- `WB-SUG-(\d+)`")
STATUS_RE = re.compile(r"^- status:\s*`?([a-z_]+)`?")
BACKTICK_TOKEN_RE = re.compile(r"`([^`]+)`")
ALLOWED_STATUSES = {"new", "reviewing", "approved", "scheduled", "implemented", "rejected"}
REPORT_SCHEMA = "cp4b.suggestions_bin_report.v1"
MAX_SUGGESTIONS = 100


def _extract_report_items(path: Path) -> dict[str, str] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("schema_version") != REPORT_SCHEMA:
        return None
    items = payload.get("items")
    if not isinstance(items, list):
        return None

    report: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        suggestion_id = item.get("id")
        status = item.get("status")
        if isinstance(suggestion_id, str) and isinstance(status, str):
            report[suggestion_id] = status.lower()
    return report


def _check_evidence_paths(root: Path, suggestion_id: str, refs: list[str]) -> list[str]:
    issues: list[str] = []
    if not refs:
        issues.append(f"{suggestion_id}: implemented status missing evidence references")
        return issues

    path_like_refs = [
        ref
        for ref in refs
        if "/" in ref and not ref.startswith("http://") and not ref.startswith("https://")
    ]
    if not path_like_refs:
        issues.append(f"{suggestion_id}: implemented status missing local path evidence")
        return issues

    checkable_refs = [
        ref for ref in path_like_refs if not any(ch in ref for ch in "{}<>*?$|")
    ]
    if not checkable_refs:
        return issues

    existing = [(root / ref).exists() for ref in checkable_refs]
    if not any(existing):
        issues.append(
            f"{suggestion_id}: implemented evidence paths not found ({', '.join(checkable_refs[:3])})"
        )
    return issues


def check_suggestions_bin(root: Path) -> list[str]:
    path = root / SUGGESTIONS_BIN_DOC
    if not path.exists():
        return [f"missing suggestions bin doc: {SUGGESTIONS_BIN_DOC.as_posix()}"]

    lines = path.read_text(encoding="utf-8").splitlines()
    issues: list[str] = []
    seen_ids: set[str] = set()
    parsed_statuses: dict[str, str] = {}
    found = 0

    for idx, line in enumerate(lines):
        match = SUGGESTION_RE.match(line.strip())
        if not match:
            continue

        found += 1
        suggestion_id = f"WB-SUG-{int(match.group(1)):03d}"
        if suggestion_id in seen_ids:
            issues.append(f"duplicate suggestion id: {suggestion_id}")
        seen_ids.add(suggestion_id)

        status_value: str | None = None
        status_line: str | None = None
        cursor = idx + 1
        while cursor < len(lines):
            stripped = lines[cursor].strip()
            if stripped.startswith("## ") or SUGGESTION_RE.match(stripped):
                break
            status_match = STATUS_RE.match(stripped)
            if status_match:
                status_value = status_match.group(1).lower()
                status_line = stripped
                break
            cursor += 1

        label = suggestion_id
        if status_value is None:
            issues.append(f"{label}: missing status line")
            continue
        if status_value not in ALLOWED_STATUSES:
            issues.append(
                f"{label}: invalid status '{status_value}' (allowed: {sorted(ALLOWED_STATUSES)})"
            )
            continue
        parsed_statuses[label] = status_value
        if status_value == "implemented":
            refs = []
            if status_line:
                refs = BACKTICK_TOKEN_RE.findall(status_line)
                if refs and refs[0].lower() == status_value:
                    refs = refs[1:]
            issues.extend(_check_evidence_paths(root, label, refs))

    if found == 0:
        issues.append(f"no suggestion entries found in {SUGGESTIONS_BIN_DOC.as_posix()}")
        return issues
    if found > MAX_SUGGESTIONS:
        issues.append(
            f"suggestion count exceeds cap ({MAX_SUGGESTIONS}): found={found}"
        )

    report_path = root / SUGGESTIONS_BIN_REPORT
    if not report_path.exists():
        issues.append(f"missing report file: {SUGGESTIONS_BIN_REPORT.as_posix()}")
        return issues

    report_items = _extract_report_items(report_path)
    if report_items is None:
        issues.append(
            f"invalid or unsupported report schema in {SUGGESTIONS_BIN_REPORT.as_posix()}"
        )
        return issues

    missing_in_report = sorted(set(parsed_statuses) - set(report_items))
    if missing_in_report:
        issues.append(
            "report missing suggestion ids: " + ", ".join(missing_in_report[:5])
        )

    extra_in_report = sorted(set(report_items) - set(parsed_statuses))
    if extra_in_report:
        issues.append(
            "report has unexpected suggestion ids: " + ", ".join(extra_in_report[:5])
        )

    for suggestion_id, status in parsed_statuses.items():
        report_status = report_items.get(suggestion_id)
        if report_status is None:
            continue
        if status != report_status:
            issues.append(
                f"{suggestion_id}: status mismatch markdown='{status}' report='{report_status}'"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate suggestion status coverage and vocabulary."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_suggestions_bin(root)
    if issues:
        print("[fail] suggestions bin status check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    content_lines = (root / SUGGESTIONS_BIN_DOC).read_text(encoding="utf-8").splitlines()
    suggestions_total = sum(
        1 for line in content_lines if SUGGESTION_RE.match(line.strip())
    )
    implemented_total = sum(
        1 for line in content_lines if re.search(r"- status:\s*`implemented`", line)
    )
    print(
        f"[ok] suggestions bin status check suggestions={suggestions_total} implemented={implemented_total}"
    )
    print(f"  - {SUGGESTIONS_BIN_DOC.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
