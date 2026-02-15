#!/usr/bin/env python3
"""Validate that GitHub Actions workflow `uses:` dependencies are SHA pinned."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


USES_RE = re.compile(r"^\s*(?:-\s*)?uses\s*:\s*(.+?)\s*(?:#.*)?$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class Issue:
    path: str
    line: int
    uses: str
    reason: str


@dataclass
class WorkflowPinningException:
    exception_id: str
    workflow: str
    uses: str
    reason: str
    review_by: str


def _normalize_uses(value: str) -> str:
    text = value.strip().strip("'").strip('"')
    # Preserve matrix/env expressions as-is for error reporting.
    return text


def _validate_uses_value(value: str) -> str | None:
    text = _normalize_uses(value)
    if not text:
        return "empty uses reference"
    if text.startswith("./"):
        return None
    if text.startswith("docker://"):
        return None
    if "${{" in text:
        return "dynamic uses reference is not allowed"
    if "@" not in text:
        return "missing @ref in uses reference"

    _, ref = text.rsplit("@", 1)
    if SHA_RE.fullmatch(ref):
        return None
    return "uses reference is not pinned to a full commit SHA"


def _parse_iso_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except Exception:
        return None


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _load_active_exceptions(
    path: Path, today: dt.date
) -> tuple[dict[tuple[str, str], WorkflowPinningException], list[str], list[str]]:
    if not path.exists():
        return {}, [], []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, [f"invalid JSON in exceptions file `{path}`: {exc}"], []

    if not isinstance(payload, dict):
        return {}, [f"exceptions file `{path}` must contain a JSON object"], []

    rows = payload.get("exceptions", [])
    if not isinstance(rows, list):
        return {}, [f"exceptions file `{path}` has non-list `exceptions` value"], []

    active: dict[tuple[str, str], WorkflowPinningException] = {}
    invalid: list[str] = []
    expired: list[str] = []
    seen_ids: set[str] = set()
    seen_keys: set[tuple[str, str]] = set()

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
        review_by = str(row.get("review_by", "")).strip()
        review_date = _parse_iso_date(review_by)

        if (
            not exception_id
            or not workflow
            or not uses
            or not reason
            or review_date is None
        ):
            invalid.append(
                f"row {idx}: requires non-empty id/workflow/uses/reason and ISO review_by date"
            )
            continue
        if exception_id in seen_ids:
            invalid.append(f"row {idx}: duplicate id `{exception_id}`")
            continue

        key = (workflow, uses)
        if key in seen_keys:
            invalid.append(
                f"row {idx}: duplicate workflow+uses pair `{workflow}` `{uses}`"
            )
            continue

        seen_ids.add(exception_id)
        seen_keys.add(key)
        if review_date < today:
            expired.append(
                f"id `{exception_id}` for `{workflow}` `{uses}` expired on {review_by}"
            )
            continue

        active[key] = WorkflowPinningException(
            exception_id=exception_id,
            workflow=workflow,
            uses=uses,
            reason=reason,
            review_by=review_by,
        )

    return active, invalid, expired


def _scan_workflow(
    path: Path,
    root: Path,
    active_exceptions: dict[tuple[str, str], WorkflowPinningException],
) -> tuple[list[Issue], list[dict[str, str]]]:
    issues: list[Issue] = []
    excepted: list[dict[str, str]] = []
    rel_path = str(path.relative_to(root))
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines, start=1):
        match = USES_RE.match(line)
        if not match:
            continue
        value = match.group(1)
        normalized_uses = _normalize_uses(value)
        reason = _validate_uses_value(value)
        if reason:
            exception = active_exceptions.get((rel_path, normalized_uses))
            if exception is not None:
                excepted.append(
                    {
                        "exception_id": exception.exception_id,
                        "path": rel_path,
                        "line": str(idx),
                        "uses": normalized_uses,
                        "review_by": exception.review_by,
                        "reason": exception.reason,
                    }
                )
                continue
            issues.append(
                Issue(
                    path=rel_path,
                    line=idx,
                    uses=normalized_uses,
                    reason=reason,
                )
            )
    return issues, excepted


def _workflow_files(root: Path, workflow_glob: str) -> list[Path]:
    workflow_root = root / ".github" / "workflows"
    return sorted(workflow_root.glob(workflow_glob))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check GitHub workflow actions are pinned to commit SHAs."
    )
    parser.add_argument(
        "--workflow-glob",
        default="*.yml",
        help="Workflow glob inside .github/workflows (default: *.yml).",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/workflow_pinning_audit.json",
        help="JSON report output path relative to repo root.",
    )
    parser.add_argument(
        "--exceptions-file",
        default=".github/workflow-pinning-exceptions.json",
        help="Exception policy JSON relative to repo root.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    files = _workflow_files(root, args.workflow_glob)
    exceptions_path = (root / args.exceptions_file).resolve()
    today = dt.date.today()
    active_exceptions, invalid_exceptions, expired_exceptions = _load_active_exceptions(
        exceptions_path, today
    )

    issues: list[Issue] = []
    excepted: list[dict[str, str]] = []
    for file in files:
        file_issues, file_excepted = _scan_workflow(file, root, active_exceptions)
        issues.extend(file_issues)
        excepted.extend(file_excepted)

    report: dict[str, Any] = {
        "workflow_count": len(files),
        "issue_count": len(issues),
        "excepted_count": len(excepted),
        "exception_summary": {
            "exceptions_file": _display_path(exceptions_path, root),
            "active_count": len(active_exceptions),
            "invalid_count": len(invalid_exceptions),
            "expired_count": len(expired_exceptions),
        },
        "exceptions": {
            "invalid": invalid_exceptions,
            "expired": expired_exceptions,
            "applied": excepted,
        },
        "issues": [
            {
                "path": issue.path,
                "line": issue.line,
                "uses": issue.uses,
                "reason": issue.reason,
            }
            for issue in issues
        ],
    }

    out_path = (root / args.json_out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Workflow files: {len(files)}")
    print(f"Issues: {len(issues)}")
    print(f"Excepted uses: {len(excepted)}")
    print(f"Invalid exceptions: {len(invalid_exceptions)}")
    print(f"Expired exceptions: {len(expired_exceptions)}")
    print(f"JSON report: {out_path}")
    for row in invalid_exceptions:
        print(f"- exception invalid: {row}")
    for row in expired_exceptions:
        print(f"- exception expired: {row}")
    for issue in issues:
        print(f"- {issue.path}:{issue.line} `{issue.uses}` -> {issue.reason}")
    has_error = bool(issues or invalid_exceptions or expired_exceptions)
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
