# CP Runbook Commands

Date: 2026-02-17  
Scope: `Workbench/**`

## Canary

- `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals`
- `python3 scripts/check_workflow_run_summary_wiring.py`
- `python3 scripts/check_workflow_operator_handoff_policy.py`
- `python3 scripts/check_workflow_concurrency.py`
- `python3 scripts/check_workflow_permissions_policy.py`
- `python3 scripts/check_attestation_preflight_wiring.py`
- `python3 scripts/check_attestation_identity_wiring.py`
- `python3 scripts/check_attestation_offline_wiring.py`
- `python3 scripts/check_artifact_digest_wiring.py`
- `python3 scripts/check_artifact_retention_policy.py`
- `python3 scripts/check_gh_cli_version.py --min-version 2.50.0`
- `python3 scripts/check_cp4b_sla.py`
- `python3 scripts/check_chimera_packets.py`
- `python3 scripts/generate_suggestions_bin_report.py --check`
- `python3 scripts/check_suggestions_bin_status.py`
- `python3 scripts/check_operations_nist_mapping.py`
- `python3 scripts/check_ssdf_quality_gate_mapping.py`
- `python3 scripts/check_dora_reliability_scoreboard.py`
- `python3 scripts/check_campaign_wave_policy.py`
- `python3 scripts/check_openai_async_policy.py`
- `python3 scripts/check_jetstream_openai_campaign_policy.py`
- `python3 scripts/check_workflow_codeql_matrix_policy.py`
- `python3 scripts/check_reusable_workflow_governance_policy.py`
- `python3 scripts/check_jetstream_consumer_openai_loop_policy.py`
- `python3 scripts/check_dependency_review_policy.py`
- `python3 scripts/check_merge_queue_readiness.py`
- `python3 scripts/check_merge_ruleset_deployment_guardrails.py`
- `python3 scripts/check_workflow_script_injection.py`
- `python3 scripts/check_dependency_inventory_forge_policy.py`
- `python3 scripts/check_event_resilience_policy.py`
- `python3 scripts/check_async_eval_handoff_policy.py`
- `python3 scripts/check_release_supply_chain_policy.py`
- `python3 scripts/check_cicd_telemetry_policy.py`

## Run Summary

- `python3 scripts/generate_run_summary.py --repo owner/repo --workflow "Workbench CI" --run-id 123456789 --run-attempt 1 --job-status failure --failure-taxonomy "$(python3 scripts/select_failure_taxonomy.py --workflow 'Workbench CI' --job 'python-smoke')" --failing-job "python-smoke" --failing-step "see job logs" --next-owner lane-workbench --incident-id CUTOVER-2026-02-17-001`
- `python3 scripts/validate_run_summary.py --path docs/reports/run_summary/run_summary.json`

## Rerun Failed with Debug

- `gh run rerun <run-id> --failed --debug`
- `gh run rerun <run-id> --repo <owner/repo> --failed --debug`
- `gh run watch <run-id> --exit-status`

## Pause Non-Critical Workflows

- `gh workflow disable "Nightly Evals"`
- `gh workflow disable "Policy Review"`
- `gh workflow disable "Scorecards"`
- `gh workflow enable "Nightly Evals"`
- `gh workflow enable "Policy Review"`
- `gh workflow enable "Scorecards"`

## Visualization Graph First-Pass Triage

- `gh run view <run-id> --repo <owner/repo> --web`
- `gh run view <run-id> --repo <owner/repo> --json jobs`
- Capture upstream failed node and blocked dependents before step-log deep-dive.

## Artifact Fetch + Index

- `bash scripts/fetch_workbench_artifacts.sh --run-id 123456789 --repo owner/repo --incident-id CUTOVER-2026-02-17-001 --run-attempt 1 --class eval --class attestations --class policy --dry-run`
- `python3 scripts/validate_fetch_index.py`

## Offline Attestation Verify

- `python3 scripts/verify_attestations.py --repo owner/repo --signer-workflow owner/repo/.github/workflows/nightly-evals.yml --predicate-type https://slsa.dev/provenance/v1 --subject attested_artifacts/eval_report.json --subject attested_artifacts/eval_report.md --bundle attested_artifacts/attestations_bundle.jsonl --json-out docs/reports/attestation_verify_report.json`
- `cat docs/research/ATTESTATION_OFFLINE_VERIFICATION_PLAYBOOK.md`

## Artifact Digest Integrity

- `python3 scripts/generate_artifact_digest_report.py --source nightly-evals --artifact eval_report_json=docs/reports/eval_report.json --artifact eval_report_md=docs/reports/eval_report.md --output docs/reports/artifact_digest_report.json`
- `python3 scripts/verify_artifact_digests.py --report attested_artifacts/artifact_digest_report.json --artifact eval_report_json=attested_artifacts/eval_report.json --artifact eval_report_md=attested_artifacts/eval_report.md --json-out docs/reports/artifact_digest_verify_report.json`

## Artifact Retention Policy

- `python3 scripts/check_artifact_retention_policy.py`
- `cat docs/research/ARTIFACT_RETENTION_CLASSES.md`

## DORA + Reliability Scoreboard

- `python3 scripts/check_dora_reliability_scoreboard.py`
- `cat docs/reports/dora_reliability_scoreboard.md`

