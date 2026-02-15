#!/usr/bin/env python3
"""Run pytest for tests mapped to changed files."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _git_changed_files(base_ref: str | None) -> list[str]:
    if base_ref:
        cmd = ["git", "diff", "--name-only", f"{base_ref}...HEAD"]
    else:
        cmd = ["git", "status", "--porcelain"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if base_ref:
        return lines

    paths: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if path:
            paths.append(path)
    return paths


def _select_tests(changed_files: list[str], root: Path) -> list[str]:
    tests_root = root / "tests"
    all_tests = sorted(str(path) for path in tests_root.glob("test_*.py"))
    if not changed_files:
        return []

    changed_tokens = {Path(path).stem.lower() for path in changed_files}
    selected: set[str] = set()
    for test_path in all_tests:
        stem = Path(test_path).stem.lower().replace("test_", "")
        for token in changed_tokens:
            if token and (token in stem or stem in token):
                selected.add(test_path)

    # Explicit contract mappings for high-signal modules.
    changed = set(changed_files)
    if any(path.startswith("plugins/workflow_engine.py") for path in changed):
        selected.add(str(tests_root / "test_phase0_smoke.py"))
    if any(path.startswith("plugins/mcp_auth.py") for path in changed):
        selected.add(str(tests_root / "test_phase0_smoke.py"))
    if any(path.startswith("scripts/validate_workspace_index.py") for path in changed):
        selected.add(str(tests_root / "test_validate_workspace_index.py"))
    if any(path.startswith("scripts/eval_report.py") for path in changed):
        selected.add(str(tests_root / "test_eval_report.py"))
    if any(path.startswith("scripts/check_workflow_pinning.py") for path in changed):
        selected.add(str(tests_root / "test_check_workflow_pinning.py"))
    if any(path.startswith("scripts/check_workflow_pinning_exceptions.py") for path in changed):
        selected.add(str(tests_root / "test_check_workflow_pinning_exceptions.py"))
    if any(path.startswith("scripts/check_scorecard_threshold.py") for path in changed):
        selected.add(str(tests_root / "test_check_scorecard_threshold.py"))
    if any(path.startswith("scripts/verify_attestations.py") for path in changed):
        selected.add(str(tests_root / "test_verify_attestations.py"))
    if any(path.startswith("scripts/update_scorecard_history.py") for path in changed):
        selected.add(str(tests_root / "test_update_scorecard_history.py"))
    if any(path.startswith("scripts/check_secret_hygiene.py") for path in changed):
        selected.add(str(tests_root / "test_check_secret_hygiene.py"))
    if any(path.startswith("scripts/check_plugin_contracts.py") for path in changed):
        selected.add(str(tests_root / "test_check_plugin_contracts.py"))

    return sorted(selected)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run pytest for changed-file impacts.")
    parser.add_argument(
        "--base-ref",
        default=None,
        help="Git base ref for diff selection (example: origin/main).",
    )
    parser.add_argument(
        "--fallback-all",
        action="store_true",
        help="Run full pytest when no mapped tests are found.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    changed = _git_changed_files(args.base_ref)
    selected = _select_tests(changed, root)

    if selected:
        cmd = ["pytest", "-q", *selected]
    elif args.fallback_all:
        cmd = ["pytest", "-q"]
    else:
        print("No mapped tests for changed files.")
        return 0

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
