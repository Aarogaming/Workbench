#!/usr/bin/env python3
"""Run core Workbench quality gates in a single command."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class Gate:
    name: str
    cmd: list[str]


def _run_gate(gate: Gate, cwd: Path) -> tuple[bool, int]:
    print(f"[gate] {gate.name}")
    result = subprocess.run(gate.cmd, cwd=cwd)
    ok = result.returncode == 0
    if ok:
        print(f"[pass] {gate.name}")
    else:
        print(f"[fail] {gate.name} (exit {result.returncode})")
    return ok, int(result.returncode)


def _build_gates(args: argparse.Namespace) -> Sequence[Gate]:
    gates: list[Gate] = [
        Gate(
            name="secret-hygiene",
            cmd=["python3", "scripts/check_secret_hygiene.py", "--all", "--strict"],
        ),
        Gate(
            name="git-size",
            cmd=["python3", "scripts/check_git_size.py"],
        ),
        Gate(
            name="compileall",
            cmd=["python3", "-m", "compileall", "-q", "Assets", "plugins", "Tools"],
        ),
        Gate(
            name="workflow-pinning",
            cmd=["python3", "scripts/check_workflow_pinning.py"],
        ),
        Gate(
            name="workflow-pinning-exceptions",
            cmd=["python3", "scripts/check_workflow_pinning_exceptions.py"],
        ),
    ]
    if not args.skip_tests:
        gates.append(Gate(name="pytest", cmd=["pytest", "-q"]))
    gates.append(
        Gate(
            name="workspace-index",
            cmd=[
                "python3",
                "scripts/validate_workspace_index.py",
                "--suite-root",
                "..",
                "--strict-enforced-only",
                "--ignore-submodule-dirty",
                "--ignore-submodule-ahead",
            ],
        )
    )
    if not args.skip_evals:
        gates.append(
            Gate(
                name="eval-report",
                cmd=["python3", "scripts/eval_report.py", "--baseline", "evals/baselines/main.json"],
            )
        )
    return gates


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Workbench quality gates.")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest gate.",
    )
    parser.add_argument(
        "--skip-evals",
        action="store_true",
        help="Skip eval-report gate.",
    )
    args = parser.parse_args()

    workbench_root = Path(__file__).resolve().parents[1]
    gates = _build_gates(args)
    failures: list[tuple[str, int]] = []
    for gate in gates:
        ok, code = _run_gate(gate, cwd=workbench_root)
        if not ok:
            failures.append((gate.name, code))

    print(f"[summary] total={len(gates)} failed={len(failures)}")
    if failures:
        for name, code in failures:
            print(f"  - {name}: exit {code}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
