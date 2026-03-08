# Artifact Retention Classes

Date: 2026-02-17  
Scope: `Workbench/**`

## Default Classes

- `short`: `7` days
- `standard`: `30` days
- `forensic`: `90` days

## Current Mapping

- `run-summary-*` -> `short` (`7`)
- `nightly-eval-report` -> `standard` (`30`)
- `workflow-policy-reports` -> `standard` (`30`)
- `scorecard-results` -> `standard` (`30`)
- `attestation-verify-report` -> `forensic` (`90`)

## Enforcement

- Workflow policy checker:
  - `python3 scripts/check_artifact_retention_policy.py`
- CI gates:
  - `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals`
  - `python3 scripts/run_quality_gates.py --skip-tests --skip-evals`
