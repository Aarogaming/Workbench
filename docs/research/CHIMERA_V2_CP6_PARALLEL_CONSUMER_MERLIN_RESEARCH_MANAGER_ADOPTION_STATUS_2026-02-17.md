# CHIMERA V2 CP6 Parallel Consumer Merlin Research Manager Adoption Status

Date refreshed: 2026-02-19  
Scope: `Workbench/**` (Merlin consumer lane + CP6 packet)

## Function Statement

Refresh CP6 parallel-consumer adoption evidence for the Workbench Merlin research-manager lane and verify success plus expected failure behavior with command-level proof.

## Evidence References

- `scripts/merlin_research_manager_consumer.py:95`
- `scripts/merlin_research_manager_consumer.py:111`
- `scripts/merlin_research_manager_consumer.py:129`
- `scripts/merlin_research_manager_consumer.py:142`
- `scripts/merlin_research_manager_consumer.py:189`
- `scripts/merlin_research_manager_consumer.py:208`
- `scripts/merlin_research_manager_consumer.py:242`
- `scripts/merlin_mock_capabilities_server.py:21`
- `scripts/merlin_mock_capabilities_server.py:39`
- `scripts/merlin_mock_capabilities_server.py:70`
- `scripts/run_merlin_cp6_local_checks.py:17`
- `scripts/run_merlin_cp6_local_checks.py:33`
- `scripts/run_merlin_cp6_local_checks.py:73`
- `scripts/run_merlin_cp6_local_checks.py:113`
- `tests/test_merlin_research_manager_consumer.py:50`
- `tests/test_merlin_research_manager_consumer.py:65`
- `tests/test_merlin_research_manager_consumer.py:77`
- `tests/test_merlin_research_manager_consumer.py:88`
- `tests/test_merlin_research_manager_consumer.py:102`
- `tests/test_merlin_research_manager_consumer.py:133`
- `tests/test_merlin_mock_capabilities_server.py:20`
- `tests/test_merlin_mock_capabilities_server.py:32`
- `tests/test_run_merlin_cp6_local_checks.py:17`
- `artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json`
- `artifacts/diagnostics/merlin_envelopes_preview_2026-02-19.json`
- `artifacts/diagnostics/merlin_error_read_only_2026-02-19.json`
- `artifacts/diagnostics/merlin_error_validation_2026-02-19.json`
- `docs/research/CHIMERA_V2_CP6_PARALLEL_CONSUMER_MERLIN_RESEARCH_MANAGER_ADOPTION_STATUS_2026-02-17.md`

## Changes Applied

1. Re-ran the required CP6 verification command set and refreshed this packet with exact command strings and outcomes.
2. Re-established local capabilities JSON generation through the required endpoint command.
3. Confirmed the Merlin consumer selects `research_manager` when create/signal/brief operations are present.
4. Reconfirmed fallback mappings for `RESEARCH_MANAGER_READ_ONLY` and `VALIDATION_ERROR`.
5. Added a one-pass implementation slice: `--emit-envelopes-json` (plus `--objective`, `--session-id`) to generate deterministic operator envelope artifacts from the consumer CLI.
6. Added `test_build_operator_demo_envelopes_emits_create_signal_brief` to validate create/signal/brief operation emission for the new helper.
7. Added direct CLI fallback runs with local error fixtures for both expected failure branches.
8. Generated an envelope preview artifact through the new CLI path.
9. Added `scripts/merlin_mock_capabilities_server.py` with `--once` mode to make required command-4 verification reproducible without ad hoc inline server code.
10. Added `tests/test_merlin_mock_capabilities_server.py` to verify payload composition and API-key enforcement behavior.
11. Added `scripts/run_merlin_cp6_local_checks.py` to execute the full required five-command CP6 verification set and emit a machine-readable PASS/FAIL summary artifact.
12. Added `tests/test_run_merlin_cp6_local_checks.py` to lock the runner to the exact required command set.

## Verification Commands Run

1. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py`
   - Outcome: PASS
   - Result: `7 passed in 0.73s`
2. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k test_envelope_builders_emit_create_signal_brief_operations`
   - Outcome: PASS
   - Result: `1 passed, 6 deselected in 0.45s`
3. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k "test_read_only_error_selects_non_mutating_fallback or test_validation_error_maps_to_expected_fallback"`
   - Outcome: PASS
   - Result: `2 passed, 5 deselected in 0.45s`
4. `python3 - <<'PY'
import json, requests
from pathlib import Path
p=Path('artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json'); p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(requests.get('http://localhost:8001/merlin/operations/capabilities', headers={'X-Merlin-Key':'merlin-secret-key'}, timeout=20).json(), indent=2)+'\n', encoding='utf-8')
print(p.as_posix())
PY`
   - Outcome: PASS
   - Result: `artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json`
5. `python3 scripts/merlin_research_manager_consumer.py --capabilities-json artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json`
   - Outcome: PASS
   - Result: capability gate output includes:
     - `research_manager_enabled: true`
     - `selected_path: research_manager`
     - `missing_core_operations: []`
     - `available_operations` contains `merlin.research.manager.session.create`, `merlin.research.manager.session.signal.add`, `merlin.research.manager.brief.get`
6. `python3 scripts/merlin_research_manager_consumer.py --error-json artifacts/diagnostics/merlin_error_read_only_2026-02-19.json --requested-operation merlin.research.manager.session.create`
   - Outcome: PASS
   - Result: fallback output includes:
     - `error_code: RESEARCH_MANAGER_READ_ONLY`
     - `selected_path: legacy_non_research_non_mutating`
     - `fallback_mode: read_only_guard_non_mutating_fallback`
     - `recommended_read_operation: merlin.research.manager.brief.get`
7. `python3 scripts/merlin_research_manager_consumer.py --error-json artifacts/diagnostics/merlin_error_validation_2026-02-19.json --requested-operation merlin.research.manager.session.get`
   - Outcome: PASS
   - Result: fallback output includes:
     - `error_code: VALIDATION_ERROR`
     - `selected_path: legacy_non_research`
     - `fallback_mode: repair_input_and_retry_legacy`
8. `python3 scripts/merlin_research_manager_consumer.py --emit-envelopes-json artifacts/diagnostics/merlin_envelopes_preview_2026-02-19.json --objective cutover-canary --session-id sess-001`
   - Outcome: PASS
   - Result: envelope preview output includes:
     - `artifact_path: artifacts/diagnostics/merlin_envelopes_preview_2026-02-19.json`
     - `create_operation: merlin.research.manager.session.create`
     - `signal_operation: merlin.research.manager.session.signal.add`
     - `brief_operation: merlin.research.manager.brief.get`
9. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k test_build_operator_demo_envelopes_emits_create_signal_brief`
   - Outcome: PASS
   - Result: `1 passed, 6 deselected in 0.55s`
10. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k test_emit_envelopes_cli_writes_artifact`
   - Outcome: PASS
   - Result: `1 passed, 6 deselected in 0.66s`
11. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k test_validation_error_fallback_supports_top_level_code`
   - Outcome: PASS
   - Result: `1 passed, 6 deselected in 0.52s`
12. `python3 -m pytest -q tests/test_merlin_mock_capabilities_server.py`
   - Outcome: PASS
   - Result: `2 passed in 0.61s`
13. `python3 scripts/merlin_mock_capabilities_server.py --once --host 127.0.0.1 --port 8001 --api-key merlin-secret-key`
   - Outcome: PASS
   - Result: `mock_merlin_capabilities_server: listening on 127.0.0.1:8001` (served one request and exited)
14. `python3 -m pytest -q tests/test_run_merlin_cp6_local_checks.py`
   - Outcome: PASS
   - Result: `1 passed in 0.37s`
15. `python3 scripts/run_merlin_cp6_local_checks.py --output-json artifacts/diagnostics/merlin_cp6_local_checks_2026-02-19.json`
   - Outcome: PASS
   - Result:
     - `artifacts/diagnostics/merlin_cp6_local_checks_2026-02-19.json`
     - `PASS`

## Success Flow Evidence (create -> signal -> brief)

1. `tests/test_merlin_research_manager_consumer.py:50` passed (`test_envelope_builders_emit_create_signal_brief_operations`).
2. `scripts/merlin_research_manager_consumer.py:95` builds session-create envelope using `OP_SESSION_CREATE`.
3. `scripts/merlin_research_manager_consumer.py:111` builds session-signal envelope using `OP_SESSION_SIGNAL_ADD`.
4. `scripts/merlin_research_manager_consumer.py:129` builds brief-get envelope using `OP_BRIEF_GET`.
5. Command 5 output confirms create/signal/brief operations are available and route selection is `research_manager`.
6. `scripts/merlin_research_manager_consumer.py:142` and `tests/test_merlin_research_manager_consumer.py:88` verify deterministic operator demo envelope generation.
7. `tests/test_merlin_research_manager_consumer.py:102` verifies CLI `--emit-envelopes-json` writes artifact and emits create/signal/brief operation metadata.
8. Command 8 generated `artifacts/diagnostics/merlin_envelopes_preview_2026-02-19.json` with explicit create/signal/brief operation values through the CLI.
9. Command 13 establishes a reusable, one-shot local endpoint for command 4 execution in operator runbooks.
10. `scripts/run_merlin_cp6_local_checks.py:17` and command 15 now execute the full required flow (`pytest -> focused success test -> focused failure tests -> capabilities fetch -> capability gate`) in one deterministic operator command.

