#!/usr/bin/env python3
"""Generate a deterministic SHA256 artifact digest report."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "cp2.artifact_digest_report.v1"


def _parse_artifact_arg(raw: str) -> tuple[str, str]:
    value = raw.strip()
    if not value:
        raise ValueError("artifact argument must be non-empty")
    if "=" in value:
        name, path = value.split("=", 1)
        name = name.strip()
        path = path.strip()
    else:
        path = value
        name = Path(path).stem
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


def generate_report(
    root: Path,
    artifacts: list[str],
    source: str,
) -> tuple[dict[str, Any], list[str]]:
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_names: set[str] = set()

    for raw in artifacts:
        try:
            name, artifact_path = _parse_artifact_arg(raw)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if name in seen_names:
            errors.append(f"duplicate artifact name '{name}'")
            continue
        seen_names.add(name)

        resolved = Path(artifact_path)
        if not resolved.is_absolute():
            resolved = (root / artifact_path).resolve()
        if not resolved.exists():
            errors.append(f"artifact '{name}' missing file: {resolved}")
            continue
        if not resolved.is_file():
            errors.append(f"artifact '{name}' path is not a file: {resolved}")
            continue

        try:
            relative_path = str(resolved.relative_to(root))
        except ValueError:
            relative_path = str(resolved)

        entries.append(
            {
                "name": name,
                "path": relative_path,
                "sha256": _sha256(resolved),
                "size_bytes": resolved.stat().st_size,
            }
        )

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "summary": {
            "total": len(entries),
        },
        "artifacts": sorted(entries, key=lambda item: item["name"]),
    }
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate artifact SHA256 report for integrity evidence."
    )
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help=(
            "Artifact definition in NAME=PATH format. If NAME omitted, "
            "file stem is used."
        ),
    )
    parser.add_argument(
        "--source",
        default="workflow",
        help="Source label for this digest report.",
    )
    parser.add_argument(
        "--output",
        default="docs/reports/artifact_digest_report.json",
        help="Output JSON path relative to repo root.",
    )
    args = parser.parse_args()

    if not args.artifact:
        print("At least one --artifact is required.")
        return 1

    root = Path(__file__).resolve().parents[1]
    report, errors = generate_report(
        root=root,
        artifacts=args.artifact,
        source=args.source.strip() or "workflow",
    )
    if errors:
        print("[fail] artifact digest report generation issues")
        for item in errors:
            print(f"  - {item}")
        return 1

    out_path = (root / args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"[ok] digest report: {out_path}")
    print(f"[summary] artifacts={report['summary']['total']} source={report['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
