# Suggestions Bin (Workbench)

Status: Active research-first intake  
Mode: ULTRA-FAST PASS  
Updated: 2026-02-15

## Pass 0 (capture)

- `WB-RS-001` Forge Run Summary Contract
  - repo_fit: Workbench is an operator/agent console; consistent run summaries reduce handoff entropy across 8+ parallel lanes.
  - source: https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary
  - impact: Faster triage and clearer shift turnover because every workflow exposes the same outcome, failures, and next action.
  - risk_class: `R0`
  - notes: Add a tiny markdown schema in `.github` workflows and include terminal class + retry command.

- `WB-RS-002` Gate Annotation Contract for script-based checks
  - repo_fit: Workbench has many local gate scripts (`check_secret_hygiene`, `check_workflow_pinning`, `eval_report`) where inline file/line signals speed repairs.
  - source: https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message
  - impact: Reduced mean diagnostic time for operators because failures land directly where they occur.
  - risk_class: `R0`
  - notes: Add stable prefix format in `scripts/*` and parseable annotation output in CI logs.

- `WB-RS-003` One-command Rerun and Recovery Path
  - repo_fit: Frequent reruns happen under concurrency spikes; operators need deterministic recovery actions not manual UI hunting.
  - source: https://docs.github.com/en/actions/managing-workflow-runs/re-running-a-workflow-and-jobs
  - impact: Lower operator friction during red states and lower stale-run burn-in.
  - risk_class: `R0`
  - notes: Add `scripts/recover_workflow.sh` wrapper that maps run IDs to rerun + artifact fetch.

- `WB-RS-004` Workflow Health Board in docs
  - repo_fit: Workbench runs multiple control workflows and depends on lane visibility during wave reviews.
  - source: https://docs.github.com/en/actions/managing-workflow-runs/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge
  - impact: Immediate health context for all operators entering a run.
  - risk_class: `R0`
  - notes: Add a consolidated badges page with latest result, skip cause, and responsible lane.

- `WB-RS-005` Handoff Packet Auto-Builder
  - repo_fit: Task handoff usability is central to 8+ lane execution; failed runs need one predictable evidence artifact.
  - source: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts
  - impact: Cleaner operator transitions and less context loss after failed transitions.
  - risk_class: `R1`
  - notes: Generate `handoff_packet.md/json` containing failing job, failing command, top log lines, artifacts.

- `WB-RS-006` Incident Pause Switch for optional workflows
  - repo_fit: Workbench has optional/nightly controls; incident periods should reduce noise automatically.
  - source: https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/disabling-and-enabling-a-workflow
  - impact: Reduced CI churn while preserving critical safety checks.
  - risk_class: `R1`
  - notes: Add `incident_mode` repo variable + required checks whitelist.

- `WB-RS-007` Queue Stall Sentinel
  - repo_fit: Parallel PRs can stall when required checks are pending due to filters, causing false deadlocks.
  - source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/troubleshooting-required-status-checks
  - impact: Fewer stuck PRs and faster unblocking decisions.
  - risk_class: `R1`
  - notes: Emit report if required check remains pending after path-filter-driven skip.

- `WB-RS-008` Failure Snapshot Artifact Standard
  - repo_fit: Diagnosing recurring failures in `run_quality_gates` and attestations needs deterministic repro data.
  - source: docs/OPERATIONS.md
  - impact: Shorter recovery timelines and fewer blind restarts.
  - risk_class: `R0`
  - notes: Standardize bundle keys: command, environment, git SHA, matrix values, log tails, schema version.

- `WB-RS-009` Idempotency-Key Policy for side-effecting actions
  - repo_fit: Campaign retries and replays currently appear across gate and eval workflows.
  - source: https://microservices.io/patterns/data/transactional-outbox.html
  - impact: Prevents duplicate side effects during retries and resume events.
  - risk_class: `R2`
  - notes: Require operation-id fields for scripts that call external systems.

- `WB-RS-010` Human-in-the-loop Promotion Gate
  - repo_fit: Workbench promotions are high-impact paths; explicit pause before promotion reduces high-severity incidents.
  - source: https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment
  - impact: Stronger auditability and separation of duties for production-like actions.
  - risk_class: `R1`
  - notes: Gate with required reviewers + optional wait timer.

- `WB-RS-011` Workflow Problem-Matcher Baseline
  - repo_fit: Failures from Python/JSON outputs dominate gate triage and are hard to locate.
  - source: https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message
  - impact: Faster fix cycles from direct annotations in PR check UI.
  - risk_class: `R0`
  - notes: Add `.github/problem-matchers/workbench.json` and import in CI gates.

- `WB-RS-012` Dual-Channel Gate Output
  - repo_fit: `run_quality_gates.py` feeds both operators and potential automation; both should get stable formats.
  - source: https://docs.python.org/3/library/json.html and scripts/run_quality_gates.py
  - impact: Better automation hooks and cleaner machine parsing of gate failures.
  - risk_class: `R1`
  - notes: Add `--json-out` and align keys with `docs/reports` schema.

- `WB-RS-013` Concurrency Lease for Critical Workflows
  - repo_fit: 8+ agents create overlapping queue pressure on CI and can duplicate the same lane work.
  - source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax-for-github-actions#concurrency
  - impact: Removes duplicate in-flight runs and reduces flaky merge contention.
  - risk_class: `R0`
  - notes: Add branch + purpose keyed `concurrency` groups in `ci.yml` and `nightly-evals.yml`.

- `WB-RS-014` Converged Gate Artifact Naming and Retention
  - repo_fit: Recovery scripts and incident handoffs currently parse mixed artifact names manually.
  - source: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts
  - impact: Faster targeted download and deterministic cleanup.
  - risk_class: `R1`
  - notes: Standardize names with timestamp + terminal-class and retention hints.

- `WB-RS-015` Argus Artifact Fetcher Command
  - repo_fit: Failed handoffs repeatedly request specific reports and eval artifacts.
  - source: https://cli.github.com/manual/gh_run_download
  - impact: Lower recovery latency by one command for core handoff evidence.
  - risk_class: `R0`
  - notes: Add a helper script under `scripts/fetch_workbench_artifacts.sh`.

- `WB-RS-016` Artifact Integrity + Diff Fingerprint
  - repo_fit: Handoff drift in reproducibility often hides behind report reruns with same filenames.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Easier dedupe and stronger proof that a handoff packet maps to a specific input set.
  - risk_class: `R1`
  - notes: Add `packet_sha256` and manifest-hash entries to terminal outcome JSON.

