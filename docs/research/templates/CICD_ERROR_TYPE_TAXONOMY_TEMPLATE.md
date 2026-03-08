# CICD Error Type Taxonomy Template

| error.type | Description | Routing owner | Typical first command |
| --- | --- | --- | --- |
| `infra` | Runner, network, or environment capacity failure | `lane-workbench` | `gh run rerun <run-id> --failed --debug` |
| `script` | Script/runtime exception | `lane-workbench` | `python3 scripts/run_quality_gates.py --skip-tests --skip-evals` |
| `policy` | Control/policy gate failure | `lane-governance` | `python3 scripts/check_ssdf_quality_gate_mapping.py` |
| `artifact` | Artifact generation/fetch/verify mismatch | `lane-observability` | `python3 scripts/validate_fetch_index.py` |
| `human_gate` | Reviewer/approval/manual gate failure | `lane-governance` | `cat docs/OPERATIONS.md` |
| `supply_chain` | Provenance/attestation/release integrity failure | `lane-supply-chain` | `python3 scripts/verify_attestations.py --help` |
