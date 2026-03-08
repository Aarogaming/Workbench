# Dependency Inventory and Forge Gates Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## Build-Time Dependency Snapshot Submission (WB-SUG-068)

Policy:

1. Every primary CI pipeline run produces a build-time dependency snapshot artifact.
2. Snapshot data is prepared in a dependency-graph-submission-compatible format.
3. dependency graph submission to GitHub remains an admin-managed integration boundary.

Local implementation artifact:

- `scripts/generate_dependency_inventory.py`

## SBOM Artifact and Snapshot Submission (WB-SUG-069)

Policy:

1. The dependency snapshot process emits an SPDX JSON SBOM artifact.
2. Policy packet references CycloneDX/SPDX parity goals; local baseline is SPDX output.
3. Policy review workflows retain SBOM artifacts for supply-chain triage.

Local implementation artifacts:

- `docs/reports/dependency_snapshot.json`
- `docs/reports/dependency_sbom.spdx.json`

## Reusable Forge Gates Workflow Contract (WB-SUG-070)

Policy:

1. A reusable workflow (`.github/workflows/reusable-forge-gates.yml`) defines shared forge checks.
2. Primary pipelines call the reusable forge gates workflow to reduce drift.
3. Forge gates include dependency inventory generation and workflow script-injection lint checks.

## Runner Scale-Set Readiness Plan (WB-SUG-071)

Policy:

1. Keep a documented readiness plan for runner scale-sets for peak 8+ lane periods.
2. Treat scale-set rollout as design-stage until explicit runner ownership approval exists.
3. Review readiness plan at wave retro when queue latency trends regress.

## Ephemeral Self-Hosted Runner Baseline (WB-SUG-072)

Policy:

1. If self-hosted runners are adopted, baseline is ephemeral job runners.
2. Long-lived shared runner state is prohibited for control-plane workflows.
3. Exceptions require explicit owner, expiry, and risk acceptance evidence.

## Workflow Script-Injection Lint Policy (WB-SUG-073)

Policy:

1. Workflow files are linted for untrusted context interpolation in shell `run` sinks.
2. Untrusted context patterns in `run:` lines or run blocks are treated as policy failures.
3. Script-injection lint is part of forge gates and local quality gates.

Local implementation artifact:

- `scripts/check_workflow_script_injection.py`

## Required Local Artifacts

- `docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md`
- `.github/workflows/reusable-forge-gates.yml`
- `scripts/generate_dependency_inventory.py`
- `scripts/check_workflow_script_injection.py`
- `scripts/check_dependency_inventory_forge_policy.py`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/generate_dependency_inventory.py --output-dir docs/reports` | Writes dependency snapshot + SPDX SBOM files |
| `python3 scripts/check_workflow_script_injection.py` | `[ok] workflow script-injection check` |
| `python3 scripts/check_dependency_inventory_forge_policy.py` | `[ok] dependency inventory/forge policy check` |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes dependency/forge and script-injection gates |