- `WB-RS-017` MCP Auth Source Normalization for Verify Scripts
  - repo_fit: `plugins/mcp_auth.py` and `scripts/mcp_smoke.py` accept multiple env keys with partial overlap.
  - source: plugins/mcp_auth.py and scripts/verify_attestations.py
  - impact: More reliable connectivity/auth diagnostics across Workbench and AAS env profiles.
  - risk_class: `R1`
  - notes: Add a shared credential-source report and explicit precedence docs for AI tooling and MCP auth.

- `WB-RS-018` GH CLI Dependency and Auth Guard
  - repo_fit: `verify-nightly-attestations.yml` depends on `gh` command and GH token sources.
  - source: https://docs.github.com/en/actions/writing-workflow-scripts/using-github-cli-in-workflows and https://cli.github.com/manual/
  - impact: Fewer opaque failures when token source or CLI version is unavailable.
  - risk_class: `R0`
  - notes: Validate `gh --version`, `GH_TOKEN` detection source, and command availability before attestation steps.

- `WB-RS-019` Checkout Integrity and Submodule Baseline Snapshot
  - repo_fit: Drift between Workspace and neighbor repos can create false-positive gates and stale baselines.
  - source: scripts/validate_workspace_index.py and docs/MASTER_ROADMAP_SYNC.md
  - impact: Reduced surprise failures from hidden index mismatches.
  - risk_class: `R1`
  - notes: Add preflight summary section of `git submodule status` and `workspace_index` snapshot hash.

- `WB-RS-020` Recovery Ladder and Terminal Taxonomy
  - repo_fit: Long campaigns already need `complete`/`hard-block` outcomes for continuation workflows.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and scripts/check_scorecard_threshold.py
  - impact: Deterministic resume behavior and stronger escalation criteria.
  - risk_class: `R1`
  - notes: Define `terminal_class` enum and include it in all terminal outcome artifacts.

- `WB-RS-021` PR Handoff Aging and Assignment SLA
  - repo_fit: Parallel handoffs decay during wave overlap and need explicit prioritization.
  - source: https://docs.github.com/issues/planning-and-tracking-with-projects/customizing-projects-and-workflows
  - impact: Faster recovery of stale blocks and fewer dropped tasks.
  - risk_class: `R2`
  - notes: Add `next_owner`, `requires_handoff_by`, and elapsed-hours tags into handoff schema.

- `WB-RS-022` Failure Taxonomy Controlled Vocabulary
  - repo_fit: Current failures are mostly free-form strings, slowing routing logic.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and https://www.oasis-open.org/
  - impact: Predictable handoff routing and cleaner policy dashboards.
  - risk_class: `R1`
  - notes: Standardize small enum set (`infra`, `script`, `policy`, `artifact`, `human_gate`, `supply_chain`).

- `WB-RS-023` Pre-merge Gate Drift Audit
  - repo_fit: Multiple gate scripts can drift in behavior; parallel lanes magnify silent baseline shifts.
  - source: https://docs.github.com/en/actions/automating-your-workflow-with-github-actions/creating-a-workflow
  - impact: Earlier warning before routine PRs fail on unexpected gate behavior shifts.
  - risk_class: `R2`
  - notes: Add weekly baseline artifact snapshot of key gate outputs and diff against history.

- `WB-RS-024` Live Lane and Lock Overlay (command-mode)
  - repo_fit: Workbench is lane-driven; operators need quick view of running lanes and lock ownership.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and https://docs.github.com/actions/workflow-syntax-for-github-actions#concurrency
  - impact: Better campaign scheduling and fewer conflicting starts.
  - risk_class: `R2`
  - notes: Add markdown dashboard (`docs/reports/active_lanes.md`) generated from local campaign registry.

- `WB-RS-025` Structured Runbook Command Registry
  - repo_fit: Run command discoverability is central to operator UX (`docs/OPERATIONS.md` is already the canonical source).
  - source: docs/OPERATIONS.md
  - impact: Lower command errors and quicker onboarding under distributed run ownership.
  - risk_class: `R1`
  - notes: Generate command catalog with intent, required args, risk class, rollback path, and owner.

- `WB-RS-026` Scope-Bound Retry Budget in Gate Scripts
  - repo_fit: Gate scripts share repetitive retry behavior and can waste CI minutes on no-retry loops.
  - source: https://requests.readthedocs.io/en/latest/user/advanced/#timeouts and https://tenacity.readthedocs.io/en/stable/
  - impact: More stable external calls and cleaner failure signatures.
  - risk_class: `R2`
  - notes: Introduce shared retry helpers for networked checks only, with metrics.

- `WB-RS-027` Dependency Health Trend Watch
  - repo_fit: Workbench security posture depends on scorecard/pinning policy and dependency checks.
  - source: scripts/check_scorecard_threshold.py and .github/workflows/scorecards.yml
  - impact: Early warning on trend regressions before hard failures.
  - risk_class: `R2`
  - notes: Add weekly trend diff and risk threshold escalation in scorecard review workflow.

- `WB-RS-028` Evidence Digest and Evidence-of-Origin Index
  - repo_fit: 8+ agent operations need defensible provenance across artifacts and command outputs.
  - source: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds and scripts/verify_attestations.py
  - impact: Faster confidence in recovery evidence and reduced audit friction.
  - risk_class: `R1`
  - notes: Add digest manifest that records source hashes for all campaign artifacts.

- `WB-RS-029` Gate Runbook Preflight Plan Mode
  - repo_fit: Workbench operators often need to preview intended checks before running long CI-gate campaigns.
  - source: scripts/run_quality_gates.py and docs/OPERATIONS.md
  - impact: Lower surprise failures and faster triage by showing exactly which gates will run and in what order.
  - risk_class: `R1`
  - notes: Add `--dry-run`/`--plan` mode to print gate list and command invocations without execution.

- `WB-RS-030` Test-Changed Mapping Drift Detector
  - repo_fit: `scripts/test_changed.py` has explicit module-to-test bindings and can drift from actual coverage needs.
  - source: scripts/test_changed.py
  - impact: Keeps `test_changed` recommendations accurate as plugin and script surfaces evolve.
  - risk_class: `R2`
  - notes: Add unit tests that compare mapping table against `plugins` and `scripts` inventories and fail on stale bindings.

