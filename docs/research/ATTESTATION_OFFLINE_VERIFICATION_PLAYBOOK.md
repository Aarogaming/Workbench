# Attestation Offline Verification Playbook

Date: 2026-02-17  
Scope: `Workbench/**`

## Purpose

Provide a deterministic offline verification path when attestation API retrieval is constrained, using a local bundle file (`.json`/`.jsonl`) and explicit identity policy.

## Required Inputs

- Subject artifacts (for current flow):
  - `attested_artifacts/eval_report.json`
  - `attested_artifacts/eval_report.md`
- Offline bundle file:
  - Example: `attested_artifacts/attestations_bundle.jsonl`
- Identity policy:
  - `--repo owner/repo`
  - `--signer-workflow owner/repo/.github/workflows/nightly-evals.yml`
  - `--predicate-type https://slsa.dev/provenance/v1`

## Local Command Path

```bash
python3 scripts/verify_attestations.py \
  --repo owner/repo \
  --signer-workflow owner/repo/.github/workflows/nightly-evals.yml \
  --predicate-type https://slsa.dev/provenance/v1 \
  --subject attested_artifacts/eval_report.json \
  --subject attested_artifacts/eval_report.md \
  --bundle attested_artifacts/attestations_bundle.jsonl \
  --json-out docs/reports/attestation_verify_report.json
```

Expected result:

- Exit `0` on success.
- `docs/reports/attestation_verify_report.json` includes:
  - `identity.signer_workflow`
  - `identity.predicate_type`
  - `verification.mode = offline_bundle`
  - `verification.bundle_path`

## Workflow Dispatch Path

Use `.github/workflows/verify-nightly-attestations.yml` with:

- `run_id`: required source run id
- `offline_bundle_path`: optional local bundle file path

Behavior:

- If `offline_bundle_path` is provided, workflow runs `Offline bundle preflight`.
- Verification step injects `--bundle <offline_bundle_path>` into `scripts/verify_attestations.py`.
- Identity checks remain enforced in offline mode.

## Acceptance Checks

- `python3 scripts/check_attestation_preflight_wiring.py`
- `python3 scripts/check_attestation_identity_wiring.py`
- `python3 scripts/check_attestation_offline_wiring.py`
- `python3 scripts/check_gh_cli_version.py --min-version 2.50.0`
