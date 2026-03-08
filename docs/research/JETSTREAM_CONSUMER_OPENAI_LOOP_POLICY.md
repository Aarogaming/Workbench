# JetStream Consumer and OpenAI Loop Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## Pull Consumer Default for Campaign Workloads (WB-SUG-105)

Policy:

1. New JetStream consumers for campaign workers default to pull mode.
2. Replay/analysis-only consumers may use ordered or push mode with explicit justification.
3. Pull consumers must declare durable names and bounded batch/fetch settings.

## Critical AckSync Delivery Policy (WB-SUG-106)

Policy:

1. Critical side-effecting processors require `AckSync` confirmation before marking completion.
2. Missing ack confirmation is treated as uncertain processing and requires replay review.
3. Critical handlers log `operation_id`, stream sequence, and ack outcome.

## Poison-Message MaxDeliver Exhaustion Policy (WB-SUG-107)

Policy:

1. On `MaxDeliver` exhaustion, messages are quarantined to a deterministic dead-letter path.
2. Policy requires alert emission with campaign context and consumer identity.
3. Quarantine handling includes retrieval by stream sequence for forensic replay.

## OpenAI Background-Mode Terminal-State Contract (WB-SUG-108)

Policy:

1. Background-mode tasks require terminal-state polling (`completed`, `failed`, `cancelled`, `expired`).
2. Cancellation handling is mandatory and must record reason + owner.
3. Async tasks exceeding timeout SLO trigger escalation.

## Automatic Compaction Threshold Trigger (WB-SUG-109)

Policy:

1. Long-running loops evaluate context usage against compaction threshold before each turn.
2. If threshold is exceeded, call `/responses/compact` before continuing.
3. Compaction decisions are logged with threshold, observed usage, and checkpoint id.

Reference artifact:

- `scripts/evaluate_openai_compaction_threshold.py`

## Default previous_response_id Chaining (WB-SUG-110)

Policy:

1. Campaign loops default to `previous_response_id` unless explicit conversation object is required.
2. Any deviation from default chaining requires operator rationale in run notes.

## OpenAI Budget Alarm + Hard-Cap Preflight (WB-SUG-111)

Policy:

1. Campaign preflight validates spend against per-project hard caps.
2. Budget alarms are evaluated before promotion for both `staging` and `production` projects.
3. Cap breach blocks execution until owner override is documented.

Reference artifact:

- `scripts/openai_budget_preflight.py`

## JetStream Advisories Ops Stream and Weekly Review (WB-SUG-119)

Policy:

1. JetStream advisories are emitted to a retained ops stream.
2. Advisory review occurs weekly and records drift/actions.
3. Critical advisories require incident linkage and owner assignment.

Reference artifact:

- `docs/research/templates/JETSTREAM_ADVISORY_WEEKLY_REVIEW_TEMPLATE.md`

## Consumer Class Defaults by Workload (WB-SUG-120)

Policy:

1. Worker consumers default to pull + durable.
2. Analysis/replay consumers may use ordered mode when side effects are absent.
3. Consumer class selection is declared in campaign preflight notes.

## Redelivery Baseline by Workload Type (WB-SUG-121)

Policy:

1. Workload classes define baseline `AckWait` and `MaxDeliver` values.
2. Baseline changes require evidence of throughput/latency impact.
3. Excess redelivery incidents trigger policy-tuning review.

## Structured Outputs for Terminal Reports (WB-SUG-122)

Policy:

1. Terminal campaign reports use Structured Outputs with explicit schema contracts.
2. Schema-critical report requests set `parallel_tool_calls: false`.
3. Validation failures are treated as contract failures and retried via bounded policy.

Reference artifact:

- `docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json`

## Automatic Compaction Threshold Contract (WB-SUG-123)

Policy:

1. Compaction threshold checks run before each long-loop turn.
2. Threshold breaches require `/responses/compact` before next model call.
3. Compaction decision evidence is attached to run summary context.

## Background Task Timeout and Cancellation SLO (WB-SUG-124)

Policy:

1. Async tasks define explicit timeout SLO thresholds.
2. Timeout breaches require cancellation or escalation action.
3. Cancellation reasons are captured for post-run reliability analysis.

