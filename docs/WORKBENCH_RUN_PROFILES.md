# Workbench Run Profiles

Status: Active baseline
Date: 2026-02-19
Owner: Workbench A0/A6 lanes

## Purpose

Define deterministic campaign run profiles for Workbench execution lanes.

## Profiles

## `dry_run`

Use when validating packet wiring, path locks, and artifact contracts without
mutating implementation targets.

- Intended lane use: `A0`, `A6`, `A7`
- Required preflight:
  - `bash scripts/run_preflight_campaign.sh --skip-tests --skip-evals`
- Execution behavior:
  - commands run in simulation mode where available
  - outcome recorded as `complete` only when all dry-run gates pass

## `guarded_impl`

Use for low-to-medium risk implementation waves with strict preflight and
post-validation.

- Intended lane use: `A1`, `A2`, `A3`, `A5`
- Required preflight:
  - `bash scripts/run_preflight_campaign.sh`
- Required post-validate:
  - `python3 scripts/eval_report.py --baseline evals/baselines/main.json`
  - `pytest -q`

## `promotion_wave`

Use only for approved cross-lane campaigns that may impact release posture,
policy, or compatibility.

- Intended lane use: `A0` with reviewer lanes
- Required preflight:
  - `bash scripts/run_preflight_campaign.sh`
  - packet approval check against `docs/WORKBENCH_APPROVAL_PACKET_TEMPLATE.md`
- Required outcome constraints:
  - terminal outcome must include rollback pointer
  - evidence outputs must include trace + validation transcript

## Terminal Outcomes

All profiles must finish with one of:

1. `complete`
2. `hard_block`
3. `cancelled`

`hard_block` outcomes must list unblock inputs.

## Artifact Convention

Store campaign outputs under `docs/reports/campaigns/`:

- trace: `CAMPAIGN_TRACE_<campaign-id>.json`
- outcome: `CAMPAIGN_OUTCOME_<campaign-id>.json`
- summary: `CAMPAIGN_SUMMARY_<campaign-id>.md`