- `WB-RS-031` Canonical Auth-Source Event for Handovers
  - repo_fit: Handoff packets currently include outcomes but not full auth provenance for downstream reproducibility.
  - source: plugins/mcp_auth.py and scripts/verify_attestations.py
  - impact: Improves reliability debugging when CI behavior differs by environment profile.
  - risk_class: `R1`
  - notes: Add shared redacted `auth_source` field to gate and attestation report payloads.

- `WB-RS-032` Artifact Class Matrix for Retrieval Paths
  - repo_fit: Operators and agents fetch artifacts by memory today, which slows handoffs.
  - source: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts and docs/OPERATIONS.md
  - impact: Faster recovery from failed runs by grouping artifact classes (`gates`, `attestations`, `eval`, `policy`).
  - risk_class: `R1`
  - notes: Add a small index file listing each artifact set and expected file names per workflow.

- `WB-RS-033` Nightly Workflow Artifact Signature Check
  - repo_fit: `nightly-evals` and `verify-nightly-attestations` form a critical trust pair that benefits from integrity checks.
  - source: .github/workflows/nightly-evals.yml and .github/workflows/verify-nightly-attestations.yml
  - impact: Detects broken artifact handoff before manual verification or evidence assembly.
  - risk_class: `R1`
  - notes: Add SHA256 manifest for each nightly artifact bundle and verify in the attestation workflow.

- `WB-RS-034` Concurrency Cancel In-Flight for Redundant Merges
  - repo_fit: Merge bursts under 8+ agents can leave stale redundant runs competing with fresh ones.
  - source: https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/canceling-a-workflow-run
  - impact: Reduces queue clutter and frees CI capacity for latest lane state.
  - risk_class: `R0`
  - notes: Enable `cancel-in-progress` in `merge_group`/`pull_request` if/when queue mode is adopted.

- `WB-RS-035` Token and CLI Presence Contract in Attestation Preconditions
  - repo_fit: `verify-nightly-attestations.yml` depends on both token source and `gh` binary.
  - source: scripts/verify_attestations.py and https://cli.github.com/manual/gh_auth_login
  - impact: Fewer false-negative verification runs and clearer operator instructions.
  - risk_class: `R0`
  - notes: Fail early with machine-readable remediation when `GH_TOKEN`/`.env` token and `gh` version checks fail.

- `WB-RS-036` Submodule Drift Checkpoint Record in Handoff Packet
  - repo_fit: Workbench sits in a workspace with neighbor repos and submodule alignment pressure.
  - source: scripts/validate_workspace_index.py and docs/MASTER_ROADMAP_SYNC.md
  - impact: Hardens recovery traceability for cross-repo dependency mismatches.
  - risk_class: `R1`
  - notes: Persist `git submodule status` and `workspace_index` hash into terminal handoff summaries.




- `WB-RS-037` Workflow Permission Boundary Sweep
  - repo_fit: Several workflows lack explicit least-privilege permissions and rely on defaults, which is risky for automation-heavy repos.
  - source: https://docs.github.com/en/actions/learn-github-actions/security-harden-your-workflows
  - impact: Stronger token safety and clearer auditability before rollout of any high-volume gate changes.
  - risk_class: `R1`
  - notes: Add explicit `permissions` blocks to every workflow and verify with a policy lint check.

- `WB-RS-038` Gate Command Timeout Budget Defaults
  - repo_fit: `run_quality_gates.py` and `scorecard/attestation` jobs can run long under transient issues; consistent timeboxes aid recovery.
  - source: https://docs.github.com/actions/learn-github-actions/usage-limits-and-time-outs-for-github-actions
  - impact: Better capacity control and less CI slot starvation during incident windows.
  - risk_class: `R0`
  - notes: Add explicit `timeout-minutes` and command-level timeout env defaults for long gate steps.

- `WB-RS-039` Coverage of Handoff Failure Codes
  - repo_fit: Handoff outcomes need machine-consumable error classes for triage dashboards and escalation policies.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and scripts/check_plugin_contracts.py
  - impact: Faster auto-routing of failures to the right lane owner and stronger campaign handoff quality.
  - risk_class: `R1`
  - notes: Add canonical `failure_code` values to gate and attestation outputs.

- `WB-RS-040` `workflow_dispatch` Incident Snapshot Inputs
  - repo_fit: Current incident control is mostly manual in docs; dispatch-time context shortens response windows.
  - source: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch
  - impact: Faster operator activation during outages or unusual congestion.
  - risk_class: `R0`
  - notes: Add optional `incident_mode`, `skip_low_risk`, `force_lane` inputs with safe defaults.

- `WB-RS-041` Handoff Packet Artifact Index Route
  - repo_fit: Workbench handoffs are artifact-driven and require predictable retrieval across repos and agents.
  - source: https://cli.github.com/manual/gh_run_download and docs/OPERATIONS.md
  - impact: Shorter recovery times by making artifact discovery path deterministic.
  - risk_class: `R1`
  - notes: Add a manifest file (`artifacts/index.json`) in each campaign packet listing all downloadable files.

- `WB-RS-042` Gate Script Exit Contract
  - repo_fit: Multiple scripts produce mixed success/failure text; normalized exits improve automated handoff decisioning.
  - source: https://docs.python.org/3/library/sys.html#sys.exit and scripts/check_workflow_pinning.py
  - impact: Predictable operator automation and clearer red/amber recovery actions.
  - risk_class: `R2`
  - notes: Standardize exit semantics (`0` pass, `1` fail, `2` warning) and map to terminal classes.

- `WB-RS-043` PR Label Hygiene for Workflow Health
  - repo_fit: Workbench lane coordination uses labels and comments to coordinate across runs; stale health labels create confusion.
  - source: https://docs.github.com/pull-requests/collaborating-with-pull-requests/managing-your-work-on-github/using-labels-and-milestones-to-manage-your-work
  - impact: Clearer operational triage when required checks are blocked/stalled.
  - risk_class: `R2`
  - notes: Add label cleanup workflow for stale `ci-failed` / `attest-failed` labels.

- `WB-RS-044` Workspace-Adjacent Dependency Drift Guard
  - repo_fit: Workbench depends on Workspace neighbors; submodule/version drift can break assumptions.
  - source: scripts/validate_workspace_index.py and docs/MASTER_ROADMAP_SYNC.md
  - impact: Lower campaign churn caused by environmental mismatch and silent drift.
  - risk_class: `R1`
  - notes: Add a preflight check that compares root/neighbor hash manifests before campaign start.

