#!/usr/bin/env python3
"""Validate NIST SP 800-61 Rev. 3 lifecycle mapping in docs/OPERATIONS.md."""

from __future__ import annotations

import argparse
from pathlib import Path


OPERATIONS_DOC = Path("docs/OPERATIONS.md")

REQUIRED_SECTIONS: tuple[str, ...] = (
    "## Incident response (NIST SP 800-61 Rev. 3 lifecycle mapping)",
    "1. Prepare:",
    "2. Detect and Analyze:",
    "3. Contain, Eradicate, and Recover:",
    "4. Post-Incident Activity:",
)

REQUIRED_COMMAND_SNIPPETS: tuple[str, ...] = (
    "python3 scripts/check_chimera_packets.py",
    "python3 scripts/run_quality_gates.py",
    "python3 scripts/generate_run_summary.py",
    "python3 scripts/validate_run_summary.py",
)


def check_operations_doc(root: Path) -> list[str]:
    issues: list[str] = []
    operations_path = root / OPERATIONS_DOC
    if not operations_path.exists():
        return [f"missing required operations doc: {OPERATIONS_DOC.as_posix()}"]

    content = operations_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(f"missing lifecycle section in {OPERATIONS_DOC.as_posix()}: {section}")

    for snippet in REQUIRED_COMMAND_SNIPPETS:
        if snippet not in content:
            issues.append(
                f"missing lifecycle command snippet in {OPERATIONS_DOC.as_posix()}: {snippet}"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate NIST lifecycle mapping in docs/OPERATIONS.md."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_operations_doc(root)
    if issues:
        print("[fail] operations nist mapping check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] operations nist mapping check")
    print(f"  - {OPERATIONS_DOC.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
