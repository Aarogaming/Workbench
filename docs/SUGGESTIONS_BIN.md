# Workbench Suggestions Bin

Date created: 2026-02-15  
Purpose: Store research-backed implementation suggestions between roadmap drafting cycles.

## How to use this bin

1. Add new items as `new` with source links and local touchpoints.
2. Review weekly and move to `approved` or `rejected`.
3. Pull `approved` items into campaign packets and roadmap updates.

Status vocabulary:

1. `new`
2. `reviewing`
3. `approved`
4. `scheduled`
5. `implemented`
6. `rejected`

Scoring:

1. Impact: `1` low to `5` high.
2. Effort: `1` low to `5` high.
3. Confidence: `1` low to `5` high.

## Intake batch: 2026-02-15

| ID | Suggestion | Why it fits Workbench | Status | Impact | Effort | Confidence |
|---|---|---|---|---:|---:|---:|
| `WB-SUG-001` | Add workflow/job `concurrency` controls to CI/nightly flows | Workbench runs frequent pushes and manual dispatches; prevents redundant in-flight runs with 8+ agents. | `new` | 5 | 2 | 5 |
| `WB-SUG-002` | Enable `actions/setup-python` pip caching in CI/nightly | Current workflows reinstall deps every run; setup-python cache can cut repeated install cost. | `new` | 4 | 2 | 4 |
| `WB-SUG-003` | Introduce `uv` lock-based dependency workflow | Improves reproducibility and speed for local + CI Python setup. | `new` | 4 | 3 | 4 |
| `WB-SUG-004` | Add `ruff` lint/format gate | Fast linting/formatting for large plugin surface; can reduce style noise and quick-fix issues. | `new` | 3 | 2 | 4 |
| `WB-SUG-005` | Add targeted `mypy` checks for critical plugin modules | Better contract safety around `workflow_engine`, `mcp_auth`, `integration_engine` without full-repo strict typing day 1. | `new` | 4 | 3 | 4 |
| `WB-SUG-006` | Add `pytest-xdist` test sharding in CI | Faster test feedback as suite grows beyond current 55 tests. | `new` | 3 | 2 | 4 |
| `WB-SUG-007` | Add branch coverage reporting and thresholds | Increases quality signal beyond pass/fail by tracking branch-level behavior. | `new` | 4 | 3 | 4 |
| `WB-SUG-008` | Add `pip-audit` scheduled and PR checks | Direct dependency vulnerability signal; supports JSON/SBOM outputs and GitHub Action. | `new` | 4 | 2 | 5 |
| `WB-SUG-009` | Add Bandit security scan with SARIF upload | Surfaces Python security findings in code scanning UI and keeps triage centralized. | `new` | 4 | 3 | 4 |
| `WB-SUG-010` | Add private-repo provenance fallback using offline attestation verification | Current attestation workflow skips private repos; define internal verify path for parity. | `new` | 5 | 3 | 4 |
| `WB-SUG-011` | Add OpenTelemetry traces/metrics around campaign loop and gates | Supports long unattended runs with observability and failure forensics. | `new` | 4 | 3 | 4 |
| `WB-SUG-012` | Expand reusable workflow strategy for org-wide sharing | Workbench already has reusable workflows; this scales policy consistency across repos. | `new` | 3 | 2 | 4 |

## Thematic research batch: 2026-02-15 (Workbench-inspired)

These are intentionally exploratory and theme-inspired from guild/workbench/forge/mission-control patterns; keep as backlog candidates until your uniform standard is ready.

| ID | Suggestion | Why it fits Workbench | Status | Impact | Effort | Confidence |
|---|---|---|---|---:|---:|---:|
| `WB-SUG-013` | Introduce a guild-style agent maturity ladder (`apprentice`, `journeyman`, `master`) for campaign permissions | Gives explicit progression gates for 8+ parallel agents and reduces high-risk task assignment drift. | `new` | 4 | 2 | 4 |
| `WB-SUG-014` | Add a Hanseatic `kontor` pattern for cross-repo liaison nodes | Encapsulates cross-repo handoff logic into explicit liaison artifacts instead of ad hoc coordination. | `new` | 4 | 3 | 3 |
| `WB-SUG-015` | Define an `Arsenal wave` merge train model for weekly campaign integration | Venetian Arsenal-style staged assembly maps well to weekly parallel wave stabilization. | `new` | 5 | 3 | 4 |
| `WB-SUG-016` | Add a `Forge` pre-merge gate bundle (contracts + security + compile + tests) | Hephaestus/forge motif maps to a single hardened quality checkpoint before merge. | `new` | 5 | 2 | 5 |
| `WB-SUG-017` | Add `Argonaut expedition` templates for cross-functional campaign packets | Expedition framing helps enforce specialist role assignments and explicit mission scope. | `new` | 3 | 2 | 4 |
| `WB-SUG-018` | Add `Raven pair` telemetry model (`Thought` live signals + `Memory` durable summaries) | Dual-channel telemetry supports long unattended runs and easier post-run reconstruction. | `new` | 4 | 3 | 4 |
| `WB-SUG-019` | Add NIMS/ICS-style incident command overlays for high-concurrency run windows | Standardized command hierarchy and span-of-control improves parallel run safety and escalation clarity. | `new` | 5 | 3 | 4 |
| `WB-SUG-020` | Add `Mission Control` go/no-go checklist and console roles for release waves | NASA-style console ownership sharpens release accountability and last-mile triage. | `new` | 4 | 2 | 4 |
| `WB-SUG-021` | Add a Toyota `andon` stop-the-line policy for gate instability | Immediate containment prevents cascading failures during rapid agent concurrency. | `new` | 5 | 2 | 5 |
| `WB-SUG-022` | Add SRE-style error budgets for autonomous campaign reliability | Converts stability goals into measurable throttle rules for campaign throughput. | `new` | 5 | 3 | 5 |

## Operations and reliability batch: 2026-02-15

| ID | Suggestion | Why it fits Workbench | Status | Impact | Effort | Confidence |
|---|---|---|---|---:|---:|---:|
| `WB-SUG-023` | Add branch-aware workflow `concurrency` groups and cancellation policy | High parallel push rates from 8+ agents can waste CI minutes and produce stale signal without deterministic cancellation. | `implemented` | 5 | 2 | 5 |
| `WB-SUG-024` | Enforce `gh` minimum version gate for attestation verification steps | Prevents known attestation verify false-success behavior in older GitHub CLI versions. | `implemented` | 5 | 1 | 5 |
| `WB-SUG-025` | Harden attestation verification identity checks (`--repo/--owner` + `--signer-workflow` + explicit predicate) | Tightens provenance verification policy and avoids weak/default identity assumptions. | `implemented` | 5 | 2 | 5 |
| `WB-SUG-026` | Add offline attestation bundle verification playbook and workflow path | Gives private/offline resiliency and post-run auditability when online verification is constrained. | `implemented` | 4 | 3 | 4 |
| `WB-SUG-027` | Add artifact digest capture and integrity cross-check report in pipelines | Artifact digest outputs and validation warnings already exist; capturing them as evidence improves forensic confidence. | `implemented` | 4 | 2 | 4 |
| `WB-SUG-028` | Add artifact retention classes (`short`, `standard`, `forensic`) with explicit `retention-days` defaults | Reduces over-retention risk and storage sprawl while preserving required troubleshooting windows. | `implemented` | 4 | 2 | 5 |
| `WB-SUG-029` | Add explicit least-privilege `permissions` blocks in all workflows and evaluate with token-permission monitor | Workbench workflows should not depend on org/repo defaults; explicit minimal scopes reduce token blast radius. | `implemented` | 5 | 3 | 4 |
| `WB-SUG-030` | Map `docs/OPERATIONS.md` incident flow to NIST SP 800-61 Rev. 3 lifecycle checkpoints | Brings incident handling language and playbook sequencing to current NIST guidance baseline. | `implemented` | 4 | 2 | 4 |
| `WB-SUG-031` | Add SSDF control mapping (`SP 800-218`) for each quality gate script/workflow | Makes security control coverage auditable and supports compliance-minded roadmap planning. | `implemented` | 4 | 3 | 4 |
| `WB-SUG-032` | Add DORA + reliability scoreboard for weekly campaign waves | Provides objective throughput and stability metrics to tune campaign load and error budgets. | `implemented` | 5 | 3 | 4 |
| `WB-SUG-033` | Add Kanban WIP limits by lane for campaign board operations | Enforces sustainable pull-based flow and complements the 8+ agent parallel model. | `implemented` | 4 | 2 | 5 |
| `WB-SUG-034` | Add `Ariadne Thread` after-action template for campaign retrospectives | Myth-inspired framing for traceability: planned path, actual path, deviations, and recovery thread for next wave. | `implemented` | 3 | 1 | 4 |

