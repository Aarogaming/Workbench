# OpenAI Async Execution Policy

Date: 2026-02-17  
Scope: `Workbench/**`  
Applies to: Long-running campaign and evaluation tasks using OpenAI APIs

## Purpose

Define minimum policy controls for background execution, webhook processing, prompt caching, and flex-routing decisions.

## Background-Mode Webhook Worker Pattern

Required pattern:

1. Create long-running tasks with background mode enabled.
2. Persist a stable idempotency key per campaign/task initiation.
3. Track terminal-state transitions (`completed`, `failed`, `cancelled`, `expired`) in local campaign artifacts.
4. Retry non-terminal polling/webhook processing with bounded exponential backoff.

Minimum controls:

1. Record request id, response id, campaign id, and run id in the task ledger.
2. Do not mark task successful until terminal state is explicitly observed.
3. Reject duplicate webhook events based on event id and idempotency ledger.

## Webhook Signature Verification

Policy:

1. Verify webhook signatures before processing payloads.
2. Fail closed on signature validation errors.
3. Log validation failures with incident context and no secret leakage.

## Prompt-Caching Design Policy

Policy requirements:

1. Keep a stable static prompt prefix for each campaign family.
2. Set and persist a deterministic `prompt_cache_key` per campaign family/version.
3. Track cache-key version changes in campaign notes.
4. Avoid per-request randomization in cache-critical prompt prefix regions.

## Flex Processing Routing Policy

Policy:

1. Low-priority eval expansion and non-urgent analysis may use flex routing.
2. Production-critical or incident-response paths must remain on standard priority.
3. Route decision must be declared in preflight packet for each campaign wave.

## Retry and Terminal-State Handling

Minimum retry policy:

1. Exponential backoff with jitter for transient failures.
2. Cap total retry duration per task.
3. Escalate to hard block if terminal failure persists beyond retry budget.

Terminal-state policy:

1. `completed`: attach output summary + validation evidence.
2. `failed`: attach error classification + next-owner escalation.
3. `cancelled` or `expired`: attach cancellation reason + restart decision.

## Required Local Artifacts

1. `docs/research/OPENAI_ASYNC_EXECUTION_POLICY.md`
2. `docs/research/CP_RUNBOOK_COMMANDS.md` (OpenAI policy checks)
3. `docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md` (tracking entries)
