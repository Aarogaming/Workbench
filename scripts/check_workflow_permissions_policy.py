#!/usr/bin/env python3
"""Validate least-privilege GitHub Actions permission policy."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


WORKFLOWS: tuple[str, ...] = (
    ".github/workflows/ci.yml",
    ".github/workflows/codeql-actions-security.yml",
    ".github/workflows/dependency-review.yml",
    ".github/workflows/nightly-evals.yml",
    ".github/workflows/policy-review.yml",
    ".github/workflows/reusable-forge-gates.yml",
    ".github/workflows/reusable-policy-review.yml",
    ".github/workflows/reusable-scorecards.yml",
    ".github/workflows/scorecards.yml",
    ".github/workflows/size-check.yml",
    ".github/workflows/verify-nightly-attestations.yml",
)

EXPECTED_WORKFLOW_PERMISSIONS: dict[str, dict[str, str]] = {
    ".github/workflows/ci.yml": {"contents": "read"},
    ".github/workflows/codeql-actions-security.yml": {
        "contents": "read",
        "security-events": "write",
    },
    ".github/workflows/dependency-review.yml": {
        "contents": "read",
        "pull-requests": "write",
    },
    ".github/workflows/nightly-evals.yml": {"contents": "read"},
    ".github/workflows/policy-review.yml": {"contents": "read"},
    ".github/workflows/reusable-forge-gates.yml": {"contents": "read"},
    ".github/workflows/reusable-policy-review.yml": {"contents": "read"},
    ".github/workflows/reusable-scorecards.yml": {"contents": "read"},
    ".github/workflows/scorecards.yml": {"contents": "read"},
    ".github/workflows/size-check.yml": {"contents": "read"},
    ".github/workflows/verify-nightly-attestations.yml": {"contents": "read"},
}

EXPECTED_JOB_PERMISSIONS: dict[str, dict[str, dict[str, str]]] = {
    ".github/workflows/codeql-actions-security.yml": {
        "analyze": {
            "contents": "read",
            "security-events": "write",
        }
    },
    ".github/workflows/nightly-evals.yml": {
        "nightly-evals": {
            "contents": "read",
            "id-token": "write",
            "attestations": "write",
            "artifact-metadata": "write",
        }
    },
    ".github/workflows/reusable-scorecards.yml": {
        "analysis": {
            "contents": "read",
            "security-events": "write",
            "id-token": "write",
        }
    },
    ".github/workflows/scorecards.yml": {
        "scorecards": {
            "contents": "read",
            "security-events": "write",
            "id-token": "write",
        }
    },
    ".github/workflows/verify-nightly-attestations.yml": {
        "verify-attestations": {
            "actions": "read",
            "contents": "read",
            "attestations": "read",
        }
    },
}

JOB_HEADER_RE = re.compile(r"^[A-Za-z0-9_-]+:$")


def _indent(raw_line: str) -> int:
    return len(raw_line) - len(raw_line.lstrip(" "))


def _parse_permissions_map(
    lines: list[str],
    start_index: int,
    base_indent: int,
) -> dict[str, str]:
    line = lines[start_index]
    suffix = line.split(":", 1)[1].strip()
    if suffix:
        return {"__scalar__": suffix}

    parsed: dict[str, str] = {}
    index = start_index + 1
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue
        indent = _indent(raw)
        if indent <= base_indent:
            break
        if indent == base_indent + 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            parsed[key.strip()] = value.strip()
        index += 1
    return parsed


def _parse_top_level_permissions(content: str) -> dict[str, str] | None:
    lines = content.splitlines()
    for idx, raw in enumerate(lines):
        if raw.lstrip() != raw:
            continue
        if raw.startswith("permissions:"):
            return _parse_permissions_map(lines, idx, base_indent=0)
    return None


def _parse_job_permissions(content: str) -> dict[str, dict[str, str]]:
    lines = content.splitlines()
    jobs_index: int | None = None
    for idx, raw in enumerate(lines):
        if raw.lstrip() == raw and raw.startswith("jobs:"):
            jobs_index = idx
            break
    if jobs_index is None:
        return {}

    parsed: dict[str, dict[str, str]] = {}
    index = jobs_index + 1
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue
        indent = _indent(raw)
        if indent == 0:
            break
        if indent == 2 and JOB_HEADER_RE.match(stripped):
            job_name = stripped[:-1]
            end = index + 1
            while end < len(lines):
                end_raw = lines[end]
                end_stripped = end_raw.strip()
                if not end_stripped:
                    end += 1
                    continue
                end_indent = _indent(end_raw)
                if end_indent == 0:
                    break
                if end_indent == 2 and JOB_HEADER_RE.match(end_stripped):
                    break
                end += 1

            permissions_map: dict[str, str] | None = None
            for cursor in range(index + 1, end):
                candidate = lines[cursor]
                candidate_stripped = candidate.strip()
                if not candidate_stripped:
                    continue
                if _indent(candidate) == 4 and candidate_stripped.startswith("permissions:"):
                    permissions_map = _parse_permissions_map(lines, cursor, base_indent=4)
                    break

            if permissions_map is not None:
                parsed[job_name] = permissions_map
            index = end
            continue
        index += 1

    return parsed


def _contains_macro_permission(permissions: dict[str, str]) -> bool:
    return any(value in {"read-all", "write-all"} for value in permissions.values())


def _fmt_permissions(permissions: dict[str, str]) -> str:
    return json.dumps(permissions, sort_keys=True)


def check_workflow_content(
    content: str,
    workflow_label: str,
    expected_workflow_permissions: dict[str, str] | None = None,
    expected_job_permissions: dict[str, dict[str, str]] | None = None,
) -> list[str]:
    issues: list[str] = []
    expected_top = (
        expected_workflow_permissions
        if expected_workflow_permissions is not None
        else EXPECTED_WORKFLOW_PERMISSIONS.get(workflow_label)
    )
    if expected_top is None:
        return [f"{workflow_label}: no workflow permission policy mapping"]

    top_permissions = _parse_top_level_permissions(content)
    if top_permissions is None:
        issues.append(f"{workflow_label}: missing top-level permissions block")
    elif "__scalar__" in top_permissions:
        issues.append(f"{workflow_label}: permissions must be a mapping, not scalar")
    else:
        if _contains_macro_permission(top_permissions):
            issues.append(
                f"{workflow_label}: forbidden macro permission detected (read-all/write-all)"
            )
        if top_permissions != expected_top:
            issues.append(
                f"{workflow_label}: top-level permissions={_fmt_permissions(top_permissions)} "
                f"expected={_fmt_permissions(expected_top)}"
            )

    expected_jobs = (
        expected_job_permissions
        if expected_job_permissions is not None
        else EXPECTED_JOB_PERMISSIONS.get(workflow_label, {})
    )
    if expected_jobs:
        actual_job_permissions = _parse_job_permissions(content)
        for job_name, expected in expected_jobs.items():
            actual = actual_job_permissions.get(job_name)
            if actual is None:
                issues.append(f"{workflow_label}: job '{job_name}' missing permissions block")
                continue
            if "__scalar__" in actual:
                issues.append(
                    f"{workflow_label}: job '{job_name}' permissions must be a mapping, not scalar"
                )
                continue
            if _contains_macro_permission(actual):
                issues.append(
                    f"{workflow_label}: job '{job_name}' uses forbidden macro permission"
                )
            if actual != expected:
                issues.append(
                    f"{workflow_label}: job '{job_name}' permissions={_fmt_permissions(actual)} "
                    f"expected={_fmt_permissions(expected)}"
                )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check least-privilege permissions policy for workflows."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    all_issues: list[str] = []

    for relative in WORKFLOWS:
        workflow_path = root / relative
        if not workflow_path.exists():
            issue = f"{relative}: file not found"
            all_issues.append(issue)
            print(f"[fail] {relative}")
            print(f"  - {issue}")
            continue

        issues = check_workflow_content(
            workflow_path.read_text(encoding="utf-8"),
            relative,
        )
        if issues:
            all_issues.extend(issues)
            print(f"[fail] {relative}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[ok] {relative}")

    if all_issues:
        print(f"[summary] workflows={len(WORKFLOWS)} failed={len(all_issues)}")
        return 1

    print(f"[summary] workflows={len(WORKFLOWS)} failed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
