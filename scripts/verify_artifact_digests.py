#!/usr/bin/env python3
"""Verify local artifact files against a digest report."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "cp2.artifact_digest_report.v1"


def _parse_artifact_arg(raw: str) -> tuple[str, str]:
    value = raw.strip()
    if not value or "=" not in value:
        raise ValueError(f"artifact '{raw}' must use NAME=PATH format")
    name, path = value.split("=", 1)
    name = name.strip()
    path = path.strip()
    if not name:
        raise ValueError(f"artifact '{raw}' has empty name")
    if not path:
        raise ValueError(f"artifact '{raw}' has empty path")
    return name, path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify_digests(
    root: Path,
    report_path: Path,
    artifacts: list[str],
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not report_path.exists():
        return {}, [f"report file not found: {report_path}"]

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"report is invalid JSON: {exc}"]

    if payload.get("schema_version") != EXPECTED_SCHEMA:
        errors.append(
            f"unsupported schema_version '{payload.get('schema_version')}', "
            f"expected '{EXPECTED_SCHEMA}'"
        )

    raw_entries = payload.get("artifacts")
    if not isinstance(raw_entries, list):
        errors.append("report missing artifacts list")
        raw_entries = []

    expected_by_name: dict[str, dict[str, Any]] = {}
    for row in raw_entries:
        if not isinstance(row, dict):
            errors.append("report artifact row is not an object")
            continue
        name = str(row.get("name", "")).strip()
        sha256 = str(row.get("sha256", "")).strip()
        if not name or not sha256:
            errors.append("report artifact row missing name or sha256")
            continue
        expected_by_name[name] = row

    requested: dict[str, Path] = {}
    for raw in artifacts:
        try:
            name, artifact_path = _parse_artifact_arg(raw)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if name in requested:
            errors.append(f"duplicate input artifact name '{name}'")
            continue
        resolved = Path(artifact_path)
        if not resolved.is_absolute():
            resolved = (root / artifact_path).resolve()
        requested[name] = resolved

    results: list[dict[str, Any]] = []
    missing_files: list[str] = []
    missing_expected: list[str] = []
    digest_mismatch: list[str] = []

    for name, path in sorted(requested.items()):
        if name not in expected_by_name:
            missing_expected.append(name)
            results.append(
                {
                    "name": name,
                    "path": str(path),
                    "status": "missing_expected_digest",
                }
            )
            continue
        if not path.exists() or not path.is_file():
            missing_files.append(name)
            results.append(
                {
                    "name": name,
                    "path": str(path),
                    "status": "missing_file",
                }
            )
            continue

        actual = _sha256(path)
        expected = str(expected_by_name[name]["sha256"])
        if actual != expected:
            digest_mismatch.append(name)
            status = "digest_mismatch"
        else:
            status = "ok"
        results.append(
            {
                "name": name,
                "path": str(path),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "status": status,
            }
        )

    unverified_expected = sorted(set(expected_by_name.keys()) - set(requested.keys()))
    if unverified_expected:
        errors.append(
            "input artifacts missing for expected report entries: "
            + ", ".join(unverified_expected)
        )

    if missing_files:
        errors.append("missing local artifact files: " + ", ".join(sorted(missing_files)))
    if missing_expected:
        errors.append("missing expected digest entries: " + ", ".join(sorted(missing_expected)))
    if digest_mismatch:
        errors.append("digest mismatch artifacts: " + ", ".join(sorted(digest_mismatch)))

    report: dict[str, Any] = {
        "schema_version": "cp2.artifact_digest_verify_report.v1",
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_report_path": str(report_path),
        "summary": {
            "total_input": len(requested),
            "ok": len([row for row in results if row.get("status") == "ok"]),
            "failed": len([row for row in results if row.get("status") != "ok"]),
        },
        "results": results,
        "gate": {
            "pass": len(errors) == 0,
            "reasons": errors,
        },
    }
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify artifact digests against a digest report."
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Digest report JSON path.",
    )
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="Artifact in NAME=PATH format.",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/artifact_digest_verify_report.json",
        help="Output JSON report path relative to repo root.",
    )
    args = parser.parse_args()

    if not args.artifact:
        print("At least one --artifact is required.")
        return 1

    root = Path(__file__).resolve().parents[1]
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = (root / args.report).resolve()

    report, errors = verify_digests(root=root, report_path=report_path, artifacts=args.artifact)

    out_path = (root / args.json_out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if errors:
        print(f"[fail] digest verify report: {out_path}")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(f"[ok] digest verify report: {out_path}")
    print(
        "[summary] "
        f"total_input={report['summary']['total_input']} "
        f"ok={report['summary']['ok']} failed={report['summary']['failed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
