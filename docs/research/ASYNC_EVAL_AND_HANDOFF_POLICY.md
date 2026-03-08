# Async Eval and Campaign Handoff Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## OpenAI Batch Queue Routing (WB-SUG-078)

Policy:

1. low-priority eval expansion workloads are routed to Batch API-compatible lanes.
2. Batch jobs are tagged by campaign and lane for replay and traceability.
3. High-priority interactive checks remain on synchronous lanes.

## AI RMF Risk Register Contract (WB-SUG-079)

Policy:

1. Campaign-risk entries are tagged with AI RMF functions: `Govern`, `Map`, `Measure`, and `Manage`.
2. Every autonomous campaign packet references an AI RMF risk register row.
3. Risk owner and mitigation status are mandatory fields.

Reference artifact:

- `docs/research/templates/AI_RMF_RISK_REGISTER_TEMPLATE.md`

## Daedalus Diagram Contract (WB-SUG-080)

Policy:

1. Every campaign includes a Daedalus diagram with planned path, fallback branches, and escape hatch.
2. Diagram links are included in approval and incident handoff packets.
3. Diagram revisions are versioned by campaign run identifier.

Reference artifact:

- `docs/research/templates/DAEDALUS_DIAGRAM_TEMPLATE.md`

## Hermes Relay Handoff Packet Standard (WB-SUG-081)

Policy:

1. Cross-lane baton passes use Hermes relay packet fields: source lane, destination lane, transfer reason, and acknowledgement.
2. Handoff packet includes known risks, next commands, and blocking dependencies.
3. Relay acknowledgement is required before source lane closure.

Reference artifact:

- `docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md`

## Required Local Artifacts

- `docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md`
- `docs/research/templates/AI_RMF_RISK_REGISTER_TEMPLATE.md`
- `docs/research/templates/DAEDALUS_DIAGRAM_TEMPLATE.md`
- `docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md`
- `scripts/check_async_eval_handoff_policy.py`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_async_eval_handoff_policy.py` | `[ok] async eval/handoff policy check` |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `async-eval-handoff-policy` gate |
| `cat docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md` | Hermes relay template available for handoff packets |
