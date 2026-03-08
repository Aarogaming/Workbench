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


def _escape_annotation(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _emit_annotation(level: str, title: str, message: str) -> None:
    print(f"::{level} title={_escape_annotation(title)}::{_escape_annotation(message)}")


def _run_gate(gate: Gate, cwd: Path) -> tuple[bool, int]:
    print(f"[gate] {gate.name}")
    _emit_annotation("notice", "quality-gate-start", f"{gate.name} running")
    result = subprocess.run(gate.cmd, cwd=cwd)
    ok = result.returncode == 0
    if ok:
        print(f"[pass] {gate.name}")
        _emit_annotation("notice", "quality-gate-pass", f"{gate.name} passed")
    else:
        print(f"[fail] {gate.name} (exit {result.returncode})")
        _emit_annotation("error", "quality-gate-fail", f"{gate.name} failed (exit {result.returncode})")
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
        Gate(
            name="chimera-packets",
            cmd=["python3", "scripts/check_chimera_packets.py"],
        ),
        Gate(
            name="suggestions-bin-report-sync",
            cmd=["python3", "scripts/generate_suggestions_bin_report.py", "--check"],
        ),
        Gate(
            name="suggestions-bin-status",
            cmd=["python3", "scripts/check_suggestions_bin_status.py"],
        ),
        Gate(
            name="operations-nist-mapping",
            cmd=["python3", "scripts/check_operations_nist_mapping.py"],
        ),
        Gate(
            name="ssdf-quality-gate-mapping",
            cmd=["python3", "scripts/check_ssdf_quality_gate_mapping.py"],
        ),
        Gate(
            name="dora-reliability-scoreboard",
            cmd=["python3", "scripts/check_dora_reliability_scoreboard.py"],
        ),
        Gate(
            name="campaign-wave-policy",
            cmd=["python3", "scripts/check_campaign_wave_policy.py"],
        ),
        Gate(
            name="openai-async-policy",
            cmd=["python3", "scripts/check_openai_async_policy.py"],
        ),
        Gate(
            name="jetstream-openai-campaign-policy",
            cmd=["python3", "scripts/check_jetstream_openai_campaign_policy.py"],
        ),
        Gate(
            name="workflow-codeql-matrix-policy",
            cmd=["python3", "scripts/check_workflow_codeql_matrix_policy.py"],
        ),
        Gate(
            name="reusable-workflow-governance-policy",
            cmd=["python3", "scripts/check_reusable_workflow_governance_policy.py"],
        ),
        Gate(
            name="jetstream-consumer-openai-loop-policy",
            cmd=["python3", "scripts/check_jetstream_consumer_openai_loop_policy.py"],
        ),
        Gate(
            name="dependency-review-policy",
            cmd=["python3", "scripts/check_dependency_review_policy.py"],
        ),
        Gate(
            name="merge-queue-readiness",
            cmd=["python3", "scripts/check_merge_queue_readiness.py"],
        ),
        Gate(
            name="merge-ruleset-deployment-guardrails",
            cmd=["python3", "scripts/check_merge_ruleset_deployment_guardrails.py"],
        ),
        Gate(
            name="workflow-script-injection",
            cmd=["python3", "scripts/check_workflow_script_injection.py"],
        ),
        Gate(
            name="dependency-inventory-forge-policy",
            cmd=["python3", "scripts/check_dependency_inventory_forge_policy.py"],
        ),
        Gate(
            name="event-resilience-policy",
            cmd=["python3", "scripts/check_event_resilience_policy.py"],
        ),
        Gate(
            name="async-eval-handoff-policy",
            cmd=["python3", "scripts/check_async_eval_handoff_policy.py"],
        ),
        Gate(
            name="release-supply-chain-policy",
            cmd=["python3", "scripts/check_release_supply_chain_policy.py"],
        ),
        Gate(
            name="cicd-telemetry-policy",
            cmd=["python3", "scripts/check_cicd_telemetry_policy.py"],
        ),
        Gate(
            name="workflow-run-summary-wiring",
            cmd=["python3", "scripts/check_workflow_run_summary_wiring.py"],
        ),
        Gate(
            name="workflow-operator-handoff-policy",
            cmd=["python3", "scripts/check_workflow_operator_handoff_policy.py"],
        ),
        Gate(
            name="workflow-concurrency",
            cmd=["python3", "scripts/check_workflow_concurrency.py"],
        ),
        Gate(
            name="workflow-permissions-policy",
            cmd=["python3", "scripts/check_workflow_permissions_policy.py"],
        ),
        Gate(
            name="attestation-preflight-wiring",
            cmd=["python3", "scripts/check_attestation_preflight_wiring.py"],
        ),
        Gate(
            name="attestation-identity-wiring",
            cmd=["python3", "scripts/check_attestation_identity_wiring.py"],
        ),
        Gate(
            name="attestation-offline-wiring",
            cmd=["python3", "scripts/check_attestation_offline_wiring.py"],
        ),
        Gate(
            name="artifact-digest-wiring",
            cmd=["python3", "scripts/check_artifact_digest_wiring.py"],
        ),
        Gate(
            name="artifact-retention-policy",
            cmd=["python3", "scripts/check_artifact_retention_policy.py"],
        ),
        Gate(
            name="cp4b-sla",
            cmd=["python3", "scripts/check_cp4b_sla.py"],
        ),
        Gate(
            name="committed-run-summaries",
            cmd=["python3", "scripts/check_committed_run_summaries.py"],
        ),
        Gate(
            name="fetch-index",
            cmd=["python3", "scripts/validate_fetch_index.py"],
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
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Print gate execution plan without running commands.",
    )
    args = parser.parse_args()

    workbench_root = Path(__file__).resolve().parents[1]
    gates = _build_gates(args)
    if args.plan:
        print(f"[plan] total={len(gates)}")
        for gate in gates:
            print(f"  - {gate.name}: {' '.join(gate.cmd)}")
        return 0

    failures: list[tuple[str, int]] = []
    for gate in gates:
        ok, code = _run_gate(gate, cwd=workbench_root)
        if not ok:
            failures.append((gate.name, code))

    print(f"[summary] total={len(gates)} failed={len(failures)}")
    if failures:
        _emit_annotation(
            "warning",
            "quality-gate-summary",
            f"{len(failures)} of {len(gates)} gates failed",
        )
        for name, code in failures:
            print(f"  - {name}: exit {code}")
        return 1
    _emit_annotation("notice", "quality-gate-summary", f"all {len(gates)} gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
