# Workbench Supply-Chain Hardening Plan (2026-02-15)

## Research inputs

Primary-source guidance used:

1. GitHub Actions security hardening:
   - https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
2. Dependabot updates for GitHub Actions:
   - https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file
3. Dependency review action:
   - https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/configuring-dependency-review
4. OpenSSF Scorecards:
   - https://github.com/ossf/scorecard
5. SLSA framework:
   - https://slsa.dev/

## Multi-phase plan

### Phase 1: Immutable workflow dependencies

1. Pin all third-party `uses:` actions in workflow files to full commit SHAs.
2. Keep human-readable version comments for maintainability.

Status: completed.

### Phase 2: Policy enforcement in repo gates

1. Add `scripts/check_workflow_pinning.py` to enforce SHA pinning policy.
2. Run the pinning audit in CI and quality-gate orchestration.
3. Add unit tests for workflow-pinning policy checks.

Status: completed.

### Phase 3: Automated update + review controls

1. Add `dependency-review` workflow for pull requests.
2. Add Dependabot config for GitHub Actions version/update visibility.
3. Include workflow-pinning audit in eval/baseline gate.

Status: completed.

### Phase 4: Continuous assurance and provenance

1. Add Scorecards workflow as a scheduled security signal.
2. Add SLSA-aligned artifact provenance attestations in nightly evals.
3. Add workflow pinning exception policy file + review automation.

Status: completed.

### Phase 5: Scorecard threshold policy

1. Add repo-local Scorecard threshold policy file.
2. Add automated threshold check script against Scorecard API payloads.
3. Run threshold checks in scorecards and policy-review workflows and retain reports.

Status: completed.

### Phase 6: Reusable workflows + downstream attestation verification

1. Refactor policy/scorecards workflows into reusable templates.
2. Add downstream workflow to verify nightly artifact attestations.
3. Add local verification script and tests for attestation verification flow.

Status: completed.

### Phase 7: Scorecard trend tracking

1. Add scorecard history rollup script for longitudinal trend tracking.
2. Persist history JSON/markdown artifacts from scorecard and policy-review workflows.
3. Add tests for history update semantics (append, dedupe, markdown render).

Status: completed.

## Delivered artifacts

1. `.github/workflows/ci.yml` (pinned actions + policy check step)
2. `.github/workflows/size-check.yml` (pinned actions + policy check step)
3. `.github/workflows/nightly-evals.yml` (pinned actions)
4. `.github/workflows/dependency-review.yml`
5. `.github/dependabot.yml`
6. `scripts/check_workflow_pinning.py`
7. `tests/test_check_workflow_pinning.py`
8. `scripts/run_quality_gates.py` (workflow-pinning + exception-review gates added)
9. `scripts/eval_report.py` + `evals/*` (workflow-pinning and exception-review scenarios enforced)
10. `.github/workflows/scorecards.yml`
11. `.github/workflows/policy-review.yml`
12. `scripts/check_workflow_pinning_exceptions.py`
13. `.github/workflow-pinning-exceptions.json`
14. `scripts/check_scorecard_threshold.py`
15. `.github/scorecard-policy.json`
16. `.github/workflows/reusable-scorecards.yml`
17. `.github/workflows/reusable-policy-review.yml`
18. `.github/workflows/verify-nightly-attestations.yml`
19. `scripts/verify_attestations.py`
20. `tests/test_verify_attestations.py`
21. `scripts/update_scorecard_history.py`
22. `tests/test_update_scorecard_history.py`
23. `docs/reports/scorecard_history.json`
24. `docs/reports/scorecard_history.md`

## Validation summary

1. `pytest -q` -> `55 passed`
2. `python3 scripts/check_workflow_pinning.py` -> `0 issues`
3. `python3 scripts/check_workflow_pinning_exceptions.py` -> `0 issues`
4. `python3 scripts/check_scorecard_threshold.py --project github.com/ossf/scorecard --allow-unavailable` -> policy pass
5. `python3 scripts/eval_report.py --baseline evals/baselines/main.json` -> `pass_rate 1.000 (7/7)`
6. `python3 scripts/run_quality_gates.py` -> all gates passed
7. `pytest -q tests/test_verify_attestations.py` -> pass
8. `pytest -q tests/test_update_scorecard_history.py` -> pass

## Next hardening candidates

1. Promote reusable workflow templates to a central shared-workflow repository for sibling repos.
2. Extend downstream verification to release artifacts and container attestations.
3. Add policy-driven alerting on trend deltas (e.g., fail if score drops more than configured delta).
