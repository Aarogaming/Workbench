# Merge, Ruleset, and Deployment Guardrails

Date: 2026-02-17  
Scope: `Workbench/**`

## Strict Required Status Checks (WB-SUG-057)

Policy:

1. Protected branch `main` uses strict required status checks (must be up to date with base before merge).
2. Baseline required checks are:
   - `Workbench CI / python-smoke`
   - `Check File Sizes / size-check`
   - `Required Check Sentinel / sentinel`
   - `CodeQL Actions Security / analyze`

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/rulesets --paginate`

## Staging Deployment Requirement (WB-SUG-058)

Policy:

1. Promotion rules require successful deployment to environment `staging` before merge to protected branches.
2. Deployment evidence is attached to the promotion wave packet before cutover approval.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/environments/staging`

## Environment Reviewer and Self-Review Guard (WB-SUG-059)

Policy:

1. Promotion environments require named reviewers.
2. Environments must enable prevent self-review for deployment approvals.
3. Required reviewer identities are reviewed every wave kickoff.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/environments/staging`

## Custom Deployment Protection Rule Integration (WB-SUG-113)

Policy:

1. Promotion environments integrate custom protection rules for service-health gating.
2. Deployment requests are blocked when protection-rule status is degraded.
3. Protection-rule provider identity and SLA are documented in operator packet evidence.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/environments/staging/protection-rules`

## Foreman Bench Advisory Protection Service Contract (WB-SUG-134)

Policy:

1. Custom protection service blocks deployment when JetStream advisories indicate degraded or critical stream health.
2. Protection decisions include advisory stream identity, decision timestamp, and gate owner.
3. Advisory-gate outcomes are attached as promotion evidence before cutover approval.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/environments/staging/protection-rules`

## Environment Wait Timer and Required Reviewer Policy (WB-SUG-114)

Policy:

1. Promotion environments configure a non-zero wait timer before deployment starts.
2. required reviewers are mandatory for guarded environments.
3. Wait timer and reviewer assignments are validated at each cutover wave.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/environments/staging`

## Deployment Branch/Tag Allowlist Policy (WB-SUG-115)

Policy:

1. Prod-like environments allow only release branch/tag patterns.
2. Required allowlist baseline includes `release-*` and `hotfix-*`.
3. Promotion from non-allowlisted refs is treated as policy drift.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/environments/staging/deployment-branch-policies`

## Disable Admin Bypass for Guarded Environments (WB-SUG-116)

Policy:

1. Guarded promotion environments disable admin bypass.
2. Admin bypass attempts are treated as `hard_block` incidents.
3. Any temporary bypass exception requires explicit expiry and owner.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/environments/staging`

## Required Check Source Pinning (WB-SUG-045 and WB-SUG-065)

Policy:

1. Required status checks are pinned to an expected GitHub App source.
2. Ruleset definitions must include check context and source pairing for each required check.
3. Source changes are handled as `hard_block` until explicitly approved in CP packet review.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/rulesets --paginate`

## Ruleset Required Code-Scanning Results (WB-SUG-060)

Policy:

1. Protected branch rulesets require code-scanning results for merge eligibility.
2. Blocking set includes high-severity findings in workflow/security scanning lanes.
3. Temporary exception windows require explicit expiry and owner assignment.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/rulesets --paginate`

## Ruleset Path and File-Size Restrictions (WB-SUG-061)

Policy:

1. Rulesets define path restrictions for high-risk control-plane paths.
2. Rulesets enforce file size restrictions for oversized artifact commits.
3. Restriction bypass requests require packet evidence and expiry.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/rulesets --paginate`

## Linear History and Merge Method Alignment (WB-SUG-062)

Policy:

1. Protected branches require linear history to preserve rollback clarity.
2. Merge method configuration aligns with linear history policy.
3. Divergent merge settings are treated as policy drift.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}`

## Signed-Commit Pilot Rollout (WB-SUG-063)

Policy:

1. Signed commits are piloted on sensitive protected branches first.
2. Expansion to additional branches follows two stable waves with no blocker regressions.
3. Unsigned commit exceptions require explicit owner and sunset date.
4. Policy language uses signed commits as the required baseline for pilot branches.

Audit command (admin/API lane):

- `gh api repos/{owner}/{repo}/rulesets --paginate`

## Self-Hosted Runner Group and Repository Boundary Policy (WB-SUG-064)

Policy:

1. If self-hosted runners are introduced, jobs must target explicit runner groups.
2. Self-hosted runner groups are restricted to private-repo-only assignments.
3. Broad `self-hosted` selectors without group/label constraints are prohibited.

Audit command (admin/API lane):

- `gh api orgs/{org}/actions/runner-groups`
- `gh api repos/{owner}/{repo}/actions/runners`

## CODEOWNERS Control-Plane Stewardship (WB-SUG-046 and WB-SUG-066)

Policy:

1. `.github/CODEOWNERS` defines control-plane ownership boundaries.
2. At minimum, ownership is explicit for:
   - `/.github/workflows/**`
   - `/scripts/check_*.py`
   - `/scripts/run_quality_gates.py`
3. CODEOWNERS drift is treated as a policy regression and blocked by quality gates.

## Merge-Queue Timeout Triage Playbook (WB-SUG-067)

