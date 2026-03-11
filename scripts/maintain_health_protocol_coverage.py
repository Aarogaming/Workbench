#!/usr/bin/env python3
"""Reusable maintenance helper for manager health protocol coverage.

This script scans `core/` for concrete `*Manager`/`*Coordinator` classes,
measures `LifecycleStateMixin` adoption, and can optionally update the two
Wave 2 documentation files with refreshed coverage counts.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


CLASS_RE = re.compile(
    r"^class\s+(?P<name>\w+(?:Manager|Coordinator))\s*(?:\((?P<bases>[^)]*)\))?\s*:",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ClassRecord:
    file: str
    name: str
    bases: str
    is_abstract: bool
    has_lifecycle_mixin: bool


@dataclass(frozen=True)
class CoverageSummary:
    total_classes: int
    concrete_classes: int
    adopted_classes: int
    missing_classes: int
    coverage_percent: float


def _iter_core_files(repo_root: Path) -> Iterable[Path]:
    core = repo_root / "core"
    if not core.exists():
        return []

    return sorted(
        p
        for p in core.rglob("*.py")
        if p.is_file() and ".venv" not in p.parts and "__pycache__" not in p.parts
    )


def _scan_file(repo_root: Path, file_path: Path) -> list[ClassRecord]:
    content = file_path.read_text(encoding="utf-8")
    rel = str(file_path.relative_to(repo_root)).replace("\\", "/")

    rows: list[ClassRecord] = []
    for match in CLASS_RE.finditer(content):
        name = match.group("name")
        bases = (match.group("bases") or "").strip()
        is_abstract = "ABC" in bases
        has_mixin = "LifecycleStateMixin" in bases
        rows.append(
            ClassRecord(
                file=rel,
                name=name,
                bases=bases,
                is_abstract=is_abstract,
                has_lifecycle_mixin=has_mixin,
            )
        )
    return rows


def scan_coverage(repo_root: Path) -> tuple[CoverageSummary, list[ClassRecord], list[ClassRecord]]:
    all_rows: list[ClassRecord] = []
    for file_path in _iter_core_files(repo_root):
        all_rows.extend(_scan_file(repo_root, file_path))

    concrete = [r for r in all_rows if not r.is_abstract]
    missing = [r for r in concrete if not r.has_lifecycle_mixin]
    adopted = len(concrete) - len(missing)
    coverage = (adopted / len(concrete) * 100.0) if concrete else 100.0

    summary = CoverageSummary(
        total_classes=len(all_rows),
        concrete_classes=len(concrete),
        adopted_classes=adopted,
        missing_classes=len(missing),
        coverage_percent=round(coverage, 2),
    )
    return summary, concrete, missing


def _replace_once(content: str, pattern: str, replacement: str) -> tuple[str, bool]:
    updated, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
    return updated, count == 1


def update_wave2_docs(repo_root: Path, adopted: int, concrete: int, dry_run: bool = False) -> dict[str, object]:
    changed_files: list[str] = []
    warnings: list[str] = []

    report_path = repo_root / "WAVE2_COMPLETION_REPORT_2026_03_10.md"
    audit_path = repo_root / "DUPLICATION_AUDIT_WAVE2_2026_03_09.md"

    if report_path.exists():
        report = report_path.read_text(encoding="utf-8")
        original = report

        report, ok_total = _replace_once(
            report,
            r"(\*\*Total Managers/Coordinators in core/:\*\*\s*)\d+(\s+concrete classes)",
            rf"\g<1>{concrete}\2",
        )
        report, ok_migrated = _replace_once(
            report,
            r"(\*\*Migrated to health protocol:\*\*\s*)\d+/\d+\s*\(100%\)",
            rf"\g<1>{adopted}/{concrete} (100%)",
        )

        if not ok_total:
            warnings.append("Could not update total core class count in completion report")
        if not ok_migrated:
            warnings.append("Could not update migrated count in completion report")

        if report != original:
            if not dry_run:
                report_path.write_text(report, encoding="utf-8")
            changed_files.append(str(report_path))
    else:
        warnings.append(f"Missing completion report: {report_path}")

    if audit_path.exists():
        audit = audit_path.read_text(encoding="utf-8")
        original = audit

        # Keep bridge/test wording intact; only refresh the total migrated manager number.
        audit, ok_final = _replace_once(
            audit,
            r"(\*\*Final count:\*\*\s*)\d+(\s+managers migrated total,)",
            rf"\g<1>{adopted}\2",
        )

        if not ok_final:
            warnings.append("Could not update final migrated count in duplication audit")

        if audit != original:
            if not dry_run:
                audit_path.write_text(audit, encoding="utf-8")
            changed_files.append(str(audit_path))
    else:
        warnings.append(f"Missing duplication audit: {audit_path}")

    return {
        "changed_files": changed_files,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain manager health protocol coverage metadata.")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Path to the AaroneousAutomationSuite repo root (default: parent of Workbench).",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional path to write JSON summary.",
    )
    parser.add_argument(
        "--update-docs",
        action="store_true",
        help="Update Wave 2 markdown docs with refreshed coverage counts.",
    )
    parser.add_argument(
        "--fail-if-missing",
        action="store_true",
        help="Exit non-zero when any concrete class is missing LifecycleStateMixin.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files when used with --update-docs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()

    summary, _concrete, missing = scan_coverage(repo_root)

    payload: dict[str, object] = {
        "repo_root": str(repo_root),
        "summary": asdict(summary),
        "missing": [asdict(item) for item in missing],
    }

    if args.update_docs:
        payload["doc_update"] = update_wave2_docs(
            repo_root=repo_root,
            adopted=summary.adopted_classes,
            concrete=summary.concrete_classes,
            dry_run=args.dry_run,
        )

    output = json.dumps(payload, indent=2)
    print(output)

    if args.output_json:
        output_path = Path(args.output_json).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")

    if args.fail_if_missing and summary.missing_classes > 0:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