## Campaign Wave Policy

- `python3 scripts/check_campaign_wave_policy.py`
- `cat docs/research/CAMPAIGN_WAVE_OPERATIONS_POLICY.md`
- `cat docs/research/templates/ARIADNE_THREAD_AFTER_ACTION_TEMPLATE.md`
- `cat docs/research/templates/BLAMELESS_POSTMORTEM_TEMPLATE.md`
- `cat docs/research/templates/CURSUS_PUBLICUS_RELAY_TEMPLATE.md`

## OpenAI Async Policy

- `python3 scripts/check_openai_async_policy.py`
- `cat docs/research/OPENAI_ASYNC_EXECUTION_POLICY.md`

## JetStream and OpenAI Campaign Guardrails

- `python3 scripts/check_jetstream_openai_campaign_policy.py`
- `python3 scripts/openai_retry_backoff.py --attempts 5 --base-delay 1 --max-delay 30 --jitter-ratio 0.2 --seed 42`
- `cat docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md`

## Workflow CodeQL and Matrix Guardrails

- `python3 scripts/check_workflow_codeql_matrix_policy.py`
- `cat docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md`
- `cat .github/workflow-matrix-review-checklist.md`
- `cat .github/workflows/codeql-actions-security.yml`
- `cat docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md`

## Reusable Workflow Governance

- `python3 scripts/generate_reusable_workflow_inventory.py --output-dir docs/reports`
- `python3 scripts/check_reusable_workflow_governance_policy.py`
- `cat docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md`
- `cat docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md`

## JetStream Consumer and OpenAI Loop Policy

- `python3 scripts/check_jetstream_consumer_openai_loop_policy.py`
- `python3 scripts/evaluate_openai_compaction_threshold.py --current-ratio 0.84 --threshold 0.80`
- `python3 scripts/openai_budget_preflight.py --project-tier production --current-spend 950 --cap 1000 --alarm-threshold 0.9`
- `python3 scripts/evaluate_background_task_slo.py --duration-seconds 450 --timeout-seconds 600 --cancelled false`
- `python3 scripts/evaluate_jetstream_consumer_profile.py --workload critical`
- `cat docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json`
- `cat docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md`
- `cat docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md`
- `cat docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md`
- `cat docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md`

## Dependency Review Supply-Chain Policy

- `python3 scripts/check_dependency_review_policy.py`
- `cat .github/dependency-review-config.yml`
- `cat docs/research/DEPENDENCY_REVIEW_SUPPLY_CHAIN_POLICY.md`

## Merge Queue Readiness

- `python3 scripts/check_merge_queue_readiness.py`
- `cat .github/workflows/required-check-sentinel.yml`

## Merge Ruleset and Deployment Guardrails

- `python3 scripts/check_merge_ruleset_deployment_guardrails.py`
- `python3 scripts/evaluate_promotion_watchtower.py --ci-pass true --provenance-pass true --advisory-health healthy --review-approved true --runtime-health healthy`
- `gh api repos/{owner}/{repo}/rulesets --paginate > docs/reports/ruleset_drift_audit.json`
- `cat docs/reports/ruleset_drift_audit.json`
- `cat docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`
- `cat .github/CODEOWNERS`
- `gh api repos/{owner}/{repo}/environments/staging/protection-rules`
- `gh api repos/{owner}/{repo}/environments/staging/deployment-branch-policies`

## Dependency Inventory and Forge Gates

- `python3 scripts/generate_dependency_inventory.py --output-dir docs/reports`
- `python3 scripts/check_workflow_script_injection.py`
- `python3 scripts/check_dependency_inventory_forge_policy.py`
- `cat docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md`

## Event Resilience and Flow Control

- `python3 scripts/check_event_resilience_policy.py`
- `python3 scripts/compute_littles_law_wip.py --throughput-per-day 6 --lead-time-days 2 --buffer 1.15`
- `cat docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md`

## Async Eval and Campaign Handoff

- `python3 scripts/check_async_eval_handoff_policy.py`
- `cat docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md`
- `cat docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md`

## Release and Supply Chain Policy

- `python3 scripts/check_release_supply_chain_policy.py`
- `cat docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md`
- `gh release verify <tag>`
- `gh release verify-asset <tag> <asset-name>`

## CICD Telemetry and Error Taxonomy

- `python3 scripts/check_cicd_telemetry_policy.py`
- `python3 scripts/select_failure_taxonomy.py --workflow "Workbench CI" --job "policy-review"`
- `cat docs/research/CICD_TELEMETRY_ERROR_TAXONOMY_POLICY.md`

## Rollback Packet Prep

- `python3 scripts/check_committed_run_summaries.py`
- `python3 scripts/clean_cutover_artifacts.py --retention-class short --dry-run`
- `cat docs/research/CHIMERA_V2_CP4A_OPERATOR_READINESS_STATUS_2026-02-15.md`

## Suggestions Bin Governance

- `python3 scripts/generate_suggestions_bin_report.py`
- `python3 scripts/generate_suggestions_bin_report.py --check`
- `python3 scripts/check_suggestions_bin_status.py`
- `cat docs/SUGGESTIONS_BIN.md`
- `cat docs/reports/suggestions_bin.json`
