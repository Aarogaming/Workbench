#!/usr/bin/env python3
"""Validate SSDF SP 800-218 mapping coverage for quality gates/workflows."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MAPPING_DOC = Path("docs/research/SSDF_SP800_218_QUALITY_GATE_MAPPING.md")
GATES_SOURCE = Path("scripts/run_quality_gates.py")

REQUIRED_SECTION_HEADERS: tuple[str, ...] = (
    "## Script Gate Mapping",
    "## Workflow Enforcement Mapping",
)

REQUIRED_WORKFLOW_ROWS: tuple[str, ...] = (
    ".github/workflows/ci.yml",
    ".github/workflows/size-check.yml",
)

SSDF_TOKEN_RE = re.compile(r"\b(?:PO|PS|PW|RV|GV)\.\d+\.\d+\b")
GATE_NAME_RE = re.compile(r'name="([^"]+)"')


def _extract_gate_names(root: Path) -> list[str]:
    source_path = root / GATES_SOURCE
    if not source_path.exists():
        return []

    content = source_path.read_text(encoding="utf-8")
    seen: set[str] = set()
    names: list[str] = []
    for match in GATE_NAME_RE.finditer(content):
        name = match.group(1)
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def _find_row(content: str, key: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("|") and f"`{key}`" in line:
            return line
    return None


def check_mapping(root: Path) -> list[str]:
    issues: list[str] = []
    mapping_path = root / MAPPING_DOC
    if not mapping_path.exists():
        return [f"missing required mapping doc: {MAPPING_DOC.as_posix()}"]

    content = mapping_path.read_text(encoding="utf-8")
    for header in REQUIRED_SECTION_HEADERS:
        if header not in content:
            issues.append(f"missing section in {MAPPING_DOC.as_posix()}: {header}")

    gate_names = _extract_gate_names(root)
    if not gate_names:
        issues.append(f"unable to extract gate names from {GATES_SOURCE.as_posix()}")
        return issues

    for gate_name in gate_names:
        row = _find_row(content, gate_name)
        if row is None:
            issues.append(
                f"missing gate mapping row in {MAPPING_DOC.as_posix()}: {gate_name}"
            )
            continue
        if SSDF_TOKEN_RE.search(row) is None:
            issues.append(
                f"gate mapping row missing SSDF token in {MAPPING_DOC.as_posix()}: {gate_name}"
            )

    for workflow_path in REQUIRED_WORKFLOW_ROWS:
        row = _find_row(content, workflow_path)
        if row is None:
            issues.append(
                f"missing workflow mapping row in {MAPPING_DOC.as_posix()}: {workflow_path}"
            )
            continue
        if SSDF_TOKEN_RE.search(row) is None:
            issues.append(
                f"workflow mapping row missing SSDF token in {MAPPING_DOC.as_posix()}: "
                f"{workflow_path}"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SSDF quality-gate mapping document coverage."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_mapping(root)
    if issues:
        print("[fail] ssdf quality-gate mapping check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] ssdf quality-gate mapping check")
    print(f"  - {MAPPING_DOC.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
