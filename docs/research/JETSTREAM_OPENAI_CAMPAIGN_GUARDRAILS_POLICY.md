# JetStream and OpenAI Campaign Guardrails Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## JetStream KV Lease Coordination (WB-SUG-090)

Policy:

1. Lane ownership leases use JetStream Key-Value with explicit `ttl` boundaries.
2. Lease keys follow `lane_lease/<lane_id>` naming for deterministic watcher filters.
3. Watchers are required for create, update, and delete events to detect lease takeovers or expiry.
4. Lease renewal cadence must stay below half of configured `ttl` to preserve handoff safety.

## JetStream Dedupe + Double-Ack Delivery (WB-SUG-091)

Policy:

1. Critical campaign event publishes include a deterministic dedupe id using `Nats-Msg-Id`.
2. Consumer ack policy for critical side effects requires explicit ack confirmation via `AckSync`.
3. Dedupe id generation uses `campaign_id + operation_id + logical_step` to remain replay-safe.
4. If `AckSync` confirmation is not observed, treat event handling as uncertain and escalate for replay review.

## OpenAI Webhook Signature Verification (WB-SUG-092)

Policy:

1. Any async callback path requires signature verification before payload parsing.
2. Signature failures are fail-closed and must not trigger campaign state mutation.
3. Verification logs include event id, run id, and incident id with no secret leakage.
4. Callback handlers enforce replay-window checks using webhook timestamp and nonce/event id tracking.

## Conversation Continuity via previous_response_id (WB-SUG-093)

Policy:

1. Multi-turn campaign loops default to `previous_response_id` chaining.
2. New conversation roots are only allowed with explicit operator rationale in run notes.
3. Resume flows must persist `response_id` checkpoints before control transfer.

## Mandatory Exponential Backoff + Jitter Wrapper (WB-SUG-094)

Policy:

1. OpenAI loop calls use exponential backoff with bounded jitter for transient failures.
2. Retry wrappers include configurable `base_delay`, `max_delay`, and jitter ratio controls.
3. Retry attempts are budgeted and logged with final terminal-state classification.

Reference artifact:

- `scripts/openai_retry_backoff.py`

## Project Separation and Budget Caps (WB-SUG-095)

Policy:

1. Staging and production OpenAI projects are separated with distinct API credentials.
2. Production projects enforce hard caps for spend and request-rate limits.
3. Campaign preflight must declare the target project tier (`staging` or `production`) and associated budget guard.
4. Any cap exceedance immediately blocks promotion until reviewed by lane owner.

## Required Local Artifacts

- `docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md`
- `scripts/check_jetstream_openai_campaign_policy.py`
- `scripts/openai_retry_backoff.py`
- `docs/research/CP_RUNBOOK_COMMANDS.md`
- `docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_jetstream_openai_campaign_policy.py` | `[ok] jetstream/openai campaign policy check` |
| `python3 scripts/openai_retry_backoff.py --attempts 5 --base-delay 1 --max-delay 30 --jitter-ratio 0.2 --seed 42` | Prints deterministic retry delay schedule JSON |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `jetstream-openai-campaign-policy` gate |