## Process discipline batch: 2026-02-15

| ID | Suggestion | Why it fits Workbench | Status | Impact | Effort | Confidence |
|---|---|---|---|---:|---:|---:|
| `WB-SUG-035` | Add three-phase campaign checklist (`sign-in`, `time-out`, `sign-out`) with one responsible conductor per run | Structured phase checks improve handoff quality in high-concurrency execution windows. | `implemented` | 4 | 2 | 4 |
| `WB-SUG-036` | Add `start small` pilot rollout rule for new gates/workflows (one lane, then broaden) | Reduces blast radius while introducing new controls in an 8+ agent environment. | `implemented` | 4 | 1 | 5 |
| `WB-SUG-037` | Implement continuous monitoring loop for gate health and campaign risk signals | Moves from periodic checks to continuous risk awareness across active waves. | `implemented` | 5 | 3 | 4 |
| `WB-SUG-038` | Add blameless postmortem trigger policy and template in campaign artifacts | Improves learning velocity and reduces repeat failure patterns across lanes. | `implemented` | 5 | 2 | 5 |
| `WB-SUG-039` | Add `cursus publicus` relay model for long-run handoffs (`mutationes` quick relays, `mansiones` full checkpoints) | Clear relay/checkpoint distinctions can reduce context-loss during multi-agent baton passes. | `implemented` | 4 | 2 | 4 |
| `WB-SUG-040` | Add OpenAI background-mode webhook worker pattern for long campaign tasks | Supports robust async execution with retries, idempotency keys, and terminal-state handling. | `implemented` | 4 | 3 | 4 |
| `WB-SUG-041` | Add prompt-caching-aware campaign prompt design policy (`static prefix`, `prompt_cache_key`) | Can materially reduce token cost/latency for repeated orchestration prompts. | `implemented` | 4 | 2 | 4 |
| `WB-SUG-042` | Route low-priority evaluation workloads to flex processing where acceptable | Cost optimization for non-urgent eval jobs while preserving primary lane capacity. | `implemented` | 3 | 2 | 4 |

## Research sources

1. OpenAI function calling guide: https://platform.openai.com/docs/guides/function-calling
2. OpenAI background mode guide: https://platform.openai.com/docs/guides/background
3. GitHub Actions concurrency: https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
4. GitHub reusable workflows: https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
5. GitHub dependency caching: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
6. `actions/setup-python` caching behavior: https://github.com/actions/setup-python
7. Dependency review action config: https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/configuring-the-dependency-review-action
8. GitHub artifact attestations: https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
9. GitHub offline attestation verification: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/verifying-attestations-offline
10. `uv` docs: https://docs.astral.sh/uv/
11. `ruff` docs: https://docs.astral.sh/ruff
12. `mypy` getting started / existing codebase: https://mypy.readthedocs.io/en/stable/getting_started.html and https://mypy.readthedocs.io/en/stable/existing_code.html
13. `pytest-xdist` docs and limitations: https://pytest-xdist.readthedocs.io/
14. Coverage.py branch coverage: https://coverage.readthedocs.io/en/5.5/branch.html
15. `pip-audit`: https://github.com/pypa/pip-audit
16. Bandit: https://bandit.readthedocs.io/en/latest/
17. Bandit CI/CD: https://bandit.readthedocs.io/en/latest/ci-cd/index.html
18. SARIF upload guidance: https://docs.github.com/en/code-security/how-tos/scan-code-for-vulnerabilities/integrate-with-existing-tools/uploading-a-sarif-file-to-github
19. OpenTelemetry Python instrumentation: https://opentelemetry.io/docs/languages/python/instrumentation/
20. Guild history (Britannica): https://www.britannica.com/topic/guild-trade-association
21. Hanseatic League (Britannica): https://www.britannica.com/topic/Hanseatic-League
22. Arsenal of Venice (Britannica): https://www.britannica.com/place/Arsenal-district-Venice-Italy
23. Hephaestus (Britannica): https://www.britannica.com/topic/Hephaestus
24. Argonaut (Britannica): https://www.britannica.com/topic/Argonaut
25. Germanic mythology (Britannica): https://www.britannica.com/topic/Germanic-religion-and-mythology
26. FEMA NIMS: https://www.fema.gov/national-incident-management-system
27. NASA Mission Control: https://www.nasa.gov/centers-and-facilities/johnson/mission-control/
28. Toyota Production System: https://global.toyota/en/company/vision-and-philosophy/production-system/
29. SRE workbook (error budgets/SLO operations): https://sre.google/workbook/alerting-on-slos/
30. GitHub Actions concurrency: https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
31. GitHub CLI attestation verify manual: https://cli.github.com/manual/gh_attestation_verify
32. GitHub CLI advisory GHSA-fgw4-v983-mgp8: https://github.com/advisories/GHSA-fgw4-v983-mgp8
33. Artifact attestations docs (GitHub): https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
34. Artifact storage and digest validation docs: https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts
35. Artifact/log retention docs (org settings): https://docs.github.com/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization
36. GITHUB_TOKEN least-privilege docs: https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-guides/automatic-token-authentication
37. NIST SP 800-61 Rev. 3: https://csrc.nist.gov/pubs/sp/800/61/r3/final
38. NIST SP 800-218 SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
39. DORA metrics: https://dora.dev/guides/dora-metrics/
40. Kanban guide (WIP limits): https://kanban.university/kanban-guide/
41. U.S. Army TC 7-0.1 (AAR publication notice): https://www.army.mil/article/283214/tmd_publishes_training_circular_to_augment_fm_and_adp_7_0
42. Ariadne reference (Britannica): https://www.britannica.com/topic/Ariadne-Greek-mythology
43. WHO Safe Surgery FAQ: https://www.who.int/news-room/questions-and-answers/item/safe-surgery-saves-lives-frequently-asked-questions
44. WHO checklist implementation manual: https://iris.who.int/handle/10665/70046
45. NIST SP 800-137 Continuous Monitoring: https://csrc.nist.gov/pubs/sp/800/137/final
46. Google SRE postmortem culture: https://sre.google/sre-book/postmortem-culture/
47. Cursus publicus (Britannica): https://www.britannica.com/topic/cursus-publicus
48. OpenAI webhooks guide: https://platform.openai.com/docs/webhooks
49. OpenAI background mode: https://platform.openai.com/docs/guides/background
50. OpenAI prompt caching: https://platform.openai.com/docs/guides/prompt-caching/prompt-caching
51. OpenAI flex processing: https://platform.openai.com/docs/guides/flex-processing

## Next roadmap draft pull-in rule

Promote a suggestion into roadmap scope only if:

1. It remains relevant after one weekly review.
2. It has at least one clear Workbench touchpoint (script/workflow/plugin/doc).
3. Required gate and rollback implications are documented in the approval packet.

## Lightweight intake batch: 2026-02-15 (parallel-forge operations)

- Archival note: the original implemented merge/ruleset seed items (IDs 043 through 052) were rotated to `docs/research/SUGGESTIONS_BIN_ARCHIVE_2026-02-18.md` to keep active bin capacity at 100 while promoting new repo-specific recommendations.

