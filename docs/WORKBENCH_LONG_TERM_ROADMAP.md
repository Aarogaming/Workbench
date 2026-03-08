# Workbench Long-Term Roadmap (12-Month Parallel Program)

Date: 2026-02-15  
Status: Proposed for pre-approval  
Scope: Workbench-only roadmap aligned to AAS governance  
Planning window: 2026-03-01 through 2027-02-28  
Execution model: 8+ parallel agents with central integration control

## 1. Purpose

Define a Workbench-specific, one-year program that is safe for rapid parallel execution by 8+ agents and can be approved upfront for extended autonomous runs.

## 2. Reviewed Inputs (Already Completed Work)

Workbench local:

1. `docs/reports/workbench_gap_assessment_2026-02-15.md`
2. `docs/reports/workbench_supply_chain_plan_2026-02-15.md`
3. `RUNBOOK.md`
4. `docs/OPERATIONS.md`
5. `docs/PLUGIN_CONTRACT_OWNERSHIP.md`
6. `scripts/run_quality_gates.py`
7. `scripts/validate_workspace_index.py`
8. `scripts/eval_report.py`
9. `.github/workflows/ci.yml`
10. `.github/workflows/nightly-evals.yml`

Parent governance and planning:

1. `../docs/planning/NEXT_PHASES_EXECUTION_PLAN_2026-02-15.md`
2. `../docs/governance/CONTINUE_UNTIL_DONE_ORCHESTRATION.md`
3. `../docs/governance/GATE_POLICY.md`
4. `../docs/AAS_CONTROL_PLANE_ALIGNMENT.md`
5. `../docs/planning/IMPLEMENTATION_STATUS.md`
6. `../docs/planning/DEV_LIBRARY_EXECUTION_BATCHES.md`
7. `../docs/planning/AI_TOOL_SELECTION_MATRIX.md`
8. `../docs/planning/RESEARCH_FIRST_SCAFFOLDING_SYSTEM.md`

Neighbor references used for compatibility constraints:

1. `../Library/docs/source-of-truth/MULTI_PHASE_PLAN.md`
2. `../Library/docs/repo-alignment/ARTIFACT_CONVENTION_POLICY.md`
3. `../Maelstrom/docs/repo-alignment/README.md`
4. `../Merlin/docs/protocols/compatibility-policy.md`
5. `../AndroidApp/docs/QA_RELEASE_RUNBOOK.md`

## 3. Baseline Snapshot (2026-02-15)

Validated locally:

1. `python3 scripts/run_quality_gates.py` passed (`8/8`).
2. `pytest -q` passed (`55` tests).
3. `python3 scripts/eval_report.py --baseline evals/baselines/main.json` passed (`7/7`, pass rate `1.000`).

Validated in GitHub Actions on commit `4b8fdac570facdc2faa39c0d950d0d645ed0b6f9`:

1. `Workbench CI` success (`22034004047`).
2. `Check File Sizes` success (`22034004051`).
3. `Nightly Evals` success (`22034030058`).
4. `Verify Nightly Attestations` skipped on private repo by policy (`22034035311`).

Current structural snapshot:

1. Manifest plugins: `9`.
2. Flat helper modules in `plugins/`: `34`.
3. Workflow files: `9`.
4. Neighbor-audit history indicates parent-workspace submodule drift risk.

## 4. Parallel Execution Model (8+ Agents)

## 4.1 Lane Topology

Use fixed lanes to avoid overlap and thrash.

1. `A0` Program Orchestrator:
Owns campaign queue, approvals, integration branch, terminal reports.
2. `A1` Plugin Migration Lane:
Manifest conversion and plugin packaging.
3. `A2` Plugin Contracts Lane:
Capability export checks, ownership, deprecation notes.
4. `A3` Test Lane:
Unit/integration coverage growth, flaky-test mitigation.
5. `A4` Eval Lane:
Scenario expansion, baseline stewardship, trend analysis.
6. `A5` CI/Supply-Chain Lane:
Workflow policy, dependency review, SBOM/provenance controls.
7. `A6` Ops/Runbooks Lane:
Run profiles, approval packets, incident playbooks, lifecycle docs.
8. `A7` Cross-Repo Compatibility Lane:
Interop fixtures, compatibility bundles, parent alignment evidence.
9. `A8+` Reserve Lane:
Hotfixes, blockers, and spillover.

