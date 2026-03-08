# Suggestions Bin Archive

Date: 2026-02-18  
Scope: `Workbench/**`  
Purpose: Preserve rotated `WB-SUG` entries moved out of active `docs/SUGGESTIONS_BIN.md` to maintain active-bin cap (`<=100`).

## Rotation Context

- Rotation batch: `2026-02-18`
- Reason: Promote new repo-specific advancement suggestions while preserving active bin at 100 entries.
- Active bin reference: `docs/SUGGESTIONS_BIN.md`

## Archived Entries

| ID | Title | Final status | Closure evidence |
| --- | --- | --- | --- |
| `WB-SUG-043` | Require merge queue on `main` and add `merge_group` trigger to required workflows. | `implemented` | `.github/workflows/ci.yml` + `.github/workflows/size-check.yml` + `.github/workflows/required-check-sentinel.yml` |
| `WB-SUG-044` | Tune merge queue build concurrency to match weekly wave capacity. | `implemented` | `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-045` | Bind required status checks to the expected app/integration source in rulesets. | `implemented` | `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-046` | Add `CODEOWNERS` protection for `.github/workflows/**` and gate scripts. | `implemented` | `.github/CODEOWNERS` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-047` | Use protected environments with required reviewers and prevent self-review for promotion-wave jobs. | `implemented` | `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-048` | Replace long-lived cloud credentials with OIDC for any external publish/deploy steps. | `implemented` | `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-049` | Apply canary rollout policy to workflow/gate changes (one canary wave at a time). | `implemented` | `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-050` | Define campaign steady-state metrics and run monthly controlled chaos drills. | `implemented` | `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-051` | Set explicit merge-queue status-check timeout policy tied to CI SLOs. | `implemented` | `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
| `WB-SUG-052` | Add weekly ruleset drift audit via REST API and publish report artifact. | `implemented` | `docs/reports/ruleset_drift_audit.json` + `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py` |