- `WB-RS-045` Campaign Lane Lock Registry Backing File
  - repo_fit: Workbench lane execution is distributed; lock state should be machine-readable and inspectable outside live memory.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and docs/MASTER_ROADMAP_SYNC.md
  - impact: Reduced double-claim conflicts on the same run path or workflow surface.
  - risk_class: `R1`
  - notes: Add a local lock registry file (`docs/reports/active_lanes.json`) with TTL and owner stamps.

- `WB-RS-046` Test-Changed Fallback Strategy
  - repo_fit: `scripts/test_changed.py` can produce empty plans on unmapped files, causing blind spots in focused reruns.
  - source: scripts/test_changed.py
  - impact: Better confidence before campaign start by flagging insufficient test coverage coverage path.
  - risk_class: `R2`
  - notes: In `--fallback-all` mode, include `--unmapped` summary and risk hint in output.

- `WB-RS-047` Plugin Contract Diff Badge in Ops Feed
  - repo_fit: Plugin migration lanes rely on contract stability; regressions in exports/capabilities need visible notice.
  - source: scripts/check_plugin_contracts.py and docs/PLUGIN_CONTRACT_OWNERSHIP.md
  - impact: Earlier detection of contract changes before dependent lanes consume broken exports.
  - risk_class: `R1`
  - notes: Emit change summary diff (delta count by plugin) into summary and handoff packet.

- `WB-RS-048` Structured Scorecard Drift Alert
  - repo_fit: Scorecard checks run on schedule and in policy review, but trend deltas are not always surfaced in ops.
  - source: .github/workflows/scorecards.yml and scripts/check_scorecard_threshold.py
  - impact: Faster response to security posture regressions before hard failure thresholds trigger.
  - risk_class: `R2`
  - notes: Add trend signal with severity tags (`warn`, `drift`, `critical`) in `docs/reports/scorecard_threshold_audit.json`.

- `WB-RS-049` Attestation Auth Source Redaction Contract
  - repo_fit: Current attestation checks expose token presence and command paths, requiring stronger privacy contracts in logs.
  - source: scripts/verify_attestations.py
  - impact: Lower audit risk and more consistent incident diagnostics without secret leakage.
  - risk_class: `R1`
  - notes: Add explicit redaction policy for token source fields in JSON/console output.

- `WB-RS-050` Merge-Queue Readiness Gate for Private Repo Runs
  - repo_fit: Workbench may run with `private` policy while merge_queue and attestation pathways diverge.
  - source: .github/workflows/verify-nightly-attestations.yml and https://docs.github.com/actions/learn-github-actions/understanding-github-actions#workflow-run-events
  - impact: Prevents CI assumptions that silently fail where attestations are skipped by policy mode.
  - risk_class: `R2`
  - notes: Add explicit branch in workflow triggers and docs path for private/public parity.

- `WB-RS-051` Deterministic Report Artifact Headers
  - repo_fit: Handoff and script outputs are used in downstream parsers; header variance causes brittle consumers.
  - source: docs/OPERATIONS.md and scripts/run_quality_gates.py
  - impact: Improved parser compatibility and reduced human parsing effort during triage.
  - risk_class: `R1`
  - notes: Add fixed header schema for `*.md` and `*.json` reports.

- `WB-RS-052` Workflow-Step Metadata Envelope
  - repo_fit: Operators need context for why a specific job failed without opening all logs.
  - source: docs/OPERATIONS.md and scripts/mcp_smoke.py
  - impact: Faster root-cause context from one compact envelope in summaries and artifacts.
  - risk_class: `R0`
  - notes: Add per-step metadata fields (`step`, `owner`, `expected_duration`, `last_success`) to workflow artifacts.

- `WB-RS-053` Atlas Preflight Campaign Command
  - repo_fit: `Workbench` roadmap requires campaign preflight before starts; no single preflight script exists yet.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and scripts/run_quality_gates.py
  - impact: Fewer broken campaign launches and lower red-to-green recovery load by validating git/state/run prerequisites first.
  - risk_class: `R1`
  - notes: Implement `scripts/run_preflight_campaign.sh` that emits `docs/reports/campaigns/<campaign>/preflight.json` with terminal codes.

- `WB-RS-054` Hermes Approval Packet Template
  - repo_fit: Pre-approved campaign execution currently depends on ad-hoc operator notes; repository needs deterministic handoff packets.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and docs/OPERATIONS.md
  - impact: Reduced ambiguity for human approvals and clearer lane ownership handoffs.
  - risk_class: `R1`
  - notes: Add `docs/WORKBENCH_APPROVAL_PACKET_TEMPLATE.md` with required fields (`lane_owner`, `risk_budget`, `rollback`, `terminal_expectation`).

- `WB-RS-055` Cronos Outcome Recorder Contract
  - repo_fit: Phase 4 explicitly requires terminal classes (`complete`, `hard_block`, `cancelled`) and replay consistency.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and scripts/run_quality_gates.py
  - impact: Enables deterministic replay and machine parsing of campaign terminal state.
  - risk_class: `R1`
  - notes: Add `scripts/record_campaign_outcome.py` to persist `terminal_class` + action checklist into campaign artifact directories.

- `WB-RS-056` Phoenix Lane-Conflict Auto-Tagger
  - repo_fit: `runbook` and `lane topology` define file-lock rules but are enforced manually.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and docs/OPERATIONS.md
  - impact: Prevents overlapping lane work and unplanned merge conflicts from same path set.
  - risk_class: `R2`
  - notes: Pre-commit/PR bot checks to suggest lane labels based on changed paths before queueing a campaign.

- `WB-RS-057` Aegis Repro Command Replay
  - repo_fit: Operators need one-click reproducibility from failure logs during incident response.
  - source: scripts/run_quality_gates.py and docs/OPERATIONS.md
  - impact: Faster recovery because failed commands can be replayed exactly with captured env and flags.
  - risk_class: `R1`
  - notes: Emit `docs/reports/campaigns/<id>/replay.sh` from gate outputs whenever failures are detected.

- `WB-RS-058` Norn Eval Drift Gate
  - repo_fit: `eval_report.py` exists but scenario drops are only observed post-merge via baseline threshold.
  - source: scripts/eval_report.py and docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Earlier detection of silent eval regression on campaign-boundary changes.
  - risk_class: `R1`
  - notes: Add per-scenario delta report and warning level (`warn`/`drift`) when scores degrade against baseline.

