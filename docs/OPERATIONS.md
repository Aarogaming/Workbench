# Operations

## Incident response (NIST SP 800-61 Rev. 3 lifecycle mapping)

When a gate, eval, or plugin contract check fails, run the incident flow in this order:

1. Prepare:
   - Confirm current branch/state: `git status --short --branch`
   - Snapshot baseline gate posture: `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals`
   - Confirm operator packet availability: `python3 scripts/check_chimera_packets.py`
2. Detect and Analyze:
   - Run active checks to confirm failing surface: `python3 scripts/run_quality_gates.py`
   - Review impact artifacts:
     - `docs/reports/workspace_index_audit.md`
     - `docs/reports/eval_report.md`
     - `docs/reports/plugin_contract_audit.json`
   - Classify failing lane/owner with taxonomy helper:
     - `python3 scripts/select_failure_taxonomy.py --workflow "Workbench CI" --job "python-smoke"`
3. Contain, Eradicate, and Recover:
   - Contain:
     - Revert or gate rollout for failing plugin/module.
     - Prefer disabling affected command routing over partial behavior.
   - Eradicate + recover:
     - `pytest -q`
     - `python3 scripts/eval_report.py --baseline evals/baselines/main.json`
     - `python3 scripts/check_plugin_contracts.py`
     - `python3 scripts/check_committed_run_summaries.py`
4. Post-Incident Activity:
   - Produce handoff packet summary:
     - `python3 scripts/generate_run_summary.py --repo owner/repo --workflow "Workbench CI" --run-id 123456789 --run-attempt 1 --job-status failure --failure-taxonomy "$(python3 scripts/select_failure_taxonomy.py --workflow 'Workbench CI' --job 'python-smoke')" --failing-job python-smoke --failing-step "see job logs" --next-owner lane-workbench --incident-id CUTOVER-2026-02-15-001`
     - `python3 scripts/validate_run_summary.py --path docs/reports/run_summary/run_summary.json`
   - Capture remediation notes in `docs/reports/workbench_gap_assessment_2026-02-15.md` or successor report.

## CP4-A canary + rollback

1. Operator canary commands:
   - `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals`
   - `bash -n scripts/fetch_workbench_artifacts.sh`
   - `bash scripts/fetch_workbench_artifacts.sh --run-id 123456789 --repo owner/repo --incident-id CUTOVER-2026-02-15-001 --run-attempt 1 --class eval --class attestations --class policy --dry-run`
   - `python3 scripts/check_workflow_run_summary_wiring.py`
   - `python3 scripts/check_cp4b_sla.py`
   - `python3 scripts/validate_fetch_index.py`
   - `python3 scripts/check_committed_run_summaries.py`
   - `python3 scripts/check_chimera_packets.py`
2. Generate and validate run summary for handoff:
   - `python3 scripts/generate_run_summary.py --repo owner/repo --workflow "Workbench CI" --run-id 123456789 --run-attempt 1 --job-status failure --failure-taxonomy "$(python3 scripts/select_failure_taxonomy.py --workflow 'Workbench CI' --job 'python-smoke')" --failing-job python-smoke --failing-step "see job logs" --next-owner lane-workbench --incident-id CUTOVER-2026-02-15-001`
   - `python3 scripts/validate_run_summary.py --path docs/reports/run_summary/run_summary.json`
3. Use rollback communication template:
   - `docs/research/CHIMERA_V2_CP4A_OPERATOR_READINESS_STATUS_2026-02-15.md`
4. Optional cutover cleanup after handoff window:
   - `python3 scripts/clean_cutover_artifacts.py --retention-class short --dry-run`

## MCP auth operations

1. Local smoke:
   - `python3 scripts/mcp_smoke.py`
2. Strict verification:
   - `python3 scripts/mcp_smoke.py --require-configured`
3. Allow connectivity-only during planned verification maintenance:
   - `python3 scripts/mcp_smoke.py --allow-unverified --require-configured`

## Scheduled eval operations

1. On-demand:
   - `python3 scripts/eval_report.py --baseline evals/baselines/main.json`
2. Refresh baseline intentionally:
   - `python3 scripts/eval_report.py --update-baseline`
3. Review outputs:
   - `docs/reports/eval_report.json`
   - `docs/reports/eval_report.md`

## Workflow supply-chain operations

1. Manual policy checks:
   - `python3 scripts/check_workflow_pinning.py`
   - `python3 scripts/check_workflow_pinning_exceptions.py`
2. Exception policy source:
   - `/.github/workflow-pinning-exceptions.json`
3. Scheduled workflows:
   - `/.github/workflows/scorecards.yml`
   - `/.github/workflows/policy-review.yml`
4. Scorecard threshold policy:
   - `/.github/scorecard-policy.json`
   - `python3 scripts/check_scorecard_threshold.py --repo owner/name --allow-unavailable`
   - `python3 scripts/update_scorecard_history.py`
5. Attestation verification:
   - `/.github/workflows/verify-nightly-attestations.yml`
   - `python3 scripts/verify_attestations.py --repo owner/name --subject path/to/artifact`
