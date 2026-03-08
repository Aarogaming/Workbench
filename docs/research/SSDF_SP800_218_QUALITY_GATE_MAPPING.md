# SSDF SP 800-218 Quality Gate Mapping

Date: 2026-02-17  
Scope: `Workbench/**`

## Purpose

Provide explicit SSDF control traceability for Workbench quality gates and their workflow enforcement points.

## Script Gate Mapping

| Gate | Command | SSDF Practices | Coverage intent |
| --- | --- | --- | --- |
| `secret-hygiene` | `python3 scripts/check_secret_hygiene.py --all --strict` | `PW.6.2`, `RV.1.2` | Detect and block committed credential material. |
| `git-size` | `python3 scripts/check_git_size.py` | `PO.3.1`, `PW.1.1` | Limit oversized artifacts that complicate safe change control. |
| `compileall` | `python3 -m compileall -q Assets plugins Tools` | `PW.7.1` | Verify baseline buildability/syntax health before promotion. |
| `workflow-pinning` | `python3 scripts/check_workflow_pinning.py` | `PO.3.1`, `PW.4.1` | Enforce immutable action dependency references. |
| `workflow-pinning-exceptions` | `python3 scripts/check_workflow_pinning_exceptions.py` | `PO.4.1`, `RV.1.1` | Track and age-review risk exceptions for action pinning. |
| `chimera-packets` | `python3 scripts/check_chimera_packets.py` | `PO.2.1`, `RV.1.1` | Ensure required operator packet contracts exist. |
| `suggestions-bin-report-sync` | `python3 scripts/generate_suggestions_bin_report.py --check` | `PO.4.1`, `RV.1.1` | Enforce synchronized `suggestions_bin.json` report generation contract from markdown source. |
| `suggestions-bin-status` | `python3 scripts/check_suggestions_bin_status.py` | `PO.4.1`, `RV.1.1` | Enforce suggestion-item status coverage, `WB-SUG` cap (`<=100`), report-sync status parity, status vocabulary, and implemented-evidence references. |
| `operations-nist-mapping` | `python3 scripts/check_operations_nist_mapping.py` | `PO.1.1`, `PO.4.1` | Align incident execution playbook with NIST lifecycle flow. |
| `ssdf-quality-gate-mapping` | `python3 scripts/check_ssdf_quality_gate_mapping.py` | `PO.4.1`, `RV.1.1` | Enforce SSDF traceability coverage for the gate catalog itself. |
| `dora-reliability-scoreboard` | `python3 scripts/check_dora_reliability_scoreboard.py` | `PO.4.1`, `RV.1.1` | Enforce weekly DORA/reliability metric artifact contract for campaign waves. |
| `campaign-wave-policy` | `python3 scripts/check_campaign_wave_policy.py` | `PO.4.1`, `RV.1.1` | Enforce campaign wave WIP/checklist/relay/postmortem policy and template contracts. |
| `openai-async-policy` | `python3 scripts/check_openai_async_policy.py` | `PO.4.1`, `PW.1.1` | Enforce background-mode/webhook/prompt-cache/flex policy coverage for long tasks. |
| `jetstream-openai-campaign-policy` | `python3 scripts/check_jetstream_openai_campaign_policy.py` | `PO.4.1`, `PW.1.1` | Enforce JetStream lease/dedupe delivery controls and OpenAI callback/state/retry/budget guardrails for campaign loops. |
| `workflow-codeql-matrix-policy` | `python3 scripts/check_workflow_codeql_matrix_policy.py` | `PO.3.1`, `RV.1.1` | Enforce CodeQL Actions scan contract, workflow_run trust-boundary rule, and matrix strategy defaults (`max-parallel`, `fail-fast`, `continue-on-error`). |
| `reusable-workflow-governance-policy` | `python3 scripts/check_reusable_workflow_governance_policy.py` | `PO.4.1`, `RV.1.1` | Enforce reusable-workflow depth cap, monthly consumer inventory/reporting, private-sharing warning checklist, and self-hosted selector governance contract. |
| `jetstream-consumer-openai-loop-policy` | `python3 scripts/check_jetstream_consumer_openai_loop_policy.py` | `PO.4.1`, `PW.1.1` | Enforce JetStream pull/AckSync/poison-message consumer defaults and OpenAI background/compaction/chaining/budget preflight loop controls. |
| `dependency-review-policy` | `python3 scripts/check_dependency_review_policy.py` | `PO.3.1`, `RV.1.1` | Enforce dependency-review config thresholds (`fail-on-severity`, `fail-on-scopes`, deny groups) and workflow wiring contract. |
| `merge-queue-readiness` | `python3 scripts/check_merge_queue_readiness.py` | `PO.3.1`, `RV.1.1` | Enforce merge-group trigger parity and always-run sentinel required-check workflow. |
| `merge-ruleset-deployment-guardrails` | `python3 scripts/check_merge_ruleset_deployment_guardrails.py` | `PO.3.1`, `RV.1.1` | Enforce strict required-check/ruleset/deployment guardrail policy and CODEOWNERS control-plane ownership contract. |
| `workflow-script-injection` | `python3 scripts/check_workflow_script_injection.py` | `PW.5.1`, `RV.1.2` | Detect risky untrusted-context interpolation into workflow shell run sinks. |
| `dependency-inventory-forge-policy` | `python3 scripts/check_dependency_inventory_forge_policy.py` | `PO.3.1`, `PW.4.1` | Enforce dependency snapshot/SBOM/forge-gates reusable workflow policy and wiring contract. |
| `event-resilience-policy` | `python3 scripts/check_event_resilience_policy.py` | `PO.4.1`, `PW.1.1` | Enforce transactional outbox/idempotency/circuit-breaker/Little's Law flow policy and artifact contracts. |
| `async-eval-handoff-policy` | `python3 scripts/check_async_eval_handoff_policy.py` | `PO.4.1`, `RV.1.1` | Enforce async batch-routing policy plus AI-RMF/Daedalus/Hermes campaign handoff artifact contracts. |
| `release-supply-chain-policy` | `python3 scripts/check_release_supply_chain_policy.py` | `PO.3.1`, `RV.1.1` | Enforce attestation lifecycle/release-integrity/Dependabot/org-actions supply-chain policy contracts. |
| `cicd-telemetry-policy` | `python3 scripts/check_cicd_telemetry_policy.py` | `PO.4.1`, `RV.1.1` | Enforce OpenTelemetry CICD semantic field and controlled `error.type` taxonomy policy contracts. |
| `workflow-run-summary-wiring` | `python3 scripts/check_workflow_run_summary_wiring.py` | `PW.8.1`, `RV.1.2` | Enforce incident evidence generation on failure/cancel paths. |
| `workflow-operator-handoff-policy` | `python3 scripts/check_workflow_operator_handoff_policy.py` | `PW.8.1`, `RV.1.2` | Enforce step-summary contract publication, gate annotation standards, and debug rerun command coverage. |
| `workflow-concurrency` | `python3 scripts/check_workflow_concurrency.py` | `PO.3.1`, `PW.1.1` | Prevent stale/overlapping runs in high-concurrency waves. |
| `workflow-permissions-policy` | `python3 scripts/check_workflow_permissions_policy.py` | `PW.6.1`, `RV.1.2` | Enforce least-privilege token scopes for workflows/jobs. |
| `attestation-preflight-wiring` | `python3 scripts/check_attestation_preflight_wiring.py` | `PW.4.1`, `RV.1.1` | Ensure attest verification preflight checks are present. |
| `attestation-identity-wiring` | `python3 scripts/check_attestation_identity_wiring.py` | `PW.4.1`, `RV.1.2` | Enforce signer/predicate identity checks for provenance. |
| `attestation-offline-wiring` | `python3 scripts/check_attestation_offline_wiring.py` | `PW.4.1`, `PO.4.1` | Preserve offline verification path for constrained environments. |
| `artifact-digest-wiring` | `python3 scripts/check_artifact_digest_wiring.py` | `PW.4.1`, `RV.1.2` | Enforce digest capture and integrity-verification wiring. |
| `artifact-retention-policy` | `python3 scripts/check_artifact_retention_policy.py` | `PO.3.1`, `RV.1.1` | Keep forensic retention windows explicit and bounded. |
| `cp4b-sla` | `python3 scripts/check_cp4b_sla.py` | `PO.4.1`, `RV.1.1` | Enforce closure deadlines and escalation posture. |
| `committed-run-summaries` | `python3 scripts/check_committed_run_summaries.py` | `RV.1.2`, `PW.8.1` | Validate run-summary artifact contract integrity. |
| `fetch-index` | `python3 scripts/validate_fetch_index.py` | `PW.8.1`, `RV.1.2` | Validate incident artifact index schema and handoff fidelity. |
| `pytest` | `pytest -q` | `PW.7.2`, `RV.1.1` | Execute regression tests for behavior verification. |
| `workspace-index` | `python3 scripts/validate_workspace_index.py --suite-root .. --strict-enforced-only --ignore-submodule-dirty --ignore-submodule-ahead` | `PO.3.1`, `PW.1.1` | Maintain repository structure and enforced index integrity. |
| `eval-report` | `python3 scripts/eval_report.py --baseline evals/baselines/main.json` | `RV.1.1`, `RV.3.2` | Detect quality drift against defined evaluation baseline. |

