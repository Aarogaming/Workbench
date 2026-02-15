# Runbook

## Baseline checks

- Repository state:
  - `git status --short --branch`
- Protocol baseline present:
  - `test -f protocols/AGENT_INTEROP_V1.md && echo ok`
- Full quality gate bundle:
  - `python3 scripts/run_quality_gates.py`

## Index and neighbor audit

- Validate Workbench + neighboring targets from policy (`scripts/workspace_index_targets.json`):
  - `python scripts/validate_workspace_index.py --suite-root ..`
- Full neighboring submodule sweep (writes dedicated report artifacts):
  - `python scripts/validate_workspace_index.py --suite-root .. --include-all-submodule-targets --json-out docs/reports/workspace_neighbor_audit.json --md-out docs/reports/workspace_neighbor_audit.md`
- Print machine-readable issue summary from latest report:
  - `python - <<'PY'\nimport json\nfrom pathlib import Path\np = Path('docs/reports/workspace_index_audit.json')\ndata = json.loads(p.read_text(encoding='utf-8'))\nprint(json.dumps(data.get('issue_summary', {}), indent=2))\nPY`
- Print submodule reconciliation plan from latest report:
  - `python - <<'PY'\nimport json\nfrom pathlib import Path\np = Path('docs/reports/workspace_index_audit.json')\ndata = json.loads(p.read_text(encoding='utf-8'))\nprint(json.dumps(data.get('submodule_reconciliation_plan', []), indent=2))\nPY`
- Override targets explicitly:
  - `python scripts/validate_workspace_index.py --suite-root .. --targets ToolsShared Utilities Workbench`
- Enforce baseline only for specific targets:
  - `python scripts/validate_workspace_index.py --suite-root .. --targets ToolsShared Utilities Workbench --enforce-targets Workbench`
- Fail on enforced-target drift plus submodule/template/plugin warnings (ignore context-target warnings):
  - `python scripts/validate_workspace_index.py --suite-root .. --strict-enforced-only`
- Same as above, but ignore local submodule dirty-worktree noise while still enforcing pointer drift:
  - `python scripts/validate_workspace_index.py --suite-root .. --strict-enforced-only --ignore-submodule-dirty`
- Ignore both dirty-worktree and ahead-only submodule drift during active local development:
  - `python scripts/validate_workspace_index.py --suite-root .. --strict-enforced-only --ignore-submodule-dirty --ignore-submodule-ahead`
- Treat warnings as failures:
  - `python scripts/validate_workspace_index.py --suite-root .. --strict`

## Plugin contracts

- Validate manifest + entrypoint contracts:
  - `python3 scripts/check_plugin_contracts.py`
- Validate workflow action pinning:
  - `python3 scripts/check_workflow_pinning.py`
- Review workflow pinning exceptions:
  - `python3 scripts/check_workflow_pinning_exceptions.py`
- Run tests mapped to changed files:
  - `python3 scripts/test_changed.py --fallback-all`

## Eval pipeline

- Generate eval report using baseline:
  - `python3 scripts/eval_report.py --baseline evals/baselines/main.json`
- Update baseline intentionally:
  - `python3 scripts/eval_report.py --update-baseline`
- Report outputs:
  - `docs/reports/eval_report.json`
  - `docs/reports/eval_report.md`

## MCP smoke checks

- Optional (skip if env not configured):
  - `python3 scripts/mcp_smoke.py`
- Require configured env + strict verification:
  - `python3 scripts/mcp_smoke.py --require-configured`
- Allow connectivity-only fallback:
  - `python3 scripts/mcp_smoke.py --allow-unverified --require-configured`

## Search hygiene

- Prefer repo-local scoped searches.
- Use `.rgignore` and `.ignore` to avoid scanning heavy paths.

## Scheduled security checks

- Scorecards workflow:
  - `/.github/workflows/scorecards.yml` (weekly, public repos)
- Workflow policy review workflow:
  - `/.github/workflows/policy-review.yml` (weekly exception/pinning review)
- Manual scorecard policy check:
  - `python3 scripts/check_scorecard_threshold.py --repo owner/name --allow-unavailable`
- Update scorecard history reports:
  - `python3 scripts/update_scorecard_history.py`
- Downstream attestation verification workflow:
  - `/.github/workflows/verify-nightly-attestations.yml` (verifies nightly-eval artifact attestations)
- Manual attestation verification:
  - `python3 scripts/verify_attestations.py --repo owner/name --subject path/to/artifact`
