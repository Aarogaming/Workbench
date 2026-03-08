#!/usr/bin/env python3
"""Generate dependency snapshot and SPDX SBOM artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import subprocess
from pathlib import Path


SNAPSHOT_FILENAME = "dependency_snapshot.json"
REQUIREMENTS_FILENAME = "dependency_snapshot_requirements.txt"
SPDX_FILENAME = "dependency_sbom.spdx.json"


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_freeze_lines(raw_lines: list[str]) -> list[str]:
    cleaned = [line.strip() for line in raw_lines if line.strip() and not line.strip().startswith("#")]
    unique = sorted(set(cleaned), key=str.lower)
    return unique


def _pip_freeze() -> list[str]:
    result = subprocess.run(
        ["python3", "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "<no stderr>"
        raise RuntimeError(f"pip freeze failed: {stderr}")
    return _parse_freeze_lines(result.stdout.splitlines())


def _parse_name_version(requirement: str) -> tuple[str, str]:
    if "==" not in requirement:
        return requirement, "UNKNOWN"
    name, version = requirement.split("==", 1)
    return name.strip(), version.strip() or "UNKNOWN"


def _build_snapshot(packages: list[str], generated_at: str) -> dict[str, object]:
    return {
        "schema": "workbench.dependency_snapshot.v1",
        "generated_at_utc": generated_at,
        "python_version": platform.python_version(),
        "package_count": len(packages),
        "packages": packages,
    }


def _build_spdx(packages: list[str], generated_at: str) -> dict[str, object]:
    spdx_packages: list[dict[str, object]] = []
    for idx, requirement in enumerate(packages, start=1):
        name, version = _parse_name_version(requirement)
        spdx_packages.append(
            {
                "SPDXID": f"SPDXRef-Package-{idx}",
                "name": name,
                "versionInfo": version,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "supplier": "NOASSERTION",
            }
        )

    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "workbench-dependency-inventory",
        "documentNamespace": (
            "https://aaroneousautomation.local/workbench/dependency-inventory/"
            + generated_at.replace(":", "-")
        ),
        "creationInfo": {
            "created": generated_at,
            "creators": ["Tool: Workbench generate_dependency_inventory.py"],
        },
        "packages": spdx_packages,
    }


def generate_inventory(
    output_dir: Path,
    freeze_lines: list[str] | None = None,
    generated_at: str | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = generated_at or _utc_now_iso()
    packages = _parse_freeze_lines(freeze_lines) if freeze_lines is not None else _pip_freeze()

    requirements_path = output_dir / REQUIREMENTS_FILENAME
    snapshot_path = output_dir / SNAPSHOT_FILENAME
    spdx_path = output_dir / SPDX_FILENAME

    requirements_path.write_text("\n".join(packages) + ("\n" if packages else ""), encoding="utf-8")
    snapshot_path.write_text(
        json.dumps(_build_snapshot(packages, generated), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    spdx_path.write_text(
        json.dumps(_build_spdx(packages, generated), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return {
        "requirements": requirements_path,
        "snapshot": snapshot_path,
        "spdx": spdx_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate dependency snapshot and SPDX SBOM artifacts."
    )
    parser.add_argument(
        "--output-dir",
        default="docs/reports",
        help="Output directory for generated artifacts.",
    )
    parser.add_argument(
        "--freeze-input",
        default=None,
        help="Optional path to pip-freeze style input file for deterministic generation.",
    )
    args = parser.parse_args()

    freeze_lines: list[str] | None = None
    if args.freeze_input:
        freeze_input_path = Path(args.freeze_input)
        if not freeze_input_path.exists():
            print(f"[fail] freeze input file not found: {freeze_input_path}")
            return 1
        freeze_lines = freeze_input_path.read_text(encoding="utf-8").splitlines()

    try:
        outputs = generate_inventory(
            output_dir=Path(args.output_dir),
            freeze_lines=freeze_lines,
        )
    except RuntimeError as exc:
        print(f"[fail] {exc}")
        return 1

    print("[ok] dependency inventory generated")
    for key in ("requirements", "snapshot", "spdx"):
        print(f"  - {key}: {outputs[key].as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
