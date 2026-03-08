from __future__ import annotations

import subprocess
from pathlib import Path


def test_run_quality_gates_plan_output_contract_and_order():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            "python3",
            "scripts/run_quality_gates.py",
            "--plan",
            "--skip-tests",
            "--skip-evals",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    lines = [line.rstrip() for line in result.stdout.splitlines() if line.strip()]
    assert lines[0].startswith("[plan] total=")

    gate_lines = [line for line in lines[1:] if line.startswith("  - ")]
    gate_names = [line.split(": ", 1)[0].replace("  - ", "") for line in gate_lines]
    assert gate_names == [
        "secret-hygiene",
        "git-size",
        "compileall",
        "workflow-pinning",
        "workflow-pinning-exceptions",
        "chimera-packets",
        "suggestions-bin-report-sync",
        "suggestions-bin-status",
        "operations-nist-mapping",
        "ssdf-quality-gate-mapping",
        "dora-reliability-scoreboard",
        "campaign-wave-policy",
        "openai-async-policy",
        "jetstream-openai-campaign-policy",
        "workflow-codeql-matrix-policy",
        "reusable-workflow-governance-policy",
        "jetstream-consumer-openai-loop-policy",
        "dependency-review-policy",
        "merge-queue-readiness",
        "merge-ruleset-deployment-guardrails",
        "workflow-script-injection",
        "dependency-inventory-forge-policy",
        "event-resilience-policy",
        "async-eval-handoff-policy",
        "release-supply-chain-policy",
        "cicd-telemetry-policy",
        "workflow-run-summary-wiring",
        "workflow-operator-handoff-policy",
        "workflow-concurrency",
        "workflow-permissions-policy",
        "attestation-preflight-wiring",
        "attestation-identity-wiring",
        "attestation-offline-wiring",
        "artifact-digest-wiring",
        "artifact-retention-policy",
        "cp4b-sla",
        "committed-run-summaries",
        "fetch-index",
        "workspace-index",
    ]
