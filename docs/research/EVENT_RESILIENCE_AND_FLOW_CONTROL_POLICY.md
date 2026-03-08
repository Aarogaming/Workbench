# Event Resilience and Flow Control Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## Transactional Outbox Semantics (WB-SUG-074)

Policy:

1. Side-effecting campaign events use write + publish semantics through a transactional outbox contract.
2. Outbox records include stable `operation_id` and publish-state fields.
3. Outbox replay rules are documented for failure and recovery windows.

Reference artifact:

- `docs/research/templates/OUTBOX_EVENT_RECORD_TEMPLATE.json`

## Consumer Idempotency Ledger (WB-SUG-075)

Policy:

1. Event consumers maintain an idempotency ledger keyed by `operation_id`.
2. Duplicate event deliveries are replay-safe and must not trigger duplicate side effects.
3. Ledger entries include status and processed timestamp fields for auditability.

Reference artifact:

- `docs/research/templates/IDEMPOTENCY_LEDGER_ENTRY_TEMPLATE.json`

## Circuit Breaker Wrapper Policy (WB-SUG-076)

Policy:

1. External API and tool calls in campaign loops are wrapped by a circuit breaker.
2. Circuit states (`closed`, `open`, `half-open`) are explicitly logged.
3. Breaker recovery windows and failure thresholds are defined before promotion.

## Little's Law WIP Calibration (WB-SUG-077)

Policy:

1. Lane WIP targets are calibrated with `WIP = throughput * lead_time`.
2. A configurable buffer factor is applied to protect stability during variance.
3. WIP recalculation occurs when throughput or lead-time trend shifts exceed policy thresholds.

Reference artifact:

- `scripts/compute_littles_law_wip.py`

## Required Local Artifacts

- `docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md`
- `docs/research/templates/OUTBOX_EVENT_RECORD_TEMPLATE.json`
- `docs/research/templates/IDEMPOTENCY_LEDGER_ENTRY_TEMPLATE.json`
- `scripts/compute_littles_law_wip.py`
- `scripts/check_event_resilience_policy.py`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_event_resilience_policy.py` | `[ok] event resilience policy check` |
| `python3 scripts/compute_littles_law_wip.py --throughput-per-day 6 --lead-time-days 2 --buffer 1.15` | Prints recommended WIP result |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `event-resilience-policy` gate |
