# Release and Supply Chain Policy

Date: 2026-02-17  
Scope: `Workbench/**`

## Attestation Lifecycle Pruning (WB-SUG-082)

Policy:

1. attestation inventory is reviewed on a fixed cadence to prune stale/untrusted subjects.
2. Pruning decisions are captured in audit evidence before deletion actions.
3. Offline verification artifacts are retained according to forensic retention policy.

## Immutable Release Publish Flow (WB-SUG-083)

Policy:

1. Promotion-ready releases use immutable releases with draft-first publish flow.
2. Draft review evidence is required before final publish.
3. Post-publish asset mutation is prohibited.

## Release Integrity Verification Commands (WB-SUG-084)

Policy:

1. Release promotion packets include `gh release verify`.
2. Asset checks include `gh release verify-asset`.
3. Verification output is attached to the promotion packet before approval.

## Toolsmith Reusable Workflow Sharing Boundary (WB-SUG-085)

Policy:

1. Reusable workflow sharing is bounded to a dedicated Toolsmith governance boundary.
2. Private-workflow sharing decisions include explicit log visibility caveats.
3. Cross-repo sharing exceptions require owner and expiry.

## Dependabot Security Update Grouping (WB-SUG-086)

Policy:

1. Dependabot updates are grouped by ecosystem/risk tier to avoid PR storms.
2. Security updates are grouped separately from routine version updates.
3. Grouping policy is versioned in `.github/dependabot.yml`.

## Org Actions Policy Baseline (WB-SUG-087)

Policy:

1. Org/enterprise Actions policy requires full-length commit SHA pinning.
2. External reusable workflow restrictions are enforced at org/enterprise boundary.
3. Local repo policy packets document this as an admin-managed control.

## Required Local Artifacts

- `docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md`
- `.github/dependabot.yml`
- `.github/workflows/verify-nightly-attestations.yml`
- `docs/research/ATTESTATION_OFFLINE_VERIFICATION_PLAYBOOK.md`
- `scripts/check_release_supply_chain_policy.py`

## Verification Commands and Outcomes

| Command | Expected outcome |
| --- | --- |
| `python3 scripts/check_release_supply_chain_policy.py` | `[ok] release/supply-chain policy check` |
| `cat .github/dependabot.yml` | Includes grouped update configuration |
| `gh release verify <tag>` | Release provenance verified |
| `gh release verify-asset <tag> <asset-name>` | Release asset integrity verified |