## Expected Failure Branch Evidence (VALIDATION_ERROR / RESEARCH_MANAGER_READ_ONLY)

1. `tests/test_merlin_research_manager_consumer.py:65` passed (`test_read_only_error_selects_non_mutating_fallback`).
2. `tests/test_merlin_research_manager_consumer.py:77` passed (`test_validation_error_maps_to_expected_fallback`).
3. `tests/test_merlin_research_manager_consumer.py:133` confirms top-level `code` extraction still maps `VALIDATION_ERROR` to expected fallback.
4. `scripts/merlin_research_manager_consumer.py:189` maps `RESEARCH_MANAGER_READ_ONLY` to `legacy_non_research_non_mutating` and non-mutating mode.
5. `scripts/merlin_research_manager_consumer.py:208` maps `VALIDATION_ERROR` to `legacy_non_research` with `repair_input_and_retry_legacy`.
6. Command 6 produced runtime fallback output for `RESEARCH_MANAGER_READ_ONLY` with non-mutating route selection.
7. Command 7 produced runtime fallback output for `VALIDATION_ERROR` with repair-and-retry legacy fallback mode.
8. `scripts/merlin_mock_capabilities_server.py:39` + `tests/test_merlin_mock_capabilities_server.py:32` verify authenticated endpoint behavior (403 invalid key, 200 valid key).
9. Command 15 persisted required command outcomes in `artifacts/diagnostics/merlin_cp6_local_checks_2026-02-19.json` for handoff auditing.

## Artifacts Produced

- `docs/research/CHIMERA_V2_CP6_PARALLEL_CONSUMER_MERLIN_RESEARCH_MANAGER_ADOPTION_STATUS_2026-02-17.md`
- `artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json`
- `artifacts/diagnostics/merlin_envelopes_preview_2026-02-19.json`
- `artifacts/diagnostics/merlin_error_read_only_2026-02-19.json`
- `artifacts/diagnostics/merlin_error_validation_2026-02-19.json`
- `artifacts/diagnostics/merlin_cp6_local_checks_2026-02-19.json`

## Risks and Next Pass

1. Local CP6 runner command 4 remains mock-backed for deterministic reproducibility; this validates consumer routing/fallback logic but not remote service health.
2. Live capability gating is additionally verified against a real Merlin payload (`../artifacts/diagnostics/merlin_operations_capabilities_probe_2026-02-28_refresh.json`) with `research_manager_enabled=true`.
3. Next pass should repeat the direct live capability fetch in the target integration environment and compare manifest parity.

## FOLLOW_UP_2026_02_28_VERIFICATION

1. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py`
   - Outcome: PASS (`7 passed`)
2. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k test_envelope_builders_emit_create_signal_brief_operations`
   - Outcome: PASS (`1 passed, 6 deselected`)
3. `python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k "test_read_only_error_selects_non_mutating_fallback or test_validation_error_maps_to_expected_fallback"`
   - Outcome: PASS (`2 passed, 5 deselected`)
4. `python3 -m pytest -q tests/test_merlin_mock_capabilities_server.py tests/test_run_merlin_cp6_local_checks.py`
   - Outcome: PASS (`3 passed`)
5. `python3 scripts/run_merlin_cp6_local_checks.py --output-json artifacts/diagnostics/merlin_cp6_local_checks_2026-02-28.json`
   - Outcome: PASS (`artifacts/diagnostics/merlin_cp6_local_checks_2026-02-28.json`, overall `PASS`)
6. Live payload gate check:
   - Command: `python3 scripts/merlin_research_manager_consumer.py --capabilities-json ../artifacts/diagnostics/merlin_operations_capabilities_probe_2026-02-28_refresh.json`
   - Outcome: PASS (`research_manager_enabled=true`, `selected_path=research_manager`)

## FOLLOW_UP_2026_03_01_VERIFICATION

1. Bounded CP6 local test lane rerun:
   - `timeout 300s python3 -m pytest -q tests/test_merlin_research_manager_consumer.py tests/test_merlin_mock_capabilities_server.py tests/test_run_merlin_cp6_local_checks.py`
   - Outcome: PASS (`10 passed`)
2. Bounded full local-check runner rerun:
   - `timeout 300s python3 scripts/run_merlin_cp6_local_checks.py --output-json artifacts/diagnostics/merlin_cp6_local_checks_2026-03-01.json`
   - Outcome: PASS (`artifacts/diagnostics/merlin_cp6_local_checks_2026-03-01.json`, overall `PASS`)
3. Direct live payload gate parity check:
   - `timeout 120s python3 scripts/merlin_research_manager_consumer.py --capabilities-json ../artifacts/diagnostics/merlin_operations_capabilities_probe_2026-02-28_refresh.json`
   - Outcome: PASS (`research_manager_enabled=true`, `selected_path=research_manager`, `missing_core_operations=[]`)