- `WB-SUG-053` Add `Hephaestus Seal` pre-promotion policy: artifact must pass provenance verification before promotion.
  - repo_fit: Workbench identity/theme already uses forge metaphors; sealing artifacts before promotion is a concrete supply-chain control.
  - source: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
  - impact: Stronger assurance that promoted outputs come from trusted workflows.
  - risk_class: `R2`
  - notes: Name is thematic; control is strict attestation/provenance verification.
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-054` Add `Arsenal Dock` release lane: batch PRs for timed merge windows with precomputed compatibility checks.
  - repo_fit: Mirrors Workbench weekly wave cadence and reduces random merge timing contention during high parallelism.
  - source: https://www.britannica.com/place/Arsenal-district-Venice-Italy
  - impact: Fewer accidental integration collisions and clearer release rhythm.
  - risk_class: `R1`
  - notes: Implement as process + queue settings, not custom infrastructure.
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

## Lightweight intake batch: 2026-02-15 (merge/ruleset/deployment controls)

- `WB-SUG-055` Ensure every required CI workflow listens to both `pull_request` and `merge_group` for queue parity.
  - repo_fit: Workbench expects safe high-velocity merges; queue parity prevents a path where PR checks pass but merge-group checks are missing.
  - source: https://github.blog/changelog/2022-08-18-merge-group-webhook-event-and-github-actions-workflow-trigger and https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request-with-a-merge-queue?tool=webui
  - impact: More reliable merge-queue behavior and fewer surprise removals from queue.
  - risk_class: `R1`
  - status: `implemented` (`.github/workflows/ci.yml` and `.github/workflows/size-check.yml`)

- `WB-SUG-056` Add an always-run required-check sentinel to avoid skipped-but-required deadlocks.
  - repo_fit: Workbench uses path-scoped workflows; required checks can block forever if a required workflow is skipped by path/branch filters.
  - source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks and https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/skipping-workflow-runs
  - impact: Fewer blocked PRs caused by pending required checks.
  - risk_class: `R0`
  - status: `implemented` (`.github/workflows/required-check-sentinel.yml`)

- `WB-SUG-057` Set strict required status checks for `main` in high-concurrency waves.
  - repo_fit: Workbench’s 8+ agent pattern raises integration-conflict risk; strict checks validate against latest base before merge.
  - source: https://docs.github.com/enterprise/admin/guides/developer-workflow/about-protected-branches-and-required-status-checks
  - impact: Lower post-merge regression rate from stale branch test results.
  - risk_class: `R1`
  - status: `implemented` (local enforcement packet + gate in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` and `scripts/check_merge_ruleset_deployment_guardrails.py`; branch protection setting remains admin-managed)

- `WB-SUG-058` Require successful deployment to a `staging` environment before merge to protected branches.
  - repo_fit: Workbench already has nightly and CI artifacts; a deployment-success gate adds a real integration checkpoint before promotion.
  - source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - impact: Better release confidence and fewer failed promotions.
  - risk_class: `R2`
  - status: `implemented` (local policy contract in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`; environment rule remains admin-managed)

- `WB-SUG-059` Enforce environment required reviewers with prevent-self-review for promotion jobs.
  - repo_fit: Supports Workbench’s separation-of-duties goals for high-impact automation runs.
  - source: https://docs.github.com/en/enterprise-server%403.15/actions/reference/workflows-and-actions/deployments-and-environments and https://github.blog/changelog/2023-10-16-actions-prevent-self-reviews-for-secure-deployments-across-actions-environments/
  - impact: Stronger approval integrity on deployment/promotion workflows.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`; environment setting remains admin-managed)

- `WB-SUG-060` Enable ruleset-level required code-scanning results for protected branches.
  - repo_fit: Workbench is script/workflow heavy; code-scanning gates can catch security regressions before merge.
  - source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - impact: Earlier security defect interception in PR flow.
  - risk_class: `R2`
  - status: `implemented` (local policy + audit contract in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`; live ruleset setting remains admin-managed)

- `WB-SUG-061` Add ruleset path/file-size restrictions for high-risk locations and oversized artifacts.
  - repo_fit: Workbench manages automation scripts and artifacts; push-time restrictions reduce accidental control-plane edits and blob growth.
  - source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - impact: Cleaner history and lower accidental policy/script drift.
  - risk_class: `R1`
  - status: `implemented` (local policy + audit contract in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`; live ruleset setting remains admin-managed)

- `WB-SUG-062` Require linear history on protected branches and align merge method policy.
  - repo_fit: Workbench rollback and audit tasks benefit from simpler history traversal during campaign retros.
  - source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - impact: Easier rollback/debug and cleaner release forensics.
  - risk_class: `R1`
  - status: `implemented` (local policy + audit contract in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`; branch/ruleset setting remains admin-managed)

- `WB-SUG-063` Pilot signed-commit enforcement on the most sensitive branch set first, then expand.
  - repo_fit: Workbench has many automated commits and agents; phased signed-commit rollout can improve commit authenticity without immediate contributor friction.
  - source: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - impact: Better provenance and tamper resistance for protected branches.
  - risk_class: `R2`
  - status: `implemented` (local pilot policy contract in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`; commit-signing enforcement remains admin-managed)

- `WB-SUG-064` If self-hosted runners are introduced, require runner groups and private-repo-only policy from day zero.
  - repo_fit: Workbench automation credentials and artifacts are sensitive; runner segmentation prevents cross-repo compromise paths.
  - source: https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-guides/security-hardening-for-github-actions and https://docs.github.com/en/actions/hosting-your-own-runners/managing-access-to-self-hosted-runners-using-groups
  - impact: Lower runner compromise blast radius and clearer trust boundaries.
  - risk_class: `R3`
  - status: `implemented` (conditional self-hosted policy contract in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`; live org/runner-group settings remain admin-managed)

- `WB-SUG-065` Pin required status checks to the intended GitHub App source.
  - repo_fit: Workbench decisions depend on required checks as hard gates; app-source pinning reduces spoofable status injection risk.
  - source: https://github.blog/changelog/2021-11-30-ensure-required-status-checks-provided-by-the-intended-app/ and https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - impact: Higher trust in merge-blocking/merge-allowing signals.
  - risk_class: `R1`
  - status: `implemented` (policy + audit contract in `docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md`; live ruleset setting remains admin-managed)

- `WB-SUG-066` Add `Master Bench` CODEOWNERS policy for workflow and gate-script paths.
  - repo_fit: Guild/master-craft model maps directly to control-plane stewardship: workflow and gate files require designated maintainers.
  - source: https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-guides/security-hardening-for-github-actions and https://www.britannica.com/topic/master-craft-guild
  - impact: Fewer risky automation edits merged without domain-owner review.
  - risk_class: `R0`
  - status: `implemented` (`.github/CODEOWNERS` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-067` Add merge-queue timeout triage playbook linked to PR removal reasons.
  - repo_fit: Workbench’s weekly wave system depends on predictable queue flow; timeout/removal reason handling should be standardized.
  - source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request-with-a-merge-queue?tool=webui
  - impact: Faster unblocking and less queue thrash during peak parallel windows.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `docs/research/CP_RUNBOOK_COMMANDS.md`)

## Lightweight intake batch: 2026-02-15 (dependency graph + runner resilience + async economics)

- `WB-SUG-068` Submit build-time dependency snapshots to GitHub Dependency Graph on every CI run.
  - repo_fit: Workbench has mixed Python/tooling surfaces where manifest-only scanning can miss resolved/transitive runtime dependencies.
  - source: https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/using-the-dependency-submission-api
  - impact: Better dependency visibility and higher-fidelity Dependabot/dependency-review findings.
  - risk_class: `R1`
  - status: `implemented` (`scripts/generate_dependency_inventory.py` + `.github/workflows/reusable-forge-gates.yml` + `docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md`; dependency graph API submission remains admin-managed)

- `WB-SUG-069` Add SBOM generation and snapshot submission (`CycloneDX`/`SPDX`) as a policy-review artifact.
  - repo_fit: Workbench already runs policy/scorecard workflows; SBOM snapshot artifacts fit existing governance cadence.
  - source: https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/using-the-dependency-submission-api and https://github.com/CycloneDX/cyclonedx-python
  - impact: Stronger software inventory traceability and better vulnerability triage context.
  - risk_class: `R2`
  - status: `implemented` (`scripts/generate_dependency_inventory.py` SPDX output + `docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md`)

- `WB-SUG-070` Add a reusable workflow for “forge gates” and call it from all primary pipelines to remove drift.
  - repo_fit: Workbench has multiple workflows (`ci`, `size-check`, `nightly`, policy jobs) that can diverge unless centrally reused.
  - source: https://docs.github.com/en/actions/concepts/workflows-and-actions/avoiding-duplication
  - impact: Lower maintenance overhead and more consistent gate behavior.
  - risk_class: `R0`
  - status: `implemented` (`.github/workflows/reusable-forge-gates.yml` + calls from `.github/workflows/{ci,size-check,nightly-evals,policy-review}.yml`)

