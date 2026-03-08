#!/usr/bin/env python3
"""Validate committed run_summary.json files."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Sequence


def _git_ls_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def committed_run_summary_paths(root: Path, tracked_files: Sequence[str] | None = None) -> list[str]:
    paths = list(tracked_files) if tracked_files is not None else _git_ls_files(root)
    return sorted(
        (root / relative).as_posix()
        for relative in paths
        if relative.replace("\\", "/").endswith("run_summary.json")
    )


def _run_validator(root: Path, summary_path: Path) -> tuple[bool, str]:
    relative = str(summary_path.resolve().relative_to(root.resolve()))
    result = subprocess.run(
        ["python3", "scripts/validate_run_summary.py", "--path", relative],
        cwd=root,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate all committed run_summary.json artifacts."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = (
        Path(args.root).resolve()
        if args.root
        else Path(__file__).resolve().parents[1]
    )
    paths = committed_run_summary_paths(root)
    if not paths:
        print("[ok] no committed run_summary.json files found")
        return 0

    any_failures = False
    for path in paths:
        ok, output = _run_validator(root, Path(path))
        if output.strip():
            print(output.rstrip())
        if not ok:
            any_failures = True

    return 1 if any_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