When a PR is Removed from merge queue, run the triage sequence:

1. Capture the exact removal reason and timestamp in handoff notes.
2. Verify required check parity (`pull_request` + `merge_group`) and sentinel coverage.
3. Re-run failed checks with debug enabled when root cause is ambiguous.
4. If timeout exceeds merge SLO window, remove/requeue once with evidence in run summary.

Operator command references:

- `gh run list --workflow "Workbench CI" --limit 20`
- `gh run rerun <run-id> --failed --debug`

## Argus Watchtower Multi-Signal Promotion Gate (WB-SUG-125)

Policy:

1. Promotion requires a single aggregated gate decision across three mandatory signals: CI pass, provenance pass, and advisory health pass.
2. Advisory health must be `healthy`; `degraded` or `critical` advisory posture blocks promotion and requires incident linkage.
3. Gate decision artifacts are attached before promotion as `docs/reports/argus_watchtower_gate.json`.

Reference artifact:

- `scripts/evaluate_promotion_watchtower.py`

## Janus Gate Two-Stage Promotion Policy (WB-SUG-126)

Policy:

1. Stage 1 review gate requires environment reviewer approval with prevent-self-review controls enforced.
2. Stage 2 runtime health gate requires healthy runtime/advisory posture after review approval and before promotion.
3. Both stages must pass; evidence is attached as `docs/reports/janus_gate_evidence.json`.

## Merge Queue Build Concurrency Tuning (WB-SUG-044)

Policy:

1. Merge queue build concurrency starts with conservative values and is tuned only after two stable campaign waves.
2. Concurrency changes require recorded rationale tied to queue throughput and failure rate.
3. Aggressive concurrency changes without evidence are treated as policy drift.

## Protected Environment Promotion Gate Contract (WB-SUG-047)

Policy:

1. Promotion environments require reviewers and prevent self-review for guarded deploy paths.
2. Promotion requests require successful environment checks before merge/promotion completion.
3. Reviewer and gate settings are revalidated each cutover wave.

## OIDC Deploy Identity Policy (WB-SUG-048)

Policy:

1. External deployment identities use OIDC federation with short-lived credentials.
2. Long-lived cloud credentials in repo/org secrets are prohibited for deploy jobs.
3. Deploy workflows that authenticate to cloud targets require `id-token: write` and explicit audience/role bindings.

## Canary Rollout Policy for Workflow/Gate Changes (WB-SUG-049)

Policy:

1. New workflow or gate controls are rolled out in a single canary lane before broad rollout.
2. Canary lanes run at least one stable wave before promotion to all lanes.
3. Canary rollback conditions are captured in run-summary handoff notes.

## Steady-State Metrics and Chaos Drill Cadence (WB-SUG-050)

Policy:

1. Steady-state merge/deploy metrics are reviewed weekly (success rate, queue latency, rollback count).
2. Controlled chaos drills run monthly to validate containment and recovery actions.
3. Chaos drill outcomes are attached to campaign retrospectives.

## Merge Queue Timeout SLO Policy (WB-SUG-051)

Policy:

1. Merge queue timeout windows are bound to CI SLO targets.
2. Timeout removals trigger requeue triage and owner assignment.
3. Repeated timeout breaches in a wave trigger `hard_block` escalation.

## Weekly Ruleset Drift Audit (WB-SUG-052)

Policy:

1. Ruleset drift audit runs weekly via repository rulesets REST output.
2. Drift audit output is stored as `docs/reports/ruleset_drift_audit.json`.
3. Unreviewed drift findings block promotion decisions.

## Hephaestus Seal Provenance Gate (WB-SUG-053)

Policy:

1. Promotion requires provenance verification success before deployment approval.
2. Provenance failures are treated as `hard_block` outcomes.
3. Provenance evidence links are attached in promotion packet artifacts.

## Arsenal Dock Timed Merge Lane (WB-SUG-054)

Policy:

1. High-volume merge waves are executed in timed merge windows.
2. Timed windows include precomputed compatibility checks and queue readiness confirmation.
3. Off-window merge exceptions require owner approval and incident note linkage.

## Required Local Artifacts

- `.github/CODEOWNERS`
- `.github/workflows/required-check-sentinel.yml`
- `docs/research/CP_RUNBOOK_COMMANDS.md`
- `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`
- `scripts/check_merge_ruleset_deployment_guardrails.py`
- `scripts/evaluate_promotion_watchtower.py`
- `docs/reports/ruleset_drift_audit.json`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_merge_ruleset_deployment_guardrails.py` | `[ok] merge/ruleset/deployment guardrails check` |
| `python3 scripts/check_merge_queue_readiness.py` | `[ok] merge queue readiness check` |
| `python3 scripts/evaluate_promotion_watchtower.py --ci-pass true --provenance-pass true --advisory-health healthy --review-approved true --runtime-health healthy` | Prints `promotion_allowed: true` decision payload |
| `gh api repos/{owner}/{repo}/rulesets --paginate > docs/reports/ruleset_drift_audit.json` | Produces weekly ruleset drift audit artifact |
| `cat docs/reports/ruleset_drift_audit.json` | Shows current drift posture artifact |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `merge-ruleset-deployment-guardrails` gate |
| `cat .github/CODEOWNERS` | Contains control-plane ownership entries |