- `WB-SUG-071` Add runner scale-set readiness plan for peak 8+ agent periods (even if using hosted runners today).
  - repo_fit: Parallel wave model will eventually hit capacity/latency bottlenecks; scale-set architecture planning avoids reactive migration.
  - source: https://docs.github.com/en/actions/concepts/runners/runner-scale-sets and https://docs.github.com/en/enterprise-server%403.17/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets
  - impact: Predictable CI capacity growth path and reduced queue latency under burst load.
  - risk_class: `R3`
  - notes: Keep as design-stage until runner ownership decision is approved.
  - status: `implemented` (policy contract in `docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md`)

- `WB-SUG-072` If self-hosted is adopted, enforce ephemeral-job runners and forbid long-lived shared runner state.
  - repo_fit: Workbench executes security-sensitive automation; persistent runners accumulate cross-job residue and raise compromise risk.
  - source: https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-guides/security-hardening-for-github-actions
  - impact: Lower lateral-movement risk across jobs and cleaner trust boundary.
  - risk_class: `R3`
  - status: `implemented` (conditional ephemeral-runner policy contract in `docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md`)

- `WB-SUG-073` Add script-injection lint check for workflow files (untrusted context to shell sink patterns).
  - repo_fit: Workbench automation scripts are dense; explicit guard against `${{ github.* }}` untrusted interpolation in inline shell reduces workflow exploitability.
  - source: https://docs.github.com/en/actions/concepts/security/script-injections
  - impact: Earlier detection of high-risk workflow injection mistakes.
  - risk_class: `R1`
  - status: `implemented` (`scripts/check_workflow_script_injection.py` + reusable forge-gates + quality gate wiring)

- `WB-SUG-074` Add transactional outbox semantics to campaign-event writes (`write + publish` atomicity) where dual-write risk exists.
  - repo_fit: Workbench and AAS hive patterns already rely on outbox/event channels; formalizing outbox semantics reduces lost-event edge cases.
  - source: https://microservices.io/patterns/data/transactional-outbox.html
  - impact: Better event consistency and fewer reconciliation repairs.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md` + outbox template + `scripts/check_event_resilience_policy.py`)

- `WB-SUG-075` Add consumer idempotency ledger for campaign/event processors with replay-safe semantics.
  - repo_fit: Workbench recovery workflows may reprocess artifacts/events; idempotent consumers prevent duplicate side effects.
  - source: https://microservices.io/patterns/data/transactional-outbox.html
  - impact: Safer retries, fewer duplicate actions, and cleaner replay behavior.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md` + idempotency template + `scripts/check_event_resilience_policy.py`)

- `WB-SUG-076` Wrap external API/tool calls in explicit circuit-breaker policy during campaign loops.
  - repo_fit: Workbench invokes external systems (`gh`, MCP endpoints, remote APIs); failure cascades can stall multiple lanes without breakers.
  - source: https://martinfowler.com/bliki/CircuitBreaker.html
  - impact: Lower cascade failure probability and faster partial-service recovery.
  - risk_class: `R1`
  - status: `implemented` (circuit-breaker policy contract in `docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md` + gate enforcement)

- `WB-SUG-077` Use Little’s Law to set lane WIP limits from observed throughput and lead-time metrics.
  - repo_fit: Workbench already defines weekly waves; queueing math gives objective WIP settings instead of subjective limits.
  - source: https://en.wikipedia.org/wiki/Little%27s_law and https://dora.dev/guides/dora-metrics/
  - impact: Better flow stability and fewer overcommitted waves.
  - risk_class: `R0`
  - notes: Replace with a primary paper citation in normalization sweep if needed.
  - status: `implemented` (`scripts/compute_littles_law_wip.py` + `docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md`)

- `WB-SUG-078` Move low-priority eval expansion jobs to OpenAI Batch API queue for cost and rate headroom.
  - repo_fit: Workbench roadmap calls for larger eval sets; async batch processing suits non-immediate workloads.
  - source: https://platform.openai.com/docs/guides/batch
  - impact: Lower eval cost and less contention with synchronous operational calls.
  - risk_class: `R1`
  - status: `implemented` (batch-routing policy contract in `docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md` + gate enforcement)

- `WB-SUG-079` Add AI RMF-based risk register for autonomous campaign features (`Govern/Map/Measure/Manage` tags per campaign).
  - repo_fit: Workbench is adopting long autonomous runs; AI-RMF tagging gives structured risk oversight for agentic behavior changes.
  - source: https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook
  - impact: Better governance traceability and clearer risk ownership.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/templates/AI_RMF_RISK_REGISTER_TEMPLATE.md` + `docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md` + checker)

- `WB-SUG-080` Add `Daedalus Diagram` for each campaign: planned path, fallback branches, and escape hatch.
  - repo_fit: Mythological framing maps to concrete run-graph docs for multi-step autonomous execution and rollback decisions.
  - source: https://www.britannica.com/biography/Daedalus-Greek-mythology
  - impact: Faster operator comprehension during incidents and handoffs.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/templates/DAEDALUS_DIAGRAM_TEMPLATE.md` + `docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md` + checker)

- `WB-SUG-081` Add `Hermes Relay` handoff packet standard for cross-lane baton passes.
  - repo_fit: Workbench’s 8+ lane model needs fast reliable relays; standardized handoff packet reduces context loss between agent turns.
  - source: https://www.britannica.com/topic/Hermes-Greek-mythology
  - impact: Lower handoff error rate and shorter takeover time between lanes.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md` + `docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md` + checker)

## Lightweight intake batch: 2026-02-15 (attestation lifecycle + CI telemetry + async control plane)

- `WB-SUG-082` Add attestation lifecycle pruning job for stale/untrusted subjects.
  - repo_fit: Workbench now generates and verifies attestations; lifecycle cleanup prevents stale provenance records from creating policy ambiguity.
  - source: https://docs.github.com/actions/how-tos/security-for-github-actions/using-artifact-attestations/managing-the-lifecycle-of-artifact-attestations
  - impact: Cleaner provenance inventory and fewer confusing verification outcomes.
  - risk_class: `R1`
  - status: `implemented` (policy contract + gate in `docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md` and `scripts/check_release_supply_chain_policy.py`)

- `WB-SUG-083` Enable immutable releases for promotion-ready artifacts and enforce draft-first publish flow.
  - repo_fit: Workbench promotion waves benefit from locked tags/assets to prevent post-publish mutation.
  - source: https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/immutable-releases
  - impact: Stronger release integrity and reduced supply-chain tampering surface.
  - risk_class: `R2`
  - status: `implemented` (policy contract in `docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md`; release settings remain admin-managed)

- `WB-SUG-084` Add release integrity verification (`gh release verify` and `gh release verify-asset`) to promotion runbook.
  - repo_fit: Workbench already uses `gh` for workflow operations; release verification commands fit existing operator tooling.
  - source: https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/verifying-the-integrity-of-a-release
  - impact: Better consumer trust and explicit pre-promotion authenticity checks.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/CP_RUNBOOK_COMMANDS.md` + `docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md` + checker)

- `WB-SUG-085` Restrict reusable workflow sharing to a dedicated “Toolsmith” repo and document log-visibility caveats.
  - repo_fit: Workbench intends org-level reusable workflows; centralized sharing boundaries reduce accidental overexposure from private workflow reuse.
  - source: https://docs.github.com/actions/creating-actions/sharing-actions-and-workflows-with-your-organization
  - impact: Safer reusable-workflow distribution model.
  - risk_class: `R2`
  - status: `implemented` (Toolsmith boundary policy contract + log-visibility caveat in `docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md`)

- `WB-SUG-086` Group Dependabot security updates by ecosystem/risk tier to reduce PR storms during active campaign waves.
  - repo_fit: 8+ parallel agents plus frequent dependency updates can cause review backlog; grouped security updates keep update flow manageable.
  - source: https://docs.github.com/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates and https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file
  - impact: Lower dependency PR noise and faster security patch cadence.
  - risk_class: `R0`
  - status: `implemented` (`.github/dependabot.yml` grouped config + `scripts/check_release_supply_chain_policy.py`)

