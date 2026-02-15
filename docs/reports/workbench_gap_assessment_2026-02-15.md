# Workbench Evaluation + AI Tooling Gap Plan (2026-02-15)

## Scope and method

This review combined:

1. Local repo audit and tests
2. Code review of representative Workbench modules
3. External research across current GitHub projects and official AI tooling docs

Validation commands run on 2026-02-15:

- `python3 scripts/validate_workspace_index.py --suite-root ..`
- `python3 scripts/validate_workspace_index.py --suite-root .. --strict-enforced-only --ignore-submodule-dirty --ignore-submodule-ahead`
- `python3 -m pytest -q`
- `python3 -m compileall -q .`

## Current snapshot

- Python files: `102`
- Test files: `10`
- GitHub workflows: `9`
- Manifest-based plugins: `9`
- `pytest`: `55 passed`

## Execution status (2026-02-15)

All plan phases in this report have been implemented in Workbench:

1. Phase 0:
- CI now runs unit tests.
- Secret hygiene guard supports strict fail-closed behavior in CI.
- Smoke tests cover workflow/auth/size-guard paths.
2. Phase 1:
- Workflow pause/resume is cursor-based instead of restart-based.
- Scheduler enforces trigger/delay readiness checks.
- MCP auth now uses explicit verification semantics with typed error codes.
3. Phase 2:
- Added deterministic eval scenarios + baseline files under `evals/`.
- Added `scripts/eval_report.py` and report artifacts under `docs/reports/`.
- Added nightly eval workflow.
4. Phase 3:
- Added workflow execution metrics and richer status reporting.
- Added `scripts/mcp_smoke.py` for MCP compatibility checks.
- Added `docs/OPERATIONS.md` and `docs/PLUGIN_CONTRACT_OWNERSHIP.md`.
5. Post-plan hardening extension:
- Added workflow supply-chain controls (SHA pinning policy, dependency review, Dependabot).
- Added Scorecards and weekly policy review workflows.
- Added workflow artifact attestations in nightly evals and exception-governance audits.
- Added scorecard threshold policy enforcement with report artifacts.
- Added reusable policy/scorecards workflows and downstream nightly attestation verification flow.
- Added scorecard historical trend artifacts for baseline drift visibility.

## Historical findings (resolved)

All originally identified Phase 0-3 gaps in this report have been resolved:

1. Workflow pause/resume and scheduling semantics:
- Cursor-based resume + delay/trigger enforcement now in `plugins/workflow_engine.py`.
- Covered by `tests/test_phase0_smoke.py`.
2. MCP auth trust model:
- Typed verification/auth error paths and measured latency now in `plugins/mcp_auth.py`.
- Covered by `tests/test_phase0_smoke.py` and eval scenarios.
3. CI coverage:
- Unit tests, plugin contract audit, and eval report run in `/.github/workflows/ci.yml`.
- Nightly eval pipeline added in `/.github/workflows/nightly-evals.yml`.
4. Guardrail reliability:
- Strict fail-closed secret hygiene behavior implemented in `scripts/check_secret_hygiene.py`.
- Covered by `tests/test_check_secret_hygiene.py`.
5. Contract and eval discipline:
- Plugin contract audit in `scripts/check_plugin_contracts.py`.
- Eval harness + baseline in `scripts/eval_report.py` and `evals/`.

## External benchmark (GitHub + official docs)

Signals from active ecosystem projects and official guidance:

- MCP is now an established interoperability direction.
  - Model Context Protocol: https://modelcontextprotocol.io/
  - GitHub MCP Registry/docs: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-review/configure-mcp-server
- Agent frameworks with strong adoption (checked 2026-02-15):
  - LangGraph (~109k stars): https://github.com/langchain-ai/langgraph
  - CrewAI (~39k stars): https://github.com/crewAIInc/crewAI
  - AutoGen (~56k stars): https://github.com/microsoft/autogen
  - OpenHands (~56k stars): https://github.com/All-Hands-AI/OpenHands
