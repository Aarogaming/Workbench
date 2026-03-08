# CHIMERA V2 CP4-A Operator Readiness Status

Date: 2026-02-15  
Cycle ID: `CHIMERA-V2-RESEARCH-AND-EXECUTION-2026-02-15`  
Phase: `CP4-A`  
Scope: `Workbench/**`

## Readiness Decision

Status: `READY`  
Incident handoff status: `READY FOR CUTOVER INCIDENT TRANSFER`

Readiness basis:

- CP2 observability packet exists and defines minimum run-summary and artifact-fetch standards.
- Repo-local artifact fetch helper exists and passes syntax/help/dry-run canary checks.
- Required local evidence artifacts for eval, attestation, policy, scorecard, and workspace audit are present.

## Operator Canary Checklist

| Canary | Objective | Command | Outcome |
| --- | --- | --- | --- |
| `C1` | Validate artifact fetch helper syntax | `bash -n scripts/fetch_workbench_artifacts.sh` | `PASS` |
| `C2` | Validate deterministic fetch command generation | `bash scripts/fetch_workbench_artifacts.sh --run-id 123456789 --repo owner/repo --class eval --class attestations --class policy --dry-run --out-dir artifacts/cutover/CP4A-CANARY/123456789-a1` | `PASS` |
| `C3` | Validate CP2 run-summary contract anchors | `rg -n "schema_version|terminal_class|failure_taxonomy|artifact_fetch_cmd" docs/research/CHIMERA_V2_CP2_OPERATOR_OBSERVABILITY_PACKET_2026-02-15.md` | `PASS` |
| `C4` | Validate required local artifact presence | `for p in ...; do [ -e "$p" ] && echo "[ok] $p" || echo "[missing] $p"; done` | `PASS` |

## Rollback Communication Template

Use this template for CP4-A rollback announcements.

```text
Subject: [ROLLBACK] CHIMERA V2 CP4-A Incident Cutover

Timestamp (UTC): <YYYY-MM-DDTHH:MM:SSZ>
Incident ID: <INCIDENT_ID>
Cycle ID: CHIMERA-V2-RESEARCH-AND-EXECUTION-2026-02-15
Trigger: <hard_block|soft_block reason>
Current Terminal Class: <hard_block|soft_block>

Rollback Action:
- Scope reverted: Workbench/<path or workflow>
- Operator command used: <exact command>
- Expected stabilization window: <minutes>

Handoff Owner:
- Current owner: <lane/operator>
- Next owner: <lane/operator>
- Handoff by (UTC): <YYYY-MM-DDTHH:MM:SSZ>

Evidence Links (repo-local):
- <path 1>
- <path 2>
- <path 3>

Decision:
- Promotion/Cutover state: ROLLED BACK
- Next checkpoint: <time + gate condition>
```

## Required Local Artifact Links

- `docs/research/CHIMERA_V2_CP2_OPERATOR_OBSERVABILITY_PACKET_2026-02-15.md`
- `scripts/fetch_workbench_artifacts.sh`
- `artifacts/cutover/CP4A-CANARY/123456789-a1/fetch_summary.txt`
- `docs/reports/eval_report.md`
- `docs/reports/eval_report.json`
- `docs/reports/attestation_verify_report.json`
- `docs/reports/workflow_pinning_audit.json`
- `docs/reports/workflow_pinning_exceptions_review.json`
- `docs/reports/scorecard_threshold_audit.json`
- `docs/reports/scorecard_history.md`
- `docs/reports/scorecard_history.json`
- `docs/reports/workspace_index_audit.md`
- `docs/reports/workspace_index_audit.json`
- `docs/OPERATIONS.md`

## Verification Commands and Outcomes

1. Command:
   ```bash
   bash -n scripts/fetch_workbench_artifacts.sh
   ```
   Outcome: `exit 0` (no output)

