# Run Summary

## Incident Header
- Incident ID: `CUTOVER-2026-02-15-IMPLEMENT`
- Repo: `owner/repo`
- Workflow: `Workbench CI`
- Run: `246813579` attempt `2`
- Head SHA: `deadbeef`
- Generated (UTC): `2026-02-17T02:49:35Z`

## Outcome
- Terminal class: `hard_block`
- Failure taxonomy: `script`

## Failure Snapshot
- Failing job: `python-smoke`
- Failing step: `Unit tests`
- Top error lines: see workflow logs for the failing job/step.

## Artifact Fetch
- Command: `bash scripts/fetch_workbench_artifacts.sh --run-id 246813579 --repo owner/repo --incident-id CUTOVER-2026-02-15-IMPLEMENT --run-attempt 2 --class eval --class attestations --class policy`

## Next Actions
- Next owner: `lane-workbench`
- Handoff by (UTC): `2026-02-17T04:49:35Z`
- Rerun (debug): `gh run rerun 246813579 --repo owner/repo --failed --debug`