- Agentic coding workflows are converging on explicit loops + tool execution:
  - Claude Code docs: https://docs.anthropic.com/en/docs/claude-code
  - Aider project: https://github.com/Aider-AI/aider
- Eval-driven development is now table-stakes for AI systems:
  - OpenAI Evals design guide: https://platform.openai.com/docs/guides/evals-design
- Popular modern utility stack for fast Python/tooling loops:
  - uv: https://github.com/astral-sh/uv
  - Ruff: https://github.com/astral-sh/ruff
  - Gitleaks: https://github.com/gitleaks/gitleaks
  - Trivy: https://github.com/aquasecurity/trivy

## Gap map

1. Testing and reliability
- Current: syntax checks + one focused pytest file.
- Target: multi-layer test pyramid (unit, contract, smoke) over critical plugins/scripts.

2. CI quality gates
- Current: compile/gitleaks/index audit only.
- Target: mandatory pytest suite, changed-files test subset, optional nightly deep checks.

3. Auth/security semantics
- Current: simulated auth outputs and permissive failure modes.
- Target: verified token introspection path, explicit scope mapping, fail-closed policy for guard rails.

4. AI evaluation discipline
- Current: no formal eval harness for AI/agent behavior.
- Target: scenario-based eval suite with pass/fail thresholds and trend reporting.

5. Observability and operations
- Current: limited runtime telemetry in helper modules.
- Target: structured logs + outcome metrics for workflow runs, syncs, and plugin calls.

## Prioritized plan

### Phase 0 (Week 1) - Guardrail hardening

1. Add CI `pytest -q` step in `.github/workflows/ci.yml`.
2. Convert `check_secret_hygiene.py` to fail-closed in CI contexts (strict mode/env flag).
3. Add smoke tests for:
- `plugins/workflow_engine.py`
- `plugins/mcp_auth.py`
- `plugins/repo_size_guard/plugin.py`

Exit criteria:

- CI fails on unit regressions, not only syntax/index checks.

### Phase 1 (Weeks 2-3) - Contract correctness

1. Fix workflow pause/resume semantics with persisted cursor state.
2. Implement actual schedule enforcement for `trigger`/`delay`.
3. Replace synthetic MCP auth outputs with explicit verification contract and typed error paths.

Exit criteria:

- Deterministic tests for pause/resume, delayed scheduling, and auth validation behavior.

### Phase 2 (Weeks 4-6) - AI eval infrastructure

1. Create `evals/` with golden scenarios for key agent/tooling tasks.
2. Add pass/fail scoring and baseline snapshots.
3. Add CI/nightly eval run and trend artifact.

Exit criteria:

- Reproducible eval report for each change set.

### Phase 3 (Weeks 6-8) - Operations and ecosystem alignment

1. Add structured execution metrics for workflow and plugin operations.
2. Add MCP compatibility smoke checks for configured servers.
3. Expand docs/runbooks for incident response and plugin contract ownership.

Exit criteria:

- Observable runtime behavior and clear operator playbooks.

## Suggested script backlog

1. `scripts/run_quality_gates.py`
- Single entrypoint for secret check, size guard, compileall, pytest, index audit.

2. `scripts/test_changed.py`
- Run targeted tests from changed paths and plugin manifests.

3. `scripts/check_plugin_contracts.py`
- Validate manifest entrypoints, command exports, and duplicate capability collisions.

4. `scripts/mcp_smoke.py`
- Validate MCP server reachability, auth mode, and tool list consistency.

5. `scripts/eval_report.py`
- Produce compact markdown/json scorecards for AI task evals.

## Recommended KPIs

1. Test coverage: from current narrow scope to >=70% on prioritized plugin/script set.
2. CI signal quality: <5% flaky runs; all required checks under 10 minutes.
3. Mean time to detect regression: same PR (not post-merge).
4. Security gate reliability: zero silent-pass secret check failures.
5. Eval stability: <=10% variance on golden AI tasks release-to-release.