2. Command:
   ```bash
   bash scripts/fetch_workbench_artifacts.sh --run-id 123456789 --repo owner/repo --class eval --class attestations --class policy --dry-run --out-dir artifacts/cutover/CP4A-CANARY/123456789-a1
   ```
   Outcome:
   ```text
   [dry-run] class=eval gh run download 123456789 --repo owner/repo --name nightly-eval-report --dir artifacts/cutover/CP4A-CANARY/123456789-a1/eval
   [dry-run] class=attestations gh run download 123456789 --repo owner/repo --name attestation-verify-report --dir artifacts/cutover/CP4A-CANARY/123456789-a1/attestations
   [dry-run] class=policy gh run download 123456789 --repo owner/repo --name workflow-policy-reports --dir artifacts/cutover/CP4A-CANARY/123456789-a1/policy
   [summary] artifacts/cutover/CP4A-CANARY/123456789-a1/fetch_summary.txt
   ```
   Outcome: `exit 0`

3. Command:
   ```bash
   rg -n "schema_version|terminal_class|failure_taxonomy|artifact_fetch_cmd" docs/research/CHIMERA_V2_CP2_OPERATOR_OBSERVABILITY_PACKET_2026-02-15.md
   ```
   Outcome:
   ```text
   27:| `schema_version` | string | MUST be `cp2.run_summary.v1` |
   31:| `terminal_class` | string enum | MUST be one of `complete`, `soft_block`, `hard_block` |
   32:| `failure_taxonomy` | string enum | MUST be one of `infra`, `script`, `policy`, `artifact`, `human_gate`, `supply_chain` |
   41:| `artifact_fetch_cmd` | string | MUST be copy/paste-ready |
   124:  "schema_version": "cp2.run_summary.v1",
   128:  "terminal_class": "soft_block",
   129:  "failure_taxonomy": "policy",
   138:  "artifact_fetch_cmd": "bash scripts/fetch_workbench_artifacts.sh --run-id 123456789 --repo owner/repo --class policy --class attestations --out-dir artifacts/cutover/CUTOVER-2026-02-15-001/123456789-a1",
   ```
   Outcome: `exit 0`

4. Command:
   ```bash
   for p in docs/research/CHIMERA_V2_CP2_OPERATOR_OBSERVABILITY_PACKET_2026-02-15.md scripts/fetch_workbench_artifacts.sh artifacts/cutover/CP4A-CANARY/123456789-a1/fetch_summary.txt docs/reports/eval_report.md docs/reports/eval_report.json docs/reports/attestation_verify_report.json docs/reports/workflow_pinning_audit.json docs/reports/workflow_pinning_exceptions_review.json docs/reports/scorecard_threshold_audit.json docs/reports/scorecard_history.md docs/reports/scorecard_history.json docs/reports/workspace_index_audit.md docs/reports/workspace_index_audit.json docs/OPERATIONS.md; do if [ -e "$p" ]; then echo "[ok] $p"; else echo "[missing] $p"; fi; done
   ```
   Outcome:
   ```text
   [ok] docs/research/CHIMERA_V2_CP2_OPERATOR_OBSERVABILITY_PACKET_2026-02-15.md
   [ok] scripts/fetch_workbench_artifacts.sh
   [ok] artifacts/cutover/CP4A-CANARY/123456789-a1/fetch_summary.txt
   [ok] docs/reports/eval_report.md
   [ok] docs/reports/eval_report.json
   [ok] docs/reports/attestation_verify_report.json
   [ok] docs/reports/workflow_pinning_audit.json
   [ok] docs/reports/workflow_pinning_exceptions_review.json
   [ok] docs/reports/scorecard_threshold_audit.json
   [ok] docs/reports/scorecard_history.md
   [ok] docs/reports/scorecard_history.json
   [ok] docs/reports/workspace_index_audit.md
   [ok] docs/reports/workspace_index_audit.json
   [ok] docs/OPERATIONS.md
   ```
   Outcome: `exit 0`