Reference artifact:

- `scripts/evaluate_background_task_slo.py`

## JetStream Baseline Profiles by Workload (WB-SUG-135)

Policy:

1. Workloads use explicit baseline consumer profiles (`interactive`, `batch`, `critical`) including `MaxAckPending`.
2. Profile overrides require explicit operator review with impact notes.
3. Baseline profile records include `AckWait`, `MaxDeliver`, and backoff schedule.

Reference artifacts:

- `scripts/evaluate_jetstream_consumer_profile.py`
- `docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md`

## Explicit Redelivery Backoff Arrays (WB-SUG-136)

Policy:

1. Long-running workloads define explicit redelivery backoff arrays instead of immediate implicit retries.
2. Backoff arrays are tuned per workload class and reviewed in advisory weekly review.
3. Backoff changes require throughput/error-rate evidence in campaign notes.

Reference artifact:

- `scripts/evaluate_jetstream_consumer_profile.py`

## DLQ Contract from MaxDeliver Advisories (WB-SUG-137)

Policy:

1. `MaxDeliver` advisories route messages to a deterministic DLQ path.
2. DLQ handling captures stream and message sequence identifiers for replay.
3. DLQ retrieval procedure is recorded in workload baseline profile artifacts.

Reference artifact:

- `docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md`

## OpenAI Prompt Object Versioning Contract (WB-SUG-138)

Policy:

1. Canonical campaign prompts are referenced by prompt object id + version.
2. Prompt object references include explicit prompt version values and are attached in approval packet evidence.
3. Version rollback target is recorded with each prompt change.

Reference artifact:

- `docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md`

## Prompt Cache Key Contract by Campaign Family (WB-SUG-139)

Policy:

1. Each campaign family defines a stable `prompt_cache_key`.
2. Cache key format includes campaign family and prompt object version.
3. Cache key drift requires packet-level rationale and owner sign-off.

Reference artifact:

- `docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md`

## Compaction and Resume Playbook Contract (WB-SUG-140)

Policy:

1. Threshold breach triggers context compaction and checkpoint persistence.
2. Resume flow requires checkpoint id and `previous_response_id` linkage.
3. Compaction-and-resume evidence is attached to incident handoff packet.

Reference artifact:

- `docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md`

## Required Local Artifacts

- `docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md`
- `scripts/check_jetstream_consumer_openai_loop_policy.py`
- `scripts/evaluate_openai_compaction_threshold.py`
- `scripts/openai_budget_preflight.py`
- `docs/research/templates/JETSTREAM_ADVISORY_WEEKLY_REVIEW_TEMPLATE.md`
- `docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json`
- `scripts/evaluate_background_task_slo.py`
- `scripts/evaluate_jetstream_consumer_profile.py`
- `docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md`
- `docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md`
- `docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md`
- `docs/research/CP_RUNBOOK_COMMANDS.md`
- `docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_jetstream_consumer_openai_loop_policy.py` | `[ok] jetstream consumer/openai loop policy check` |
| `python3 scripts/evaluate_openai_compaction_threshold.py --current-ratio 0.84 --threshold 0.80` | Prints `compact=true` decision |
| `python3 scripts/openai_budget_preflight.py --project-tier production --current-spend 950 --cap 1000 --alarm-threshold 0.9` | Prints preflight decision payload |
| `python3 scripts/evaluate_background_task_slo.py --duration-seconds 450 --timeout-seconds 600 --cancelled false` | Prints SLO posture payload |
| `python3 scripts/evaluate_jetstream_consumer_profile.py --workload critical` | Prints baseline profile payload including `MaxAckPending` and backoff array |
| `cat docs/research/templates/STRUCTURED_OUTPUT_TERMINAL_REPORT_REQUEST_TEMPLATE.json` | Shows schema-critical request template with `parallel_tool_calls: false` |
| `cat docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md` | Shows workload baseline + DLQ profile template |
| `cat docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md` | Shows prompt object/version and `prompt_cache_key` reference template |
| `cat docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md` | Shows compaction/resume checkpoint and `previous_response_id` playbook template |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `jetstream-consumer-openai-loop-policy` gate |