- `WB-RS-059` Athena Workflow Permission Baseline Guard
  - repo_fit: `ci.yml` and `size-check.yml` currently rely on default workflow permissions and can inherit over-broad token scope.
  - source: .github/workflows/ci.yml and https://docs.github.com/en/actions/learn-github-actions/security-for-github-actions/security-hardening-for-github-actions
  - impact: Reduced blast radius and explicit least-privilege documentation for each job.
  - risk_class: `R1`
  - notes: Add workflow/job-level `permissions` blocks plus a lint check that fails missing permission declarations.

- `WB-RS-060` Sisyphus Queue Drain Signal
  - repo_fit: long agent waves need signal on stalled queue conditions and backoff windows.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and scripts/validate_workspace_index.py
  - impact: Faster stabilization decisions when failure rates or pending checks drift beyond safe lane throughput.
  - risk_class: `R2`
  - notes: Add scheduled reporter that tracks queue length/pending/age of stalled handoffs and emits runbook-ready alerts.

- `WB-RS-061` Atlas Private-Provenance Fallback
  - repo_fit: `Verify Nightly Attestations` is skipped on private repos; current fallback posture is informal.
  - source: .github/workflows/verify-nightly-attestations.yml and docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Restores provenance continuity for private repos and keeps operators from losing trust windows.
  - risk_class: `R2`
  - notes: Add internal provenance fallback artifact (manifest+checksum bundle) when attestation API is unavailable.

- `WB-RS-062` Hermes Utility Standard (uv + ruff + trivy)
  - repo_fit: Workbench operator UX benefits from deterministic local environment setup and faster security scan feedback.
  - source: docs/reports/workbench_gap_assessment_2026-02-15.md and https://github.com/astral-sh/uv, https://github.com/astral-sh/ruff, https://github.com/aquasecurity/trivy
  - impact: More reproducible gates and stronger utility stack for local/CI diagnostics under parallel runs.
  - risk_class: `R2`
  - notes: Add optional CI/local bootstrap profile using `uv` for deps, `ruff` lint pass, and `trivy fs` audit report output in docs/reports.

- `WB-RS-063` Hecate Campaign Artifact Quarantine
  - repo_fit: Campaign outcome artifacts currently land in shared report paths and can be overwritten across concurrent waves.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and docs/OPERATIONS.md
  - impact: Reduces recovery ambiguity and keeps per-campaign evidence isolated under `docs/reports/campaigns/<campaign>/`.
  - risk_class: `R1`
  - notes: Implement campaign artifact root with timestamped run IDs and TTL tags before each run output.

- `WB-RS-064` Minerva Runbook Contract Linter
  - repo_fit: Runbook commands and workflow profiles are human-maintained with no machine validation.
  - source: docs/OPERATIONS.md and scripts/verify_attestations.py
  - impact: Lower onboarding friction and fewer operator mistakes from stale or malformed run instructions.
  - risk_class: `R2`
  - notes: Add validator that checks required command/env blocks and references against actual repo files.

- `WB-RS-065` Icarus Campaign Replay Envelope
  - repo_fit: Incident response currently asks operators to reconstruct exact command context manually from logs.
  - source: docs/OPERATIONS.md and scripts/run_quality_gates.py
  - impact: Faster root-cause recovery and easier handoff because replay inputs are deterministic.
  - risk_class: `R1`
  - notes: Persist `argv`, working directory, and relevant env key set in handoff artifacts before every gate failure.

- `WB-RS-066` Bifrost Diff Classifier for Failed Campaigns
  - repo_fit: Current failures lack a standard failure-class taxonomy tied to lane ownership.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and scripts/run_quality_gates.py
  - impact: Faster triage routing by classifying failures into predefined operational classes.
  - risk_class: `R1`
  - notes: Add JSON failure class map (`infra`, `workflow`, `plugin`, `attestation`, `policy`) and expose it in reports.

- `WB-RS-067` Prometheus PR Queue Signal
  - repo_fit: Lane throughput and PR backlog are managed manually in weekly wave planning.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and docs/README.md
  - impact: Prevents overloaded campaigns by surfacing queue-pressure metrics.
  - risk_class: `R2`
  - notes: Emit weekly `pending_checks`/`age_hours`/`active_campaigns` metrics into `docs/reports/campaigns/queue_health.md`.

- `WB-RS-068` Nidhogg Path Conflict Pre-merge Check
  - repo_fit: Path-lock policy is documented but not automatically cross-checked before execution.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and .github/workflows/ci.yml
  - impact: Fewer avoidable merge conflicts and rework during high parallel campaigns.
  - risk_class: `R2`
  - notes: Add script that compares changed paths against declared campaign path locks and emits blocking reasons.

- `WB-RS-069` Valkyrie Provenance Mirror for Public+Private Policy
  - repo_fit: Provenance differs by repository privacy mode and can be unintuitive during private runs.
  - source: .github/workflows/verify-nightly-attestations.yml and docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Improves continuity of trust evidence irrespective of attestation mode.
  - risk_class: `R2`
  - notes: Add deterministic manifest+checksum mirror artifact written in all modes with policy reason.

- `WB-RS-070` Oathkeeper Manual Override Fence
  - repo_fit: Some workflows can be run with `workflow_dispatch` even when required preconditions are missing.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onworkflow_dispatch
  - impact: Lower risk of unguarded manual runs and missing attestations/policy context.
  - risk_class: `R1`
  - notes: Add explicit `inputs` checks and fail-fast validation path in manual workflow entry points.

- `WB-RS-071` Hades Plugin Regression Diff Capsule
  - repo_fit: Plugin migration lane changes are high risk and require fast detection of contract reversals.
  - source: scripts/check_plugin_contracts.py and docs/PLUGIN_CONTRACT_OWNERSHIP.md
  - impact: Early warning when a plugin accidentally removes exports or required command surfaces.
  - risk_class: `R1`
  - notes: Store per-run plugin contract snapshots and produce a diff summary artifact in `docs/reports/plugin_contract_audit.json`.

- `WB-RS-072` Athena Release Boundary Dry-Run
  - repo_fit: Roadmap phases depend on weekly waves but has no pre-release simulation checkpoint.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and .github/workflows/policy-review.yml
  - impact: Lower release breakage risk by running full campaign packet through synthetic `workflow_dispatch` prechecks.
  - risk_class: `R2`
  - notes: Add a synthetic "wave release rehearsal" that runs preflight + gate + eval checks without merge rights.