- `WB-SUG-087` Enforce enterprise/org Actions policy to require full SHA pinning and restrict external reusable workflows.
  - repo_fit: Workbench already pins actions; policy-level enforcement prevents accidental drift or unpinned additions.
  - source: https://docs.github.com/github/setting-up-and-managing-your-enterprise/setting-policies-for-organizations-in-your-enterprise-account/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-enterprise-account
  - impact: Stronger org-wide supply-chain baseline for workflows.
  - risk_class: `R2`
  - status: `implemented` (admin-managed org-policy contract captured in `docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md` + checker)

- `WB-SUG-088` Instrument CI pipeline spans/logs with OpenTelemetry CICD semantic conventions.
  - repo_fit: Workbench’s campaign model needs consistent telemetry keys across workflows and scripts for weekly reliability reviews.
  - source: https://opentelemetry.io/docs/specs/semconv/cicd/ and https://opentelemetry.io/docs/specs/semconv/cicd/cicd-spans/ and https://opentelemetry.io/docs/specs/semconv/cicd/cicd-logs/
  - impact: Better cross-run observability and easier dashboarding/forensics.
  - risk_class: `R1`
  - status: `implemented` (telemetry semantic-field policy contract in `docs/research/CICD_TELEMETRY_ERROR_TAXONOMY_POLICY.md` + checker)

- `WB-SUG-089` Standardize CICD error taxonomy using `error.type` and mandatory run identifiers.
  - repo_fit: Workbench failure triage currently mixes script/workflow outputs; semantic error fields improve machine grouping and alert routing.
  - source: https://opentelemetry.io/docs/specs/otel/semantic-conventions/
  - impact: Faster root-cause clustering and reduced triage time.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/templates/CICD_ERROR_TYPE_TAXONOMY_TEMPLATE.md` + `scripts/select_failure_taxonomy.py` + `scripts/check_cicd_telemetry_policy.py`)

- `WB-SUG-090` Use JetStream KV with TTL and watchers for lane-lease coordination in high-concurrency waves.
  - repo_fit: Workbench parallel lanes need short-lived ownership locks; KV TTL + watcher model maps to lease acquisition/expiration.
  - source: https://docs.nats.io/nats-concepts/jetstream/key-value-store
  - impact: Fewer conflicting campaign writes and clearer lock recovery.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md` + `scripts/check_jetstream_openai_campaign_policy.py`)

- `WB-SUG-091` Apply JetStream dedupe IDs + double-ack patterns for critical campaign event delivery.
  - repo_fit: Workbench long-run orchestration needs replay-safe messaging; dedupe + AckSync style semantics reduce duplicate side effects.
  - source: https://docs.nats.io/using-nats/developer/develop_jetstream/model_deep_dive
  - impact: Higher delivery correctness under retries/failures.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md` + `scripts/check_jetstream_openai_campaign_policy.py`)

- `WB-SUG-092` Add webhook signature verification as mandatory for any OpenAI async callback path.
  - repo_fit: Workbench is moving toward long async runs; unsigned callback handling would be a direct control-plane risk.
  - source: https://platform.openai.com/docs/webhooks
  - impact: Better authenticity guarantees for automation-triggering events.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md` + `scripts/check_jetstream_openai_campaign_policy.py`)

- `WB-SUG-093` Use `previous_response_id` conversation chaining for campaign loop continuity by default.
  - repo_fit: Workbench campaign loops are multi-turn and tool-heavy; first-class state chaining reduces context stitching bugs.
  - source: https://platform.openai.com/docs/guides/conversation-state and https://platform.openai.com/docs/guides/tools-computer-use/
  - impact: More deterministic multi-step agent behavior.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md` + `scripts/check_jetstream_openai_campaign_policy.py`)

- `WB-SUG-094` Add mandatory exponential backoff + jitter wrapper for OpenAI calls in loop scripts.
  - repo_fit: High-concurrency agent runs can hit shared rate limits; standardized retries prevent avoidable hard-blocks.
  - source: https://platform.openai.com/docs/guides/rate-limits/retrying-with-exponential-backoff
  - impact: Fewer transient-failure aborts and smoother campaign completion rates.
  - risk_class: `R0`
  - status: `implemented` (`scripts/openai_retry_backoff.py` + `docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md` + `scripts/check_jetstream_openai_campaign_policy.py`)

- `WB-SUG-095` Separate OpenAI staging vs production projects and enforce per-project spend/rate caps in campaign policy.
  - repo_fit: Workbench executes both exploratory and production-like runs; project separation prevents experiments from impacting production budgets.
  - source: https://platform.openai.com/docs/guides/production-best-practices/model-overview
  - impact: Better cost control and reduced operational blast radius.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md` + `.github/workflows/{ci,size-check}.yml` + `scripts/check_jetstream_openai_campaign_policy.py`)

## Lightweight intake batch: 2026-02-15 (workflow security scanning + queue semantics + long-run orchestration)

- `WB-SUG-096` Enable CodeQL analysis for GitHub Actions workflow files (`actions` language) in advanced setup.
  - repo_fit: Workbench’s control plane is workflow-heavy; scanning workflow YAML catches security flaws in the automation layer itself.
  - source: https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-queries/actions-built-in-queries and https://github.blog/changelog/2025-04-22-github-actions-workflow-security-analysis-with-codeql-is-now-generally-available/
  - impact: Earlier detection of workflow-specific vulnerabilities before merge.
  - risk_class: `R2`
  - status: `implemented` (`.github/workflows/codeql-actions-security.yml` + `docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md` + `scripts/check_workflow_codeql_matrix_policy.py`)

- `WB-SUG-097` Add policy gate for high-signal CodeQL Actions queries (`untrusted checkout`, `artifact poisoning`, `missing-workflow-permissions`).
  - repo_fit: These query classes map directly to Workbench’s CI/security posture and common GitHub Actions attack paths.
  - source: https://codeql.github.com/codeql-query-help/actions/
  - impact: Stronger prevention against CI/CD compromise patterns.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md` + `scripts/check_workflow_codeql_matrix_policy.py`)

- `WB-SUG-098` Add explicit `workflow_run` trust boundary rule: treat downloaded artifacts/workspace as untrusted unless provenance-verified.
  - repo_fit: Workbench consumes artifacts in verification workflows; this rule prevents trusted-context execution of untrusted material.
  - source: https://codeql.github.com/codeql-query-help/actions/actions-untrusted-checkout-high/ and https://github.blog/security/application-security/how-to-secure-your-github-actions-workflows-with-codeql/
  - impact: Reduced risk of artifact/workspace poisoning in privileged jobs.
  - risk_class: `R2`
  - status: `implemented` (`.github/workflows/verify-nightly-attestations.yml` trust-boundary declaration + `scripts/check_workflow_codeql_matrix_policy.py`)

- `WB-SUG-099` Define matrix `max-parallel` defaults per workflow class (`ci`, `nightly`, `policy`) and enforce via review checklist.
  - repo_fit: Workbench runs many concurrent jobs; explicit max-parallel settings prevent runner saturation and unstable queue times.
  - source: https://docs.github.com/enterprise-server%403.14/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow
  - impact: More predictable CI throughput under 8+ agent load.
  - risk_class: `R0`
  - status: `implemented` (`.github/workflow-matrix-review-checklist.md` + `.github/workflows/codeql-actions-security.yml` + `scripts/check_workflow_codeql_matrix_policy.py`)

- `WB-SUG-100` Require explicit `fail-fast` and `continue-on-error` declarations in every matrix job.
  - repo_fit: Workbench has both strict and exploratory lanes; explicit matrix failure semantics avoid accidental cancellation or silent failures.
  - source: https://docs.github.com/en/enterprise-cloud%40latest/actions/reference/workflow-syntax-for-github-actions
  - impact: Clearer failure behavior and less wasted compute.
  - risk_class: `R0`
  - status: `implemented` (`.github/workflows/codeql-actions-security.yml` matrix strategy + `scripts/check_workflow_codeql_matrix_policy.py`)

- `WB-SUG-101` Add reusable-workflow depth cap policy (`<=3`) even though platform permits deeper nesting.
  - repo_fit: Workbench already uses reusable workflows; depth caps preserve debuggability and reduce hidden coupling.
  - source: https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
  - impact: Lower workflow complexity and easier incident triage.
  - risk_class: `R0`
  - notes: Treat as process policy, not a platform limit.
  - status: `implemented` (`docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md` + `scripts/check_reusable_workflow_governance_policy.py`)

- `WB-SUG-102` Add monthly inventory report of reusable workflow consumers and refs.
  - repo_fit: Workbench reusable workflows are intended to spread; inventory helps track drift and stale refs across consumers.
  - source: https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
  - impact: Better governance of shared automation dependencies.
  - risk_class: `R0`
  - status: `implemented` (`scripts/generate_reusable_workflow_inventory.py` + `docs/reports/reusable_workflow_inventory.{json,md}` + `scripts/check_reusable_workflow_governance_policy.py`)

- `WB-SUG-103` Add private-workflow sharing warning checklist to onboarding/runbook (log visibility + token scope implications).
  - repo_fit: Workbench may share private reusable workflows; operators need explicit awareness of indirect access/log exposure tradeoffs.
  - source: https://docs.github.com/actions/creating-actions/sharing-actions-and-workflows-with-your-organization
  - impact: Fewer accidental exposure paths when sharing internal automation.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md` + `docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md` + `scripts/check_reusable_workflow_governance_policy.py`)

