# Dependency Review Supply-Chain Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## Dependency Review Risk Threshold Policy (WB-SUG-112)

Policy:

1. Dependency review action runs with a repository-owned config file.
2. Config enforces `fail-on-severity` threshold for blocking vulnerabilities.
3. Config enforces `fail-on-scopes` to block risky runtime/unknown scope changes.
4. Config defines deny-group packages for known high-risk dependencies.

Reference artifact:

- `.github/dependency-review-config.yml`

## Required Local Artifacts

- `docs/research/DEPENDENCY_REVIEW_SUPPLY_CHAIN_POLICY.md`
- `.github/dependency-review-config.yml`
- `.github/workflows/dependency-review.yml`
- `scripts/check_dependency_review_policy.py`
- `docs/research/CP_RUNBOOK_COMMANDS.md`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_dependency_review_policy.py` | `[ok] dependency review policy check` |
| `cat .github/dependency-review-config.yml` | Contains `fail-on-severity`, `fail-on-scopes`, and deny-group package settings |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `dependency-review-policy` gate |