- `WB-RS-073` Ananke Campaign Metadata Ledger
  - repo_fit: Campaign handoff packets currently lack canonical metadata fields for longitudinal audit.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md and scripts/verify_attestations.py
  - impact: Better cross-wave traceability for long-run campaigns and simpler post-incident investigation.
  - risk_class: `R1`
  - notes: Add a single `campaign_ledger.json` with `campaign_id`, `owner`, `start_utc`, `target_files`, `expected_outcomes`.

- `WB-RS-074` Ares Manual Escalation Channel
  - repo_fit: Incident playbooks mention escalation but no standardized channel contract exists for repeated blockers.
  - source: docs/OPERATIONS.md and docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Reduced MTTR when waves stall on the same policy or infra issue.
  - risk_class: `R2`
  - notes: Add operator escalation manifest with owner rotation and default response windows for blocked lanes.

- `WB-RS-075` Mnemosyne Handoff Memory Index
  - repo_fit: Historical failures and handoff packets are fragmented across `docs/reports/*` and scripts.
  - source: docs/reports/workspace_index_audit.md and docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Faster recurring-issue detection and less repeated triage.
  - risk_class: `R1`
  - notes: Maintain `docs/reports/campaigns/index.json` cataloging outcomes by terminal class and failure code.

- `WB-RS-076` Janus Review Fence for Private Repository Mode
  - repo_fit: Workflow behavior diverges when `github.event.repository.private == false` and in private mode.
  - source: .github/workflows/verify-nightly-attestations.yml and https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
  - impact: Reduces silent mode drift by forcing explicit policy acknowledgments before merge.
  - risk_class: `R2`
  - notes: Add a mode-fence step requiring operator confirmation + reason before allowing mode-dependent bypasses.

- `WB-RS-077` Aegir Artifact Lineage Graph
  - repo_fit: Handoffs rely on artifacts but lineage links are implicit.
  - source: docs/OPERATIONS.md and scripts/verify_attestations.py
  - impact: Faster provenance debugging when a failure ties to an earlier campaign output.
  - risk_class: `R1`
  - notes: Add parent artifact references in each packet (`upstream_run_id`, `upstream_artifact`) for one-hop lineage.

- `WB-RS-078` Hephaestus Command Smoke Matrix
  - repo_fit: Operators use many entrypoint commands but compatibility of combinations is not validated.
  - source: docs/OPERATIONS.md and scripts/test_changed.py
  - impact: Earlier failure discovery when campaign mode combos are broken.
  - risk_class: `R2`
  - notes: Add CI job that runs a matrix of canonical command combos (`run_quality_gates`, `eval_report`, `validate_workspace_index`).

- `WB-RS-079` Atlas Environment Profile Drift Watch
  - repo_fit: `MCP_AUTH_*` and `GH_*` env assumptions drive auth-sensitive campaigns.
  - source: plugins/mcp_auth.py, scripts/mcp_smoke.py, scripts/verify_attestations.py
  - impact: Lower false failures by surfacing env-profile drift before heavy checks run.
  - risk_class: `R1`
  - notes: Compare loaded env keys against expected profile in a profile manifest (`docs/research/env_profile.json`) at preflight.