- `WB-SUG-104` For any self-hosted future, require `runs-on` group + labels in all jobs (no broad `self-hosted` only selector).
  - repo_fit: Deterministic runner targeting is critical for security boundaries in high-concurrency lanes.
  - source: https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job and https://docs.github.com/actions/concepts/runners/runner-groups
  - impact: Reduced accidental scheduling onto unintended runners.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md` + `scripts/check_reusable_workflow_governance_policy.py`)

- `WB-SUG-105` Default new NATS/JetStream consumers to pull mode for campaign workloads unless replay-only semantics are needed.
  - repo_fit: Workbench campaign orchestration favors controllable flow and horizontal scaling characteristics.
  - source: https://docs.nats.io/nats-concepts/jetstream/consumers
  - impact: Better backpressure control and fewer consumer overload incidents.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-106` Use JetStream `AckSync` for critical side-effecting event processors.
  - repo_fit: Workbench recovery and replay flows need strong delivery correctness on high-value events.
  - source: https://docs.nats.io/using-nats/developer/develop_jetstream/model_deep_dive
  - impact: Lower duplicate-processing risk under acknowledgment-loss scenarios.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-107` Add poison-message policy for `MaxDeliver` exhaustion (alert + quarantine path).
  - repo_fit: Long autonomous runs need deterministic handling when messages repeatedly fail processing.
  - source: https://docs.nats.io/nats-concepts/jetstream/consumers and https://docs.nats.io/nats-concepts/jetstream/streams
  - impact: Faster failure containment and less retry thrash.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-108` Standardize OpenAI background-mode usage policy with explicit terminal-state polling and cancellation handling.
  - repo_fit: Workbench roadmap includes long-running autonomous tasks where background mode fits better than synchronous calls.
  - source: https://platform.openai.com/docs/guides/background
  - impact: Higher completion reliability for long operations.
  - risk_class: `R1`
  - notes: Include ZDR caveat and storage behavior in policy text.
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-109` Add automatic `/responses/compact` trigger when loop context approaches threshold.
  - repo_fit: Workbench campaign loops are multi-turn/tool-heavy; compaction prevents context window pressure during long runs.
  - source: https://platform.openai.com/docs/guides/conversation-state
  - impact: Longer stable run continuity with lower context-overflow risk.
  - risk_class: `R1`
  - status: `implemented` (`scripts/evaluate_openai_compaction_threshold.py` + `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-110` Default campaign loop state chaining to `previous_response_id` unless explicit conversation object is required.
  - repo_fit: Workbench needs deterministic turn linkage in high-volume automated loops.
  - source: https://platform.openai.com/docs/guides/conversation-state
  - impact: Lower context stitching errors and cleaner loop implementation.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-111` Add per-project OpenAI budget alarms and hard caps in campaign preflight checks.
  - repo_fit: Workbench parallel agent runs can spike usage; budget caps should be treated as a preflight safety gate.
  - source: https://platform.openai.com/docs/guides/production-best-practices/model-overview
  - impact: Better cost predictability and fewer runaway spend incidents.
  - risk_class: `R0`
  - status: `implemented` (`scripts/openai_budget_preflight.py` + `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-112` Tune dependency review policy file with `fail-on-scopes`, `fail-on-severity`, and package deny-groups for supply-chain guardrails.
  - repo_fit: Workbench already runs dependency review; tighter config can better match runtime risk tolerance.
  - source: https://github.com/actions/dependency-review-action
  - impact: Earlier detection of risky dependency changes in PR flow.
  - risk_class: `R1`
  - status: `implemented` (`.github/dependency-review-config.yml` + `.github/workflows/dependency-review.yml` + `docs/research/DEPENDENCY_REVIEW_SUPPLY_CHAIN_POLICY.md` + `scripts/check_dependency_review_policy.py`)

## Lightweight intake batch: 2026-02-15 (deployment protection + telemetry contracts + stream operations)

- `WB-SUG-113` Add custom deployment protection rule integration for promotion environments (service-health gate before deploy).
  - repo_fit: Workbench operates as an automation control shelf; environment-level external health approval aligns with safe promotion waves.
  - source: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/configure-custom-protection-rules
  - impact: Fewer deployments during degraded platform conditions.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-114` Enforce environment wait-timer + required-reviewer policy on all promotion jobs.
  - repo_fit: Workbench’s 8+ parallel lanes need a cooldown and human checkpoint before high-impact environment transitions.
  - source: https://docs.github.com/en/actions/reference/environments
  - impact: Lower accidental fast-path promotions and better release discipline.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-115` Require deployment branch/tag allowlists per environment (`release-*`, `hotfix-*` only for prod-like targets).
  - repo_fit: Workbench campaign model benefits from deterministic promotion source branches.
  - source: https://docs.github.com/en/actions/reference/environments
  - impact: Reduced risk of deploying unvetted branches.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-116` Add explicit “allow admin bypass = false” policy for guarded environments.
  - repo_fit: Workbench hardening goals rely on predictable gates; bypass paths undermine campaign evidence guarantees.
  - source: https://docs.github.com/en/actions/reference/environments
  - impact: Stronger protection-rule integrity.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-117` Add dedicated CodeQL Actions security workflow and treat critical findings as merge blockers.
  - repo_fit: Workbench’s security-sensitive behavior lives significantly in workflow YAML and scripts, not only app code.
  - source: https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-queries/actions-built-in-queries and https://codeql.github.com/codeql-query-help/actions/
  - impact: Earlier interception of workflow-specific attack paths.
  - risk_class: `R2`
  - status: `implemented` (`.github/workflows/codeql-actions-security.yml` + `docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md` + `scripts/check_workflow_codeql_matrix_policy.py`)

- `WB-SUG-118` Add “workflow artifact trust boundary” checklist item whenever `workflow_run` consumes artifacts.
  - repo_fit: Workbench already has downstream verification workflows; explicit trust-boundary handling prevents accidental privileged execution of untrusted artifacts.
  - source: https://codeql.github.com/codeql-query-help/actions/actions-untrusted-checkout-high/
  - impact: Lower artifact poisoning and confused-deputy risk.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md` + `.github/workflows/verify-nightly-attestations.yml` + `scripts/check_workflow_codeql_matrix_policy.py`)

- `WB-SUG-119` Emit JetStream advisories into a retained ops stream and review weekly.
  - repo_fit: Workbench/AAS event-driven paths benefit from advisory telemetry for stream/consumer health.
  - source: https://docs.nats.io/running-a-nats-service/nats_admin/monitoring/monitoring_jetstream
  - impact: Better early warning for stream and consumer reliability drift.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `docs/research/templates/JETSTREAM_ADVISORY_WEEKLY_REVIEW_TEMPLATE.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-120` Define default consumer class policy: pull+durable for workers, ordered consumer only for analysis/replay.
  - repo_fit: Workbench has both queue-like processing and analysis/replay use cases; explicit defaults reduce misconfiguration.
  - source: https://docs.nats.io/nats-concepts/jetstream/consumers
  - impact: More predictable delivery semantics and scaling behavior.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-121` Add JetStream redelivery policy baseline (`AckWait`, `MaxDeliver`) per campaign workload type.
  - repo_fit: Campaign loops vary in task duration; per-workload redelivery tuning avoids premature retries or stuck messages.
  - source: https://docs.nats.io/nats-concepts/jetstream/consumers
  - impact: Lower retry thrash and fewer false poison-message incidents.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-122` Require Structured Outputs for terminal campaign reports and set `parallel_tool_calls: false` in schema-critical steps.
  - repo_fit: Workbench requires deterministic terminal artifacts for approval evidence; schema guarantees reduce parser/contract failures.
  - source: https://openai.com/index/introducing-structured-outputs-in-the-api/ and https://cookbook.openai.com/examples/structured_outputs_intro
  - impact: More reliable machine-validated campaign outcomes.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-123` Add automatic compaction threshold policy for long-running campaign loops.
  - repo_fit: Workbench orchestration runs can be long and tool-heavy; explicit compaction thresholds prevent context saturation.
  - source: https://platform.openai.com/docs/guides/conversation-state
  - impact: Longer stable run continuity with lower token/context failures.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/evaluate_openai_compaction_threshold.py` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-124` Add background-task timeout + cancellation SLO for async campaign tasks.
  - repo_fit: Workbench autonomous waves need explicit async lifecycle controls to avoid orphaned tasks and hidden cost accumulation.
  - source: https://platform.openai.com/docs/guides/background
  - impact: Better operational control and fewer zombie tasks.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/evaluate_background_task_slo.py` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-125` Add `Argus Watchtower` multi-signal promotion gate (CI pass + provenance pass + advisory health pass).
  - repo_fit: Workbench parallel campaigns need a single watchtower checkpoint aggregating critical signals before promotion.
  - source: https://www.britannica.com/topic/Argus-Greek-mythology and https://docs.nats.io/running-a-nats-service/nats_admin/monitoring/monitoring_jetstream and https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
  - impact: Higher confidence promotions with fewer blind spots.
  - risk_class: `R2`
  - notes: Keep myth label as alias only; implement as explicit aggregated gate checks.
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/evaluate_promotion_watchtower.py` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-126` Add `Janus Gate` two-stage promotion policy (review gate then runtime health gate) with mandatory evidence artifact.
  - repo_fit: Workbench “bench/forge” identity matches two-faced gatekeeping for both code readiness and operational readiness.
  - source: https://www.britannica.com/topic/Janus-Roman-god and https://docs.github.com/en/actions/reference/environments
  - impact: Reduced “tests pass but runtime unhealthy” promotions.
  - risk_class: `R1`
  - notes: Stage 1 = environment approvals, Stage 2 = custom protection or health signal.
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/evaluate_promotion_watchtower.py` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

## Lightweight intake batch: 2026-02-15 (operator UX + diagnostics + recovery playbooks)

- `WB-SUG-127` Add a mandatory “run summary contract” step in every workflow using `GITHUB_STEP_SUMMARY`.
  - repo_fit: Workbench is a human/operator-facing tool shelf; run summaries reduce log-diving and make parallel wave triage faster.
  - source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
  - impact: Faster operator diagnosis and clearer pass/fail context in workflow UI.
  - risk_class: `R0`
  - notes: Include gate outcomes, failed step links, and recommended next command.
  - status: `implemented` (`scripts/generate_run_summary.py` + `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md` + `scripts/check_workflow_operator_handoff_policy.py`)

- `WB-SUG-128` Add standardized annotation emission (`notice`/`warning`/`error`) for gate scripts.
  - repo_fit: Workbench has many custom validation scripts; annotations surface failures directly in run UX.
  - source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
  - impact: Better actionable error surfacing and reduced manual log scanning.
  - risk_class: `R0`
  - status: `implemented` (`scripts/run_quality_gates.py` + `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md` + `scripts/check_workflow_operator_handoff_policy.py`)

- `WB-SUG-129` Add a “rerun failed with debug” operator command snippet to runbook and campaign handoff packets.
  - repo_fit: High-concurrency run model needs deterministic recovery actions when jobs fail intermittently.
  - source: https://docs.github.com/actions/managing-workflow-runs/re-running-a-workflow
  - impact: Quicker time-to-recovery for flaky or transient failures.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/CP_RUNBOOK_COMMANDS.md` + `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md` + `scripts/check_workflow_operator_handoff_policy.py`)

