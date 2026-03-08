# Workflow Operator Handoff and Recovery Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## Run Summary Contract Step via GITHUB_STEP_SUMMARY (WB-SUG-127)

Policy:

1. Failure/cancelled paths must generate `run_summary.json` and `run_summary.md` artifacts.
2. The run-summary generation step must also publish a `cp2.run_summary.v1` contract excerpt to `GITHUB_STEP_SUMMARY`.
3. Step-summary content includes terminal class, failure taxonomy, rerun command, and artifact-fetch command anchors.

Reference artifact:

- `scripts/generate_run_summary.py`

## Standardized Annotation Emission for Gate Scripts (WB-SUG-128)

Policy:

1. Gate execution emits GitHub workflow command annotations using normalized severities.
2. `::notice` is used for gate start/pass context, `::warning` for degraded summary posture, and `::error` for gate failure events.
3. Annotation messages include gate identity and operator next-action context.

Reference artifact:

- `scripts/run_quality_gates.py`

## Rerun Failed with Debug Operator Snippet (WB-SUG-129)

Policy:

1. Runbook and handoff packets include a copy/paste debug rerun command template.
2. Canonical snippet: `gh run rerun <run-id> --failed --debug`.
3. Generated run-summary artifacts keep this snippet in `rerun_debug_cmd`.

Reference artifacts:

- `docs/research/CP_RUNBOOK_COMMANDS.md`
- `scripts/generate_run_summary.py`

## Pause Switch Policy for Non-Critical Workflows (WB-SUG-130)

Policy:

1. Incident windows may temporarily pause non-critical workflows to reduce background noise.
2. Pause/resume operations use GitHub CLI workflow disable/enable commands and must be logged in handoff notes.
3. Pause scope includes at minimum `Nightly Evals`, `Policy Review`, and `Scorecards`.

Canonical command anchors:

- `gh workflow disable "<workflow-name>"`
- `gh workflow enable "<workflow-name>"`

Reference artifact:

- `docs/research/CP_RUNBOOK_COMMANDS.md`

## Workflow Health Board Badge Contract (WB-SUG-131)

Policy:

1. Operator docs maintain a workflow health board with badge links for `ci`, `size-check`, `nightly`, and `policy`.
2. Badge links resolve to workflow YAML file names for deterministic status references.
3. Health board is reviewed at each cutover readiness checkpoint.

Reference artifact:

- `docs/research/WORKFLOW_HEALTH_BOARD.md`

## Cancellation-Safe Cleanup for Non-Critical Workflows (WB-SUG-132)

Policy:

1. Non-critical workflows include an explicit cancellation cleanup step using `if: ${{ cancelled() }}`.
2. Cleanup step runs `clean_cutover_artifacts.py` in dry-run mode to produce deterministic hygiene evidence.
3. Cleanup execution outcomes are retained in workflow logs for incident handoff review.

## Visualization Graph Triage Checkpoint (WB-SUG-133)

Policy:

1. Incident triage starts with the workflow visualization graph before deep per-step log inspection.
2. Graph review records the first upstream failed node and dependent blocked nodes in handoff notes.
3. Log deep-dive starts only after graph checkpoint context is captured.

Reference artifact:

- `docs/research/CP_RUNBOOK_COMMANDS.md`

## Required Local Artifacts

- `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md`
- `scripts/check_workflow_operator_handoff_policy.py`
- `scripts/check_workflow_run_summary_wiring.py`
- `scripts/generate_run_summary.py`
- `scripts/run_quality_gates.py`
- `docs/research/CP_RUNBOOK_COMMANDS.md`
- `docs/research/WORKFLOW_HEALTH_BOARD.md`
- `.github/workflows/nightly-evals.yml`
- `.github/workflows/reusable-policy-review.yml`
- `.github/workflows/reusable-scorecards.yml`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_workflow_operator_handoff_policy.py` | `[ok] workflow operator handoff/recovery policy check` |
| `python3 scripts/check_workflow_run_summary_wiring.py` | `[summary] workflows=8 failed=0` |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `workflow-operator-handoff-policy` gate |
| `GITHUB_STEP_SUMMARY=/tmp/workbench_step_summary.md python3 scripts/generate_run_summary.py --output-dir /tmp/workbench_run_summary --repo owner/repo --workflow "Workbench CI" --run-id 123456789 --run-attempt 1 --head-sha abcdef --job-status failure --failure-taxonomy script --failing-job python-smoke --failing-step "see job logs" --next-owner lane-workbench` | Writes run summary files and appends contract block to step-summary path |
| `rg -n "gh run rerun <run-id> --failed --debug" docs/research/CP_RUNBOOK_COMMANDS.md` | Finds canonical debug rerun snippet |
| `cat docs/research/WORKFLOW_HEALTH_BOARD.md` | Shows badge links for `ci`, `size-check`, `nightly`, and `policy` workflows |
| `rg -n "if: \\$\\{\\{ cancelled\\(\\) \\}\\}|clean_cutover_artifacts.py" .github/workflows/nightly-evals.yml .github/workflows/reusable-policy-review.yml .github/workflows/reusable-scorecards.yml` | Finds cancellation-safe cleanup steps in non-critical workflows |
| `rg -n "Visualization Graph First-Pass Triage|gh run view <run-id> --repo <owner/repo> --web" docs/research/CP_RUNBOOK_COMMANDS.md` | Finds visualization-graph triage checkpoint and command |
