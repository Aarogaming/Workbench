# Campaign Wave Operations Policy

Date: 2026-02-17  
Scope: `Workbench/**`  
Applies to: Weekly parallel campaign waves (`A0` through `A8+`)

## Purpose

Define enforceable flow-control and incident-learning policies for high-concurrency campaign operations.

## Lane WIP Limits

Default lane-level work-in-progress limits for active campaign waves:

| Lane | Focus | WIP limit |
| --- | --- | ---: |
| `A0` | Program orchestration | `1` |
| `A1` | Plugin migration | `2` |
| `A2` | Plugin contracts | `2` |
| `A3` | Test lane | `2` |
| `A4` | Eval lane | `2` |
| `A5` | CI/supply-chain lane | `2` |
| `A6` | Ops/runbooks lane | `2` |
| `A7` | Cross-repo compatibility lane | `2` |
| `A8` | Reserve/hotfix lane | `1` |

Policy:

1. No lane may exceed its WIP limit without `A0` exception logging in campaign notes.
2. If total hard blocks exceed `2` in a week, freeze new starts and prioritize clearance.
3. Any canary-wave policy change runs with reduced WIP (`-1` per active lane) until steady-state pass.

## Ariadne Thread After-Action Template

Use: `docs/research/templates/ARIADNE_THREAD_AFTER_ACTION_TEMPLATE.md`

Policy:

1. Every completed campaign must produce one Ariadne Thread record.
2. The record must include planned path, actual path, deviations, and recovery thread.

## Three-Phase Checklist

Required phases for each campaign:

1. `sign-in`:
   - Confirm owner lane, scope lock, rollback owner, and target artifact contract.
2. `time-out`:
   - Mid-wave control check (`gate health`, `risk count`, `remaining scope`).
3. `sign-out`:
   - Confirm terminal outcome, evidence artifact list, and next-owner handoff.

Single-conductor rule:

1. Each campaign has one single responsible conductor for the full wave.
2. Conductor changes require explicit sign-in note in the handoff packet.

## Start-Small Pilot Rollout Rule

Policy for new gates/workflow controls:

1. Week 1: one-lane canary (`A5` or relevant owner lane), no broad rollout.
2. Week 2: expand to up to 3 lanes only if canary has no hard-block regressions.
3. Week 3+: full rollout after documented steady-state evidence.

## Continuous Monitoring Loop

Minimum monitoring loop during active waves:

1. Every 30 minutes:
   - `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals`
   - `python3 scripts/check_cp4b_sla.py`
2. Every 2 hours:
   - `python3 scripts/run_quality_gates.py --skip-tests --skip-evals`
3. On every hard block:
   - Re-run `check_chimera_packets.py`, `check_operations_nist_mapping.py`, and handoff artifacts checks.

## Blameless Postmortem Trigger Policy

Use: `docs/research/templates/BLAMELESS_POSTMORTEM_TEMPLATE.md`

Trigger conditions (any one):

1. Same gate fails in 2 consecutive waves.
2. Incident handoff completeness falls below `100%`.
3. CP4-B SLA breach count > `0` for a wave.
4. Any unplanned rollback during a promotion wave.

## Cursus Publicus Relay Model

Use: `docs/research/templates/CURSUS_PUBLICUS_RELAY_TEMPLATE.md`

Relay classes:

1. `mutationes` quick relay:
   - Fast baton pass for bounded context updates, no scope expansion.
2. `mansiones` full checkpoint:
   - Complete checkpoint with status, artifacts, risk state, and planned next actions.

Policy:

1. Active campaigns use mutationes handoffs for intra-day relays.
2. Every 12 hours, produce one mansiones checkpoint until campaign closure.