- `WB-SUG-130` Add “pause switch” policy for non-critical workflows using workflow disable/enable commands during incident windows.
  - repo_fit: Workbench orchestrates many automated checks; controlled pause reduces noise/load during active incidents.
  - source: https://docs.github.com/en/actions/how-tos/managing-workflow-runs-and-deployments/managing-workflow-runs/disabling-and-enabling-a-workflow?tool=cli
  - impact: Cleaner incident response and reduced resource waste.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/CP_RUNBOOK_COMMANDS.md` + `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md` + `scripts/check_workflow_operator_handoff_policy.py`)

- `WB-SUG-131` Add a dedicated “workflow health board” doc section with badge links for core workflows (`ci`, `size-check`, `nightly`, `policy`).
  - repo_fit: Workbench is an operator/developer surface; at-a-glance health status improves handoff usability.
  - source: https://docs.github.com/en/actions/how-tos/monitoring-and-troubleshooting-workflows/monitoring-workflows/adding-a-workflow-status-badge
  - impact: Faster situational awareness during handoff and shift changes.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/WORKFLOW_HEALTH_BOARD.md` + `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md` + `scripts/check_workflow_operator_handoff_policy.py`)

- `WB-SUG-132` Add cancellation-safe cleanup policy (`if: cancelled()`) for post-failure artifact hygiene steps.
  - repo_fit: Parallel campaign runs increase cancellation frequency; cleanup steps should still execute predictably when runs are canceled.
  - source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation
  - impact: Less orphaned state/artifacts and cleaner rerun conditions.
  - risk_class: `R1`
  - status: `implemented` (`.github/workflows/{nightly-evals,reusable-policy-review,reusable-scorecards}.yml` + `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md` + `scripts/check_workflow_operator_handoff_policy.py`)