## 4.2 Coordination Rules

1. Every campaign has one owner lane and one integration reviewer lane.
2. Path locks are declared before execution and respected for the full wave.
3. No direct pushes from non-orchestrator lanes to `main`.
4. Merge order is deterministic: contracts, code, tests, docs, release notes.
5. If two campaigns touch the same file, one is deferred to next wave.

## 4.3 Wave Cadence

1. Wave length: 1 week.
2. Planning window: Monday UTC.
3. Execution window: Tuesday through Thursday UTC.
4. Stabilization window: Friday UTC.
5. Retro and ratchet: Sunday UTC.

## 5. Annual Outcomes (End-State Targets by 2027-02-28)

1. Manifest plugin count increases from `9` to `>=24`.
2. Flat helper module count decreases from `34` to `<=15`.
3. Eval scenarios increase from `7` to `>=60`.
4. Quality-gate pass rate sustained at `>=95%` by week.
5. Mean red-to-green recovery for required gates under `24h`.
6. Hard-block rate for approved campaigns under `10%`.
7. All campaign runs produce terminal artifact bundles with schema-valid outcomes.

## 6. One-Year Phased Roadmap

## Phase 1: Program Bootstrapping (2026-03-01 to 2026-04-30)

Goal: Stand up pre-vetted parallel campaign machinery.

Deliverables:

1. `docs/WORKBENCH_RUN_PROFILES.md` with `dry_run`, `guarded_impl`, `promotion_wave`.
2. `docs/WORKBENCH_APPROVAL_PACKET_TEMPLATE.md` and review checklist.
3. `scripts/run_preflight_campaign.sh` for pre-run gating.
4. `scripts/record_campaign_outcome.py` with terminal schema enforcement.
5. Campaign artifact directory convention under `docs/reports/campaigns/`.
6. Campaign wave policy pack:
`docs/research/CAMPAIGN_WAVE_OPERATIONS_POLICY.md` and templates under `docs/research/templates/`.

Exit gates:

1. Two full dry-run waves complete with no missing artifacts.
2. No campaign starts without preflight pass and approval packet.

Primary lanes:

1. `A0`, `A5`, `A6`.

## Phase 2: Plugin Governance Wave 1 (2026-05-01 to 2026-06-30)

Goal: Move critical helper modules into explicit manifest ownership.

Deliverables:

1. Prioritized top-12 helper module migration backlog.
2. First 8 conversions to manifest-backed plugin packages.
3. Capability ownership matrix update and deprecation notes.
4. Added tests for converted modules.

Exit gates:

1. Manifest plugin count reaches `>=17`.
2. No duplicate critical capability exports.

Primary lanes:

1. `A1`, `A2`, `A3`.

## Phase 3: Test and Eval Expansion (2026-07-01 to 2026-08-31)

Goal: Raise confidence for long unattended execution.

Deliverables:

1. Eval expansion from `7` to `>=30` scenarios.
2. Targeted reliability tests for:
`plugins/workflow_engine.py`, `plugins/mcp_auth.py`, `plugins/integration_engine.py`.
3. Flaky-test detector workflow and rerun policy.
4. Eval trend report with moving-window regression flags.
5. Weekly DORA + reliability scoreboard artifacts:
`docs/reports/dora_reliability_scoreboard.json` and `docs/reports/dora_reliability_scoreboard.md`.

Exit gates:

1. `pytest` and eval report both stable through 4 consecutive waves.
2. Regression visibility includes trend-based warning, not only hard fail.

Primary lanes:

1. `A3`, `A4`, `A5`.

## Phase 4: Autonomous Campaign Runtime (2026-09-01 to 2026-10-31)

Goal: Implement Workbench-local continue-until-done run engine.