## Workflow Enforcement Mapping

| Workflow | Enforced checks | SSDF Practices | Evidence path |
| --- | --- | --- | --- |
| `.github/workflows/ci.yml` | `scripts/run_quality_gates.py` plus direct policy checks (`check_chimera_packets.py`, `check_suggestions_bin_status.py`, `check_operations_nist_mapping.py`, `check_ssdf_quality_gate_mapping.py`, `check_dora_reliability_scoreboard.py`, `check_campaign_wave_policy.py`, `check_openai_async_policy.py`, `check_jetstream_openai_campaign_policy.py`, `check_workflow_codeql_matrix_policy.py`, `check_reusable_workflow_governance_policy.py`, `check_jetstream_consumer_openai_loop_policy.py`, `check_dependency_review_policy.py`, `check_merge_queue_readiness.py`, `check_merge_ruleset_deployment_guardrails.py`, `check_event_resilience_policy.py`, `check_async_eval_handoff_policy.py`, `check_release_supply_chain_policy.py`, `check_cicd_telemetry_policy.py`, `check_workflow_operator_handoff_policy.py`, `check_workflow_permissions_policy.py`) and reusable forge-gates call | `PO.3.1`, `PW.6.1`, `RV.1.2` | `.github/workflows/ci.yml` |
| `.github/workflows/size-check.yml` | Direct policy checks (`check_chimera_packets.py`, `check_suggestions_bin_status.py`, `check_operations_nist_mapping.py`, `check_ssdf_quality_gate_mapping.py`, `check_dora_reliability_scoreboard.py`, `check_campaign_wave_policy.py`, `check_openai_async_policy.py`, `check_jetstream_openai_campaign_policy.py`, `check_workflow_codeql_matrix_policy.py`, `check_reusable_workflow_governance_policy.py`, `check_jetstream_consumer_openai_loop_policy.py`, `check_dependency_review_policy.py`, `check_merge_queue_readiness.py`, `check_merge_ruleset_deployment_guardrails.py`, `check_event_resilience_policy.py`, `check_async_eval_handoff_policy.py`, `check_release_supply_chain_policy.py`, `check_cicd_telemetry_policy.py`, `check_workflow_operator_handoff_policy.py`, `check_workflow_permissions_policy.py`) plus reusable forge-gates call | `PO.3.1`, `PW.6.1`, `RV.1.1` | `.github/workflows/size-check.yml` |
| `.github/workflows/codeql-actions-security.yml` | CodeQL Actions scan with explicit matrix strategy controls and failure-path run-summary artifact wiring | `PW.4.1`, `RV.1.1`, `RV.1.2` | `.github/workflows/codeql-actions-security.yml` |
| `.github/workflows/reusable-forge-gates.yml` | Shared forge checks (`check_workflow_script_injection.py`, `generate_dependency_inventory.py`, `check_dependency_inventory_forge_policy.py`) for primary pipelines | `PO.3.1`, `PW.4.1`, `RV.1.2` | `.github/workflows/reusable-forge-gates.yml` |
