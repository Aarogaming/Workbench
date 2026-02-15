# Operations

## Incident response

When a gate, eval, or plugin contract check fails:

1. Capture context:
   - `git status --short --branch`
   - `python3 scripts/run_quality_gates.py`
2. Triage impact:
   - Check `docs/reports/workspace_index_audit.md`
   - Check `docs/reports/eval_report.md`
   - Check `docs/reports/plugin_contract_audit.json`
3. Contain risk:
   - Revert or gate rollout for failing plugin/module.
   - Prefer disabling affected command routing over partial behavior.
4. Verify fix:
   - `pytest -q`
   - `python3 scripts/eval_report.py --baseline evals/baselines/main.json`
   - `python3 scripts/check_plugin_contracts.py`
5. Document outcome:
   - Append remediation notes in `docs/reports/workbench_gap_assessment_2026-02-15.md` or successor report.

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