- `WB-RS-080` Helios Workflow Runtime Budget Ledger
  - repo_fit: Campaigns can fail late from over-run jobs and hidden queue starvation.
  - source: .github/workflows/*.yml and docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Better planning of lane concurrency and reduced timeout-induced failures.
  - notes: Add runtime budget file with historical durations per workflow/job and cap thresholds for auto-staging slow campaigns.
  - risk_class: `R2`

## Pass 1 (upgrade top candidates)

### `WB-RS-013` Concurrency Lease for Critical Workflows
- problem: Workflow lane overlap causes duplicate work and queue contention during high parallel activity.
- impact: Reduced CI queue pressure and cleaner run ordering with fewer flaky overlap failures.
- verify: Push the same lane changes from multiple agents; confirm only one in-flight lease per branch for constrained workflows.
- rollback: Remove `concurrency` keys and restore direct workflow triggers.
- risk_class: `R0`

### `WB-RS-025` Structured Runbook Command Registry
- problem: Operators repeatedly guess command variants across lanes, slowing recovery.
- impact: Faster onboarding and lower chance of running wrong-risk command under pressure.
- verify: Command exists as generated registry and includes required risk/rollback/owner metadata.
- rollback: Keep registry generation behind optional script flag and preserve source `docs/OPERATIONS.md`.
- risk_class: `R1`

### `WB-RS-011` Workflow Problem-Matcher Baseline
- problem: Failures are often only text in logs, hard to triage in PR checks.
- impact: Direct file/line annotations shorten diagnosis loops.
- verify: Trigger a controlled failure and verify actionable annotation appears in check logs.
- rollback: Disable problem matcher upload in workflows without removing generated matcher definitions.
- risk_class: `R0`

### `WB-RS-015` Argus Artifact Fetcher Command
- problem: Recovery often pauses while humans manually gather evidence across multiple report paths.
- impact: Single-command artifact pull reduces mean time to context recovery.
- verify: Run helper on a known workflow run and fetch `eval_report` + `attestation` artifacts reliably.
- rollback: Remove command from docs and keep manual recovery steps.
- risk_class: `R0`

### `WB-RS-017` MCP Auth Source Normalization for Verify Scripts
- problem: MCP auth token/key source behavior is inconsistent across modules and profiles.
- impact: More predictable connectivity checks and lower cross-env confusion.
- verify: Test matrix across `MCP_SERVER_URL`, token/key variants, and output should show normalized effective source.
- rollback: Keep compatibility aliases for one release and log deprecation warnings for legacy names.
- risk_class: `R1`

### `WB-RS-018` GH CLI Dependency and Auth Guard
- problem: `gh` failures or missing token are discovered after long script execution.
- impact: Earlier fail-fast prevents useless runs and reduces debug loop time.
- verify: Simulate missing GH CLI and verify script exits with source-guided instruction before attestation steps.
- rollback: Guard remains permissive with warning-only mode.
- risk_class: `R0`

## Pass 2 (handoff quality)

## Top 5 candidates (ranked by actionability)

1. `WB-RS-013` Concurrency Lease for Critical Workflows
   - reason: Low effort, high stability gain, directly reduces run duplication in high concurrency.

2. `WB-RS-011` Workflow Problem-Matcher Baseline
   - reason: Fast to add, immediate diagnostic quality improvement with low operational risk.

3. `WB-RS-015` Argus Artifact Fetcher Command
   - reason: Concrete productivity gain in recovery windows with minimal implementation overhead.

4. `WB-RS-053` Atlas Preflight Campaign Command
   - reason: Directly blocks bad campaign starts and is reusable across all lanes.

5. `WB-RS-025` Structured Runbook Command Registry
   - reason: Improves operator UX and reduces command variance during handoff windows.

## Deferred / research_only

- `WB-RS-024` Live Lane and Lock Overlay (command-mode)
  - status: `deferred/research_only`
  - reason: Requires dedicated command/CI reporting model and ownership for the lane registry.

- `WB-RS-027` Dependency Health Trend Watch
  - status: `deferred/research_only`
  - reason: Useful but needs scoring policy and threshold policy before implementation.

- `WB-RS-026` Scope-Bound Retry Budget in Gate Scripts
  - status: `deferred/research_only`
  - reason: Broad implementation touches all networked checks; likely higher effort than current phase supports.

- `WB-RS-009` Idempotency-Key Policy for Side-Effecting Actions
  - status: `deferred/research_only`
  - reason: Good long-term control, but needs end-to-end idempotency semantics across affected scripts.

## Checkpoint 2026-02-15T00:00:00Z
- completed: Pass0 captured 80 actionable suggestions, Pass1 upgraded top 6 with problem/impact/verify/rollback, Pass2 ranked top5 + deferred set.
- current: waiting for next roadmap draft cycle to map top5 and deferred items into campaign packets.
- next: map top5 and deferred items into campaign packets for one-year roadmap waves.
- files changed: `docs/research/SUGGESTIONS_BIN.md`
- blockers: none

## Pass 0 (composition, diagnostics, and promotion handoff extension)

- `WB-COMP-001` Compose-to-Deploy Graph Compiler
  - repo_fit: `Workbench` already has `NodeGraph` and `WorkflowDefinition`, but no persistence path from graph to execution artifact.
  - source: plugins/custom_nodes.py, plugins/workflow_engine.py, https://json-schema.org/
  - impact: Deterministic `graph.json`/`graph.yaml` exports allow review and replay of operator-approved plans.
  - risk_class: `R1`
  - notes: Add `scripts/compile_graph.py` and a `json`/`yaml` schema contract for compile output.

- `WB-COMP-002` Deterministic Graph Decompiler for Handoff Replay
  - repo_fit: Workbench already captures handoff artifacts but not graph source snapshots.
  - source: docs/research/SUGGESTIONS_BIN.md, docs/reports/workspace_index_audit.md
  - impact: Any review-approved promotion packet can be reconstructed and rerun identically.
  - risk_class: `R1`
  - notes: Add `scripts/decompile_graph.py` that emits normalized `execution_plan.json` from stored graph artifacts.

- `WB-COMP-003` Node-level Failure Taxonomy for Workflow Engine
  - repo_fit: `WorkflowExecutor` currently returns `failed_step` and generic error strings; routing handoffs is coarse.
  - source: plugins/workflow_engine.py, docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Lane assignment and escalation become faster when failures are tagged by node class (`io`, `auth`, `policy`, `provisioning`).
  - risk_class: `R1`
  - notes: Extend status payload with `failed_node_id`, `failure_code`, `failure_scope`, and `first_error`.

- `WB-COMP-004` Campaign Approval Packet Schema (Promote/Reject)
  - repo_fit: Long-running multi-agent runs currently rely on ad-hoc operator notes for approval decisions.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md, docs/OPERATIONS.md
  - impact: Stable `docs/WORKBENCH_APPROVAL_PACKET_TEMPLATE.md` fields reduce variance in human-in-loop promotion decisions.
  - risk_class: `R1`
  - notes: Add explicit `reviewer`, `decision`, `conditions`, `rollback`, `terminal_expectation` fields.

- `WB-COMP-005` Graph Diff Against Baseline at Handoff
  - repo_fit: Existing operations show failure snapshots but no first-class plan diff to compare against baseline.
  - source: scripts/validate_workspace_index.py, docs/WORKBENCH_LONG_TERM_ROADMAP.md
  - impact: Operators can approve/reject by seeing semantic diff (added/removed/modified nodes) instead of reading full log dumps.
  - risk_class: `R2`
  - notes: Add `graph_diff` output alongside campaign outcome, with stable node IDs and edge change summary.

- `WB-COMP-006` Preflight Graph Integrity Gate
  - repo_fit: Roadmap requires campaign preflight but scripts are missing, and graph compile/deploy adds a new failure mode.
  - source: docs/WORKBENCH_LONG_TERM_ROADMAP.md, plugins/custom_nodes.py
  - impact: Bad graphs (cycles, missing ports, unsupported handlers) fail before gate execution.
  - risk_class: `R1`
  - notes: Implement `scripts/run_preflight_campaign.sh` extension path `--mode graph|workflow|promotion`.

- `WB-COMP-007` Graph Execution Replay Trail
  - repo_fit: Recovery depends on manual reconstruction; replay reliability is not first-class.
  - source: plugins/workflow_engine.py, docs/OPERATIONS.md
  - impact: Operators can rerun exactly from last green checkpoint with one command and same env/context.
  - risk_class: `R1`
  - notes: Persist `argv`, handler map hash, and environment fingerprint in a per-campaign `replay.json`.

- `WB-COMP-008` Concurrency Lease for Graph-bound Promotion Lanes
  - repo_fit: `.github/workflows/ci.yml` and `nightly-evals.yml` currently have no lease keys, but 8+ agent waves target same lane surfaces.
  - source: .github/workflows/ci.yml, .github/workflows/nightly-evals.yml, https://docs.github.com/actions/using-jobs/using-concurrency-in-github-actions
  - impact: Prevents duplicate/overlapping approval or compile campaigns against same protected surfaces.
  - risk_class: `R0`
  - notes: Add branch+purpose concurrency groups for campaign-related workflow jobs.

- `WB-COMP-009` Handoff Packet Lineage Graph
  - repo_fit: ARTIFACT_STORAGE_CONVENTIONS defines envelopes but lacks explicit lineage linkage.
  - source: docs/repo-alignment/ARTIFACT_STORAGE_CONVENTIONS.md, docs/OPERATIONS.md
  - impact: One-hop provenance can be followed automatically across failed/approved/replayed campaigns.
  - risk_class: `R1`
  - notes: Add `upstream_packet_id` and `parent_run_id` links to all campaign packets.

- `WB-COMP-010` Promotion Timeline Visualization
  - repo_fit: Operators need quick comprehension of sequence + stall points during live runs.
  - source: plugins/workflow_engine.py, tests/test_phase0_smoke.py
  - impact: Better operator situational awareness via timeline and dependency path at inspection time.
  - risk_class: `R2`
  - notes: Emit ordered node run timeline JSON and optional Mermaid/Gantt summary in handoff artifacts.

- `WB-COMP-011` Interop Promotion Gate Contracts
  - repo_fit: `protocols/AGENT_INTEROP_V1.md` references schemas that are absent and likely block reliable cross-repo packeting.
  - source: protocols/AGENT_INTEROP_V1.md, docs/repo-alignment/ARTIFACT_STORAGE_CONVENTIONS.md
  - impact: Promotion handoff to dependent repos becomes machine-parsable and audit-safe.
  - risk_class: `R2`
  - notes: Add protocol schema directory or explicit compatibility policy that states schema-free mode.

- `WB-COMP-012` Human Pause/Resume Controls for Long Campaigns
  - repo_fit: `WorkflowExecutor` already supports pause/resume, but operators lack lane-safe manual control hooks in command flow.
  - source: plugins/workflow_engine.py, docs/OPERATIONS.md
  - impact: Human-in-loop control is explicit for risky production-like campaigns with controlled intervention points.
  - risk_class: `R1`
  - notes: Add `scripts/campaign_control.py` (`pause`, `resume`, `cancel`, `checkpoint`) tied to campaign packet IDs.

## Pass 1 (compose/deploy top candidates)

### `WB-COMP-008` Concurrency Lease for Graph-bound Promotion Lanes
- problem: Concurrent campaign jobs currently can run simultaneously and collide on shared promotion surfaces, especially with 8+ agents.
- impact: Deterministic merge/approval order and fewer race-related rollback incidents.
- verify: Simulate concurrent campaign triggers in two lanes and confirm one workflow instance is canceled, deferred, or queued.
- rollback: Remove concurrency groups and revert to direct job scheduling.
- risk_class: `R0`

### `WB-COMP-001` Compose-to-Deploy Graph Compiler
- problem: No canonical compile step exists to materialize graph intent into deterministic artifacts.
- impact: Operators can approve/replay exact operator-directed plans, reducing ambiguity.
- verify: Create graph input, run compile, then verify decompile round trip outputs a semantically equivalent graph.
- rollback: Hide compiler behind fallback path and continue using current manual execution.
- risk_class: `R1`

### `WB-COMP-004` Campaign Approval Packet Schema (Promote/Reject)
- problem: Promotion approvals currently require manual interpretation of mixed artifacts and ad-hoc notes.
- impact: Faster, auditable go/no-go decisions with minimal variance across lanes.
- verify: Force a dry-run lane to produce an approval packet and validate against schema with schema mismatch rejection.
- rollback: Keep schema optional until first stable cycle and allow legacy packet format for one release.
- risk_class: `R1`

### `WB-COMP-006` Preflight Graph Integrity Gate
- problem: Existing campaign start checks miss graph-specific failure modes (cycles, missing handlers, unreachable nodes).
- impact: Reduced false promotions and fewer expensive rerun cycles.
- verify: Submit invalid graph fixture and confirm preflight fails with stable machine-readable code.
- rollback: Restrict preflight to warning-only mode while pipeline observes behavior.
- risk_class: `R1`

### `WB-COMP-003` Node-level Failure Taxonomy for Workflow Engine
- problem: Current failure output is generic and insufficient for lane-specific handoff.
- impact: Faster human routing and lower time-to-resolution during failures.
- verify: Inject failure at node/action boundary and assert `failed_node_id` + `failure_code` appear in output report.
- rollback: Keep both old and new failure formats in payload and deprecate old format later.
- risk_class: `R1`

### `WB-COMP-007` Graph Execution Replay Trail
- problem: Recovery today relies on recreated mental models and incomplete logs.
- impact: Deterministic replay reduces retry ambiguity and supports controlled recovery.
- verify: Capture one failed run, regenerate `replay.json`, and run replay command from that record successfully.
- rollback: Store replay trail only when opt-in flag is set, keeping normal run shape unchanged.
- risk_class: `R2`

## Pass 2 (compose/deploy handoff quality)

## Top 5 candidates (ranked by actionability)

1. `WB-COMP-008` Concurrency Lease for Graph-bound Promotion Lanes
   - reason: Low-code change with high operational payoff under 8+ parallel operators.

2. `WB-COMP-001` Compose-to-Deploy Graph Compiler
   - reason: Directly fills the missing compile pathway for inspectable, replayable operator plans.

3. `WB-COMP-004` Campaign Approval Packet Schema (Promote/Reject)
   - reason: Highest impact on human-in-loop determinism with clear downstream automation benefit.

4. `WB-COMP-006` Preflight Graph Integrity Gate
   - reason: Prevents invalid graphs from entering campaign execution with modest implementation surface.

5. `WB-COMP-007` Graph Execution Replay Trail
   - reason: Improves reliability during handoff/recovery cycles with manageable complexity.

## Deferred / research_only

- `WB-COMP-010` Promotion Timeline Visualization
  - status: `deferred/research_only`
  - reason: Requires choosing a timeline rendering format and retention policy before implementation.

- `WB-COMP-011` Interop Promotion Gate Contracts
  - status: `deferred/research_only`
  - reason: Depends on AGENT_INTEROP schema decision and cross-repo protocol implementation.

- `WB-COMP-012` Human Pause/Resume Controls for Long Campaigns
  - status: `deferred/research_only`
  - reason: Needs explicit authority model and command ACL in operator CLI before production.

## Checkpoint 2026-02-15T00:00:00Z
- completed: Added 12 composition/diagnostics/promotion suggestions, upgraded top 6 composition candidates, ranked composition top 5 + 3 deferred.
- current: mapping composition top candidates into Workbench one-year pre-approved roadmap packets.
- next: synthesize thin implementation slice from top 5 and align with operator runbook.
- files changed: `docs/research/SUGGESTIONS_BIN.md`
- blockers: AGENT_INTEROP_V1 schema references are declared but absent in repository.
