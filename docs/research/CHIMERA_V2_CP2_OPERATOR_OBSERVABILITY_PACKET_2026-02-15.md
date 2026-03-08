# CHIMERA V2 CP2 Operator Observability Packet

Date: 2026-02-15  
Cycle ID: `CHIMERA-V2-RESEARCH-AND-EXECUTION-2026-02-15`  
Phase: `CP2 Advisory Enforcement`  
Scope: `Workbench/**`

## Function Statement

Convert observability suggestions into an operator-ready incident handoff packet that is executable during cutover incidents, not advisory-only.

## CP2 Minimum Standard (Run Summary + Artifact Fetch)

This section is normative for cutover incident handoffs.

### 1. Run Summary Standard (MUST)

Every incident handoff MUST include both:

- `run_summary.md` (human-readable)
- `run_summary.json` (machine-readable)

Minimum required fields in `run_summary.json`:

| Field | Type | Requirement |
| --- | --- | --- |
| `schema_version` | string | MUST be `cp2.run_summary.v1` |
| `cycle_id` | string | MUST match cycle identifier |
| `phase` | string | MUST be `CP2` for this packet |
| `incident_id` | string | MUST be globally unique for the cutover window |
| `terminal_class` | string enum | MUST be one of `complete`, `soft_block`, `hard_block` |
| `failure_taxonomy` | string enum | MUST be one of `infra`, `script`, `policy`, `artifact`, `human_gate`, `supply_chain` |
| `repo` | string | MUST be `owner/repo` form |
| `workflow` | string | MUST match GitHub Actions workflow name |
| `run_id` | string | MUST be populated |
| `run_attempt` | integer | MUST be populated |
| `head_sha` | string | MUST be populated |
| `failing_job` | string | MUST be populated for non-`complete` outcomes |
| `failing_step` | string | MUST be populated for non-`complete` outcomes |
| `rerun_debug_cmd` | string | MUST be copy/paste-ready |
| `artifact_fetch_cmd` | string | MUST be copy/paste-ready |
| `next_owner` | string | MUST identify the accountable handoff owner |
| `requires_handoff_by_utc` | string | MUST be RFC3339 UTC timestamp |
| `generated_at_utc` | string | MUST be RFC3339 UTC timestamp |

Minimum required sections in `run_summary.md`:

1. `Incident Header` (incident id, run id, workflow, attempt, sha)
2. `Outcome` (terminal class, failure taxonomy, severity)
3. `Failure Snapshot` (job, step, top error lines)
4. `Artifact Fetch` (exact command + target directory)
5. `Next Actions` (owner, deadline, escalation condition)

### 2. Artifact Fetch Standard (MUST)

Incident handoff MUST classify and fetch artifacts with the class map below:

| Class | Artifact Name | Expected Source Workflow |
| --- | --- | --- |
| `eval` | `nightly-eval-report` | `Nightly Evals` |
| `attestations` | `attestation-verify-report` | `Verify Nightly Attestations` |
| `policy` | `workflow-policy-reports` | `Policy Review` |
| `scorecards` | `scorecard-results` | `Scorecards` |

Fetch destination convention:

- `artifacts/cutover/<incident_id>/<run_id>-a<run_attempt>/<class>/`

If an artifact class is unavailable for a specific run/workflow:

- Record it in `run_summary.json` under `missing_artifacts`.
- Do not leave the class implicit.

## <=1 Pass Implementation Slice (Delivered in CP2)

Pass: `CP2-P0`  
Scope: deterministic artifact retrieval for incident handoff

Delivered:

- `scripts/fetch_workbench_artifacts.sh`
- This packet (`docs/research/CHIMERA_V2_CP2_OPERATOR_OBSERVABILITY_PACKET_2026-02-15.md`)

Operator command (standardized):

```bash
bash scripts/fetch_workbench_artifacts.sh \
  --run-id <RUN_ID> \
  --repo <OWNER/REPO> \
  --class eval \
  --class attestations \
  --class policy \
  --out-dir artifacts/cutover/<INCIDENT_ID>/<RUN_ID>-a<RUN_ATTEMPT>
```

## Acceptance Checks (CP2-P0)

The implementation slice is accepted when the following checks pass:

1. Script syntax check passes.
2. Script help output renders required options.
3. Dry-run prints deterministic `gh run download` commands for requested classes.
4. Output directory and fetch summary file are created in dry-run mode.

Reference commands:

```bash
bash -n scripts/fetch_workbench_artifacts.sh
bash scripts/fetch_workbench_artifacts.sh --help
bash scripts/fetch_workbench_artifacts.sh \
  --run-id 123456789 \
  --repo owner/repo \
  --class eval \
  --class attestations \
  --class policy \
  --dry-run \
  --out-dir artifacts/cutover/CP2-ACCEPTANCE/123456789-a1
```

## Run Summary JSON Skeleton

```json
{
  "schema_version": "cp2.run_summary.v1",
  "cycle_id": "CHIMERA-V2-RESEARCH-AND-EXECUTION-2026-02-15",
  "phase": "CP2",
  "incident_id": "CUTOVER-2026-02-15-001",
  "terminal_class": "soft_block",
  "failure_taxonomy": "policy",
  "repo": "owner/repo",
  "workflow": "Policy Review",
  "run_id": "123456789",
  "run_attempt": 1,
  "head_sha": "<git_sha>",
  "failing_job": "workflow-policy-review",
  "failing_step": "Workflow pinning exceptions review",
  "rerun_debug_cmd": "gh run rerun 123456789 --repo owner/repo --failed --debug",
  "artifact_fetch_cmd": "bash scripts/fetch_workbench_artifacts.sh --run-id 123456789 --repo owner/repo --class policy --class attestations --out-dir artifacts/cutover/CUTOVER-2026-02-15-001/123456789-a1",
  "next_owner": "lane-security",
  "requires_handoff_by_utc": "2026-02-15T18:30:00Z",
  "generated_at_utc": "2026-02-15T18:00:00Z",
  "missing_artifacts": []
}
```

## Cutover Use Notes

- This packet is intentionally minimum-viable for CP2 and should be enforced before broadening schema scope.
- Automatic generation of `run_summary.md/json` in workflows is a next-pass item; CP2 enforces command and field standards first.