- `WB-SUG-133` Add an explicit visualization-graph checkpoint in triage runbook before deep log analysis.
  - repo_fit: Workbench multi-job workflows benefit from dependency graph triage to identify upstream blockers quickly.
  - source: https://docs.github.com/en/actions/how-tos/monitor-workflows/using-the-visualization-graph
  - impact: Reduced mean time to first correct failure hypothesis.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/CP_RUNBOOK_COMMANDS.md` + `docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md` + `scripts/check_workflow_operator_handoff_policy.py`)

- `WB-SUG-134` Add “Foreman Bench” environment custom protection service that blocks deploy if JetStream advisories show instability.
  - repo_fit: Workbench sits at control-plane edge; tying deploy approvals to messaging system health prevents fragile rollouts.
  - source: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/configure-custom-protection-rules and https://docs.nats.io/running-a-nats-service/nats_admin/monitoring/monitoring_jetstream
  - impact: Fewer promotions during backend instability windows.
  - risk_class: `R2`
  - notes: Myth/theme alias optional; implementation is a strict health gate API.
  - status: `implemented` (`docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md` + `scripts/check_merge_ruleset_deployment_guardrails.py`)

- `WB-SUG-135` Define JetStream consumer baseline profile by workload (`interactive`, `batch`, `critical`) with tuned `MaxAckPending`.
  - repo_fit: Workbench handles heterogeneous workloads; one-size consumer settings can cause either starvation or overload.
  - source: https://docs.nats.io/nats-concepts/jetstream/consumers
  - impact: Better throughput stability and reduced delivery stalls.
  - risk_class: `R1`
  - status: `implemented` (`scripts/evaluate_jetstream_consumer_profile.py` + `docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-136` Adopt explicit redelivery backoff arrays (not implicit immediate redelivery) for long-running campaign tasks.
  - repo_fit: Autonomous loops can generate repeated transient failures; controlled backoff prevents retry storms.
  - source: https://docs.nats.io/nats-concepts/jetstream/consumers and https://docs.nats.io/using-nats/developer/develop_jetstream/consumers
  - impact: Lower retry thrash and improved downstream service stability.
  - risk_class: `R1`
  - status: `implemented` (`scripts/evaluate_jetstream_consumer_profile.py` + `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-137` Add DLQ implementation policy based on JetStream `MaxDeliver` advisories and message sequence retrieval.
  - repo_fit: Workbench needs deterministic dead-letter handling for long unattended campaign queues.
  - source: https://docs.nats.io/using-nats/developer/develop_jetstream/consumers
  - impact: Clear poison-message path and fewer silent dropped tasks.
  - risk_class: `R2`
  - status: `implemented` (`docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md` + `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-138` Use OpenAI prompt objects/versioning for canonical campaign prompts and keep version refs in approval packets.
  - repo_fit: Workbench runs repeated autonomous prompts; versioned prompts improve repeatability and auditability.
  - source: https://platform.openai.com/docs/guides/prompting
  - impact: Lower prompt drift and easier experiment rollback.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md` + `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-139` Add `prompt_cache_key` policy per campaign family to improve cache hit consistency under parallel load.
  - repo_fit: 8+ agents can fragment prompt cache locality; stable cache keys improve latency/cost predictability.
  - source: https://platform.openai.com/docs/guides/prompt-caching
  - impact: Lower latency and token cost for repeated orchestration prompts.
  - risk_class: `R0`
  - status: `implemented` (`docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md` + `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-140` Add compaction-and-resume playbook: compact context, persist checkpoint, resume with `previous_response_id`.
  - repo_fit: Long campaign loops in Workbench can exceed practical context budgets; explicit compaction/restart process keeps runs alive.
  - source: https://platform.openai.com/docs/guides/conversation-state
  - impact: Fewer hard-blocks due to context growth and better continuity after long runs.
  - risk_class: `R1`
  - status: `implemented` (`docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md` + `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md` + `scripts/check_jetstream_consumer_openai_loop_policy.py`)

- `WB-SUG-141` Add a suggestions-bin status governance gate to enforce per-item status and evidence references.
  - repo_fit: Workbench continuously accumulates implementation suggestions; an automated checker prevents status drift and missing closure evidence.
  - source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
  - impact: More reliable between-prompt backlog governance and fewer stale/ambiguous suggestion entries.
  - risk_class: `R0`
  - status: `implemented` (`scripts/check_suggestions_bin_status.py` + `scripts/generate_suggestions_bin_report.py` + `docs/reports/suggestions_bin.json` + `tests/test_check_suggestions_bin_status.py` + `tests/test_generate_suggestions_bin_report.py` + `scripts/run_quality_gates.py`)

- `WB-SUG-142` Add suggestions-bin report-sync gate (`--check`) to fail fast when committed report drifts from markdown source.
  - repo_fit: Workbench treats `docs/SUGGESTIONS_BIN.md` as a live governance artifact; sync drift in `docs/reports/suggestions_bin.json` weakens auditability and handoff reliability.
  - source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands
  - impact: Deterministic report parity checks and lower risk of stale suggestion status evidence.
  - risk_class: `R0`
  - status: `implemented` (`scripts/generate_suggestions_bin_report.py` + `scripts/run_quality_gates.py` + `tests/test_generate_suggestions_bin_report.py` + `tests/test_run_quality_gates_plan.py` + `docs/research/SSDF_SP800_218_QUALITY_GATE_MAPPING.md`)

## Lightweight intake batch: 2026-02-18 (repo-specific advancement promotions)

- `WB-SUG-143` Add repo-local `pyproject.toml` to define Python toolchain and test/lint contracts.
  - repo_fit: Workbench relies on scripts and tests but currently inherits some tooling behavior from superproject context.
  - source: https://docs.pytest.org/en/stable/reference/customize.html and https://docs.astral.sh/uv/
  - impact: More deterministic local/CI behavior and reduced cross-repo coupling.
  - risk_class: `R1`
  - status: `new`

- `WB-SUG-144` Adopt `uv` lockfile-managed dependency installs for CI and local smoke workflows.
  - repo_fit: CI currently installs floating runtime/test dependencies; lock-based installs improve reproducibility.
  - source: https://docs.astral.sh/uv/
  - impact: Lower dependency drift and more stable gate outcomes.
  - risk_class: `R1`
  - status: `new`

- `WB-SUG-145` Add `ruff` lint/format gate in pre-commit and quality gates.
  - repo_fit: Workbench contains a large Python surface across `plugins/` and `scripts/` with many policy-critical modules.
  - source: https://docs.astral.sh/ruff/configuration/
  - impact: Faster static feedback and fewer style/quality regressions entering CI.
  - risk_class: `R0`
  - status: `new`

- `WB-SUG-146` Add targeted strict type-checking (`mypy`/`pyright`) for control-plane critical modules.
  - repo_fit: Modules such as `plugins/mcp_auth.py`, `plugins/workflow_engine.py`, and `scripts/validate_workspace_index.py` carry high reliability impact.
  - source: https://mypy.readthedocs.io/en/stable/existing_code.html and https://github.com/microsoft/pyright/blob/main/docs/configuration.md
  - impact: Reduced runtime contract errors in auth, workflow, and audit paths.
  - risk_class: `R1`
  - status: `new`

- `WB-SUG-147` Enforce branch coverage thresholds for critical script/plugin paths.
  - repo_fit: Current testing is broad but branch-level regression signal is not explicitly enforced.
  - source: https://coverage.readthedocs.io/en/5.5/branch.html and https://pytest-cov.readthedocs.io/en/latest/
  - impact: Stronger confidence on conditional logic in gate and orchestration code.
  - risk_class: `R1`
  - status: `new`

- `WB-SUG-148` Add direct runtime unit suites for high-risk plugins (`workflow_engine`, `mcp_auth`, `gui_hub_connector`).
  - repo_fit: Existing tests heavily cover policy/checker scripts; plugin runtime behavior deserves deeper direct coverage.
  - source: https://docs.pytest.org/en/stable/
  - impact: Faster detection of behavioral regressions in plugin logic.
  - risk_class: `R1`
  - status: `new`

- `WB-SUG-149` Add property-based tests for workflow state machine invariants (`pause/resume/schedule`).
  - repo_fit: `plugins/workflow_engine.py` is stateful and benefits from randomized invariant checks beyond example-based tests.
  - source: https://hypothesis.readthedocs.io/en/latest/quickstart.html
  - impact: Higher confidence in edge-case handling under varied execution orders.
  - risk_class: `R2`
  - status: `new`

- `WB-SUG-150` Standardize JSON schema validation across generated report artifacts.
  - repo_fit: Workbench emits many JSON reports under `docs/reports/`; schema-based validation improves contract stability.
  - source: https://json-schema.org/learn/getting-started-step-by-step
  - impact: Lower report-shape drift and safer automation handoffs.
  - risk_class: `R1`
  - status: `new`

- `WB-SUG-151` Add shared HTTP resilience policy (timeouts, retries, backoff) for external calls.
  - repo_fit: Network calls in `plugins/mcp_auth.py` and scorecard/dependency checks can fail transiently and currently vary in behavior.
  - source: https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts and https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.retry.Retry
  - impact: Fewer transient network-induced failures in policy and auth workflows.
  - risk_class: `R1`
  - status: `new`

- `WB-SUG-152` Refactor `scripts/validate_workspace_index.py` into modular subcommands with incremental mode.
  - repo_fit: The workspace index validator is large and high-impact; modularization improves maintainability and runtime efficiency.
  - source: https://docs.python.org/3/library/argparse.html#sub-commands and https://git-scm.com/docs/git-diff
  - impact: Faster local feedback loops and lower complexity risk in the primary index audit tool.
  - risk_class: `R2`
  - status: `new`

## Repo-Specific Advancement Research Queue (2026-02-18)

`WB-SUG` governance cap status: `100 / 100` (cap enforced by `scripts/check_suggestions_bin_status.py`).

Additional repo-specific advancement recommendations are queued in:

- `docs/research/WORKBENCH_REPO_ADVANCEMENT_RECOMMENDATIONS_2026-02-18.md`

Promotion guidance:

1. Keep `WB-SUG` entries capped at `100` for operator readability and deterministic report handoff.
2. Promote from the research queue by rotating/archive-only older implemented entries when needed.
3. Regenerate and sync-check report artifacts after each rotation (`python3 scripts/generate_suggestions_bin_report.py` and `python3 scripts/generate_suggestions_bin_report.py --check`).
