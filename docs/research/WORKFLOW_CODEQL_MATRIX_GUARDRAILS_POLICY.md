# Workflow CodeQL and Matrix Guardrails Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## CodeQL Actions Advanced Setup (WB-SUG-096)

Policy:

1. Workbench maintains a dedicated CodeQL workflow for GitHub Actions security analysis.
2. The CodeQL workflow scans `actions` language using advanced setup semantics.
3. CodeQL workflow runs on `push`, `pull_request`, and scheduled cadence for drift coverage.

Reference artifact:

- `.github/workflows/codeql-actions-security.yml`

## High-Signal Actions Query Gate (WB-SUG-097)

Policy:

1. High-signal Actions classes are treated as merge blockers until triaged:
   - `actions/untrusted-checkout/high`
   - `actions/artifact-poisoning/*`
   - `actions/missing-workflow-permissions/*`
2. Query gate outcomes must be visible in operator run packets before promotion.
3. Query coverage policy is enforced by local guardrail checks.

## workflow_run Artifact Trust Boundary Rule (WB-SUG-098)

Policy:

1. Any `workflow_run` consumer treats downloaded artifacts/workspace as untrusted by default.
2. Artifact material becomes trusted only after provenance and digest verification passes.
3. Trust-boundary declaration must be explicit in workflow steps and operator docs.

Reference artifact:

- `.github/workflows/verify-nightly-attestations.yml`

## Matrix max-parallel Defaults and Review Checklist (WB-SUG-099)

Policy defaults:

1. `ci` class default `max-parallel = 4`
2. `nightly` class default `max-parallel = 2`
3. `policy` class default `max-parallel = 1`

Review checklist reference:

- `.github/workflow-matrix-review-checklist.md`

## Explicit Matrix fail-fast and continue-on-error (WB-SUG-100)

Policy:

1. Every matrix job declares `fail-fast` explicitly.
2. Every matrix job declares `continue-on-error` explicitly.
3. Absent explicit declarations are treated as policy violations.

## Dedicated CodeQL Merge-Blocker Contract (WB-SUG-117)

Policy:

1. `CodeQL Actions Security` workflow is treated as merge-blocking for control-plane changes.
2. Critical/high Actions findings are triaged before promotion decisions.
3. Merge policy evidence includes latest CodeQL run URL and result summary.

## workflow_run Trust-Boundary Checklist Contract (WB-SUG-118)

Policy:

1. Any `workflow_run` consumer packet includes a trust-boundary checklist item.
2. Checklist confirms untrusted-by-default handling until provenance + digest verification passes.
3. Checklist completion is required before artifact-derived execution.

Reference artifact:

- `docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md`

## Required Local Artifacts

- `docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md`
- `scripts/check_workflow_codeql_matrix_policy.py`
- `.github/workflows/codeql-actions-security.yml`
- `.github/workflow-matrix-review-checklist.md`
- `docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md`
- `docs/research/CP_RUNBOOK_COMMANDS.md`
- `docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_workflow_codeql_matrix_policy.py` | `[ok] workflow codeql/matrix guardrails policy check` |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `workflow-codeql-matrix-policy` gate |
| `cat .github/workflows/codeql-actions-security.yml` | Includes `actions` matrix language plus explicit `max-parallel`, `fail-fast`, and `continue-on-error` |
| `cat docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md` | Contains checklist item for `workflow_run` artifact trust boundaries |