Deliverables:

1. `scripts/campaign_loop.py` with step-back retries and hard-block qualification.
2. Deterministic terminal outcome contract:
`complete`, `hard_block`, `cancelled`.
3. Campaign trace capture and replay utility.
4. Tests for soft-block recovery and hard-block determinism.
5. OpenAI async execution policy baseline:
`docs/research/OPENAI_ASYNC_EXECUTION_POLICY.md`.

Exit gates:

1. Replay of the same campaign inputs yields consistent terminal class.
2. Hard-block output always includes required unblock inputs.

Primary lanes:

1. `A0`, `A4`, `A6`.

## Phase 5: Private-Repo Provenance and Security Ratchet (2026-11-01 to 2026-12-31)

Goal: Close provenance and policy gaps for private repositories.

Deliverables:

1. Private provenance fallback policy in `docs/OPERATIONS.md`.
2. Internal artifact integrity verification path when attestations are unavailable.
3. SBOM generation and artifact retention policy for CI/nightly.
4. Vulnerability triage SLA workflow for Dependabot findings.

Exit gates:

1. Every nightly artifact has accepted provenance evidence path.
2. Security policy review workflow includes provenance and SBOM checks.

Primary lanes:

1. `A5`, `A6`.

## Phase 6: Plugin Governance Wave 2 + Cross-Repo Compatibility (2027-01-01 to 2027-02-28)

Goal: Finish annual migration wave and lock cross-repo contract compatibility.

Deliverables:

1. Additional 7 plugin conversions and cleanup of legacy helper surfaces.
2. Cross-repo `AGENT_INTEROP_V1` compatibility fixtures and bundle command.
3. Deprecation windows and migration notes aligned with Merlin policy.
4. Annual compatibility evidence packet for AAS governance review.

Exit gates:

1. Manifest plugin count reaches annual target (`>=24`).
2. Cross-repo bundle passes before any interop-impacting merge.

Primary lanes:

1. `A1`, `A2`, `A7`.

## 7. Pre-Approved Campaign Framework

A campaign is pre-approved only when all conditions are met:

1. Approval packet stored in repo with owner, scope, and rollback.
2. `python3 scripts/run_quality_gates.py` is green on campaign start SHA.
3. Path locks are listed and conflict-free.
4. Risk budget and hard-block escalation inputs are defined.
5. Expected terminal artifacts and schema are defined before execution.

Required campaign artifact bundle:

1. Approval packet.
2. Preflight output.
3. Terminal outcome JSON.
4. Gate/eval evidence bundle.
5. Post-run risk summary and next-wave recommendation.

## 8. Parallel Throughput Guardrails

1. Maximum concurrent campaigns: `8` active plus `1` reserve.
2. Maximum in-flight PRs per lane: `2`.
Policy reference: `docs/research/CAMPAIGN_WAVE_OPERATIONS_POLICY.md` lane WIP table.
3. Required rebase window before merge: same-day with gate rerun.
4. If gate failure rate exceeds `20%` in a wave, new campaigns pause for 24h stabilization.
5. If two consecutive waves miss Friday stabilization, reduce active campaigns by 2 for next wave.

## 9. Initial 90-Day Queue (First Three Months of the Annual Plan)

1. Campaign A:
Program bootstrapping docs, templates, and scripts.
2. Campaign B:
Top 4 plugin helper-to-manifest conversions.
3. Campaign C:
Eval expansion to first 15 scenarios plus trend report scaffolding.
4. Campaign D:
Campaign trace and terminal outcome schema test harness.
5. Campaign E:
Private provenance fallback design draft and policy review.

## 10. Review and Ratchet Cadence

1. Weekly:
Wave review, blocker triage, lane utilization, and conflict analysis.
2. Monthly:
Adjust campaign queue and path-lock map by observed failure patterns.
3. Quarterly:
Ratchet thresholds, refresh targets, and sync with parent AAS governance.
4. Annual closeout (2027-02):
Publish one-year outcomes, carry-over backlog, and next-year roadmap.
