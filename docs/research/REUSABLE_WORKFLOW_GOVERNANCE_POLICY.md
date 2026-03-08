# Reusable Workflow Governance Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## Reusable Workflow Nesting Depth Cap (WB-SUG-101)

Policy:

1. Local reusable workflow call depth is capped at `<=3`.
2. Any request to exceed cap requires explicit architecture review and exception record.
3. Depth checks are enforced by local quality gate scripts.

## Monthly Reusable Workflow Consumer Inventory (WB-SUG-102)

Policy:

1. Produce a monthly inventory of reusable workflow consumers and refs.
2. Inventory includes consumer workflow, target reusable workflow, reference/ref, and source line.
3. Inventory reports are generated to local artifacts for operator review.

Reference artifact:

- `scripts/generate_reusable_workflow_inventory.py`

## Private Workflow Sharing Warning Checklist (WB-SUG-103)

Policy:

1. Onboarding/runbook paths must include explicit warning checklist for private workflow sharing.
2. Checklist must cover log visibility and token scope implications.
3. Sharing boundary changes require checklist acknowledgement.

Reference artifact:

- `docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md`

## Self-Hosted Runner Group + Labels Selector Policy (WB-SUG-104)

Policy:

1. Broad `runs-on: self-hosted` selectors are forbidden.
2. Self-hosted jobs must use runner group + labels selectors.
3. Any future self-hosted adoption requires explicit selector review in pull request checklist.

## Required Local Artifacts

- `docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md`
- `scripts/check_reusable_workflow_governance_policy.py`
- `scripts/generate_reusable_workflow_inventory.py`
- `docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md`
- `docs/research/CP_RUNBOOK_COMMANDS.md`
- `docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/generate_reusable_workflow_inventory.py --output-dir docs/reports` | Emits reusable workflow inventory JSON+Markdown reports |
| `python3 scripts/check_reusable_workflow_governance_policy.py` | `[ok] reusable workflow governance policy check` |
| `python3 scripts/run_quality_gates.py --plan --skip-tests --skip-evals` | Plan includes `reusable-workflow-governance-policy` gate |
