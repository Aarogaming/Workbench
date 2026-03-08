# CICD Telemetry and Error Taxonomy Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## OpenTelemetry CICD Semantic Conventions (WB-SUG-088)

Policy:

1. CICD telemetry records include semantic fields for pipeline, workflow, and run identity.
2. Operator artifacts include stable run identifiers (`cicd.run.id`) for cross-system correlation.
3. Telemetry naming aligns with OpenTelemetry CICD semantic conventions.

## CICD Error Taxonomy Contract (WB-SUG-089)

Policy:

1. Failures are tagged with a standardized `error.type`.
2. `error.type` values map to controlled vocabulary used by run-summary generation (`infra`, `script`, `policy`, `artifact`, `human_gate`, `supply_chain`).
3. Every terminal packet includes run identifier + taxonomy for deterministic triage routing.

Reference artifact:

- `docs/research/templates/CICD_ERROR_TYPE_TAXONOMY_TEMPLATE.md`

## Required Local Artifacts

- `docs/research/CICD_TELEMETRY_ERROR_TAXONOMY_POLICY.md`
- `docs/research/templates/CICD_ERROR_TYPE_TAXONOMY_TEMPLATE.md`
- `scripts/select_failure_taxonomy.py`
- `scripts/check_cicd_telemetry_policy.py`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_cicd_telemetry_policy.py` | `[ok] cicd telemetry/error taxonomy policy check` |
| `python3 scripts/select_failure_taxonomy.py --workflow "Workbench CI" --job "policy-review"` | Returns controlled taxonomy value |
