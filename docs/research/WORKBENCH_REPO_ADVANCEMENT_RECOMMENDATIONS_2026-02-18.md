# Workbench Repo Advancement Recommendations

Date: 2026-02-18  
Scope: `Workbench/**`  
Status: Research queue (bin overflow while `WB-SUG` cap remains `100`)

## Objective

Capture repo-specific advancement, enhancement, optimization, and tooling recommendations grounded in current Workbench codepaths.

## Promotion Snapshot

Promoted into active bin on 2026-02-18:

1. `REC-001` -> `WB-SUG-143`
2. `REC-002` -> `WB-SUG-144`
3. `REC-003` -> `WB-SUG-145`
4. `REC-004` -> `WB-SUG-146`
5. `REC-005` -> `WB-SUG-147`
6. `REC-006` -> `WB-SUG-148`
7. `REC-007` -> `WB-SUG-149`
8. `REC-008` -> `WB-SUG-150`
9. `REC-010` -> `WB-SUG-151`
10. `REC-017` -> `WB-SUG-152`

## Recommendations Queue

| ID | Recommendation | Primary touchpoints | Why this is high-value now | Sources |
| --- | --- | --- | --- | --- |
| `REC-001` | Add repo-local `pyproject.toml` for tool and dependency contracts | `pyproject.toml` (new), `.github/workflows/ci.yml`, `.pre-commit-config.yaml` | Current test execution depends on superproject-level `pytest.ini`; local tool contracts improve reproducibility and portability. | https://docs.astral.sh/uv/, https://docs.pytest.org/en/stable/reference/customize.html |
| `REC-002` | Adopt `uv` lockfile workflow for deterministic CI installs | `uv.lock` (new), `.github/workflows/ci.yml` | CI currently installs floating deps (`pip install pytest requests`); lock-based installs reduce drift. | https://docs.astral.sh/uv/ |
| `REC-003` | Add `ruff` lint/format checks in pre-commit and CI | `.pre-commit-config.yaml`, `scripts/run_quality_gates.py` | Existing hooks cover size/secrets only; static lint catches quality regressions earlier. | https://docs.astral.sh/ruff/configuration/ |
| `REC-004` | Add selective strict type-checking (mypy/pyright) for high-risk modules | `plugins/mcp_auth.py`, `plugins/workflow_engine.py`, `scripts/validate_workspace_index.py` | These modules drive auth/control-plane behavior; stronger type contracts reduce runtime defects. | https://mypy.readthedocs.io/en/stable/existing_code.html, https://github.com/microsoft/pyright/blob/main/docs/configuration.md |
| `REC-005` | Enforce branch coverage target for critical modules | `.github/workflows/ci.yml`, `tests/` | Unit tests are broad for scripts, but branch-level quality goals are not enforced. | https://coverage.readthedocs.io/en/5.5/branch.html, https://pytest-cov.readthedocs.io/en/latest/ |
| `REC-006` | Add direct unit suites for plugin modules, not only checker scripts | `tests/test_workflow_engine*.py` (new), `tests/test_mcp_auth*.py` (new), `tests/test_gui_hub_connector*.py` (new) | Most current tests validate policy/checker scripts; runtime plugin logic has weaker direct coverage. | https://docs.pytest.org/en/stable/ |
| `REC-007` | Add property-based tests for workflow state transitions | `plugins/workflow_engine.py`, `tests/test_workflow_engine_properties.py` (new) | Workflow pause/resume/schedule state machine is ideal for invariant-based testing. | https://hypothesis.readthedocs.io/en/latest/quickstart.html |
| `REC-008` | Standardize JSON schema validation for emitted report artifacts | `docs/reports/*.json`, `scripts/*report*.py` | Many report contracts are validated ad hoc; schema validation improves interoperability and safety. | https://json-schema.org/learn/getting-started-step-by-step |
| `REC-009` | Introduce structured model parsing for JSON payloads | `plugins/mcp_auth.py`, `scripts/generate_run_summary.py`, `scripts/validate_fetch_index.py` | Typed model parsing reduces unchecked dict access and shape drift. | https://docs.pydantic.dev/latest/concepts/models/ |
| `REC-010` | Add resilient HTTP client policy (timeouts + retries + backoff) | `plugins/mcp_auth.py`, `scripts/check_scorecard_threshold.py` | External calls exist; retry/backoff and explicit timeout standards should be consistent. | https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts, https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.retry.Retry |
| `REC-011` | Add circuit-breaker/cooldown around repeated auth verification failures | `plugins/mcp_auth.py` | Repeated failing verify calls can create noisy retries and degraded UX. | https://martinfowler.com/bliki/CircuitBreaker.html |
| `REC-012` | Make `datetime` usage consistently timezone-aware | `plugins/gui_hub_connector.py`, `plugins/log_export_manager.py`, `plugins/periodic_check_workmanager.py` | Current mixed use of naive UTC datetimes complicates long-run comparisons and serialization safety. | https://docs.python.org/3/library/datetime.html#aware-and-naive-objects |
| `REC-013` | Replace unbounded in-memory histories with bounded deques/retention windows | `plugins/gui_hub_connector.py`, `plugins/log_export_manager.py`, `plugins/workflow_engine.py` | Several lists can grow indefinitely during long agent sessions. | https://docs.python.org/3/library/collections.html#collections.deque |
| `REC-014` | Add optional disk-backed cache for API responses and logs | `plugins/gui_hub_connector.py`, `plugins/log_export_manager.py` | Memory-only caches/log stores lose data on restart and can inflate RAM usage. | https://grantjenks.com/docs/diskcache/ |
| `REC-015` | Add streaming/chunked export for large log payloads | `plugins/log_export_manager.py` | Current export flow is in-memory list-based and can spike memory for large bundles. | https://docs.python.org/3/library/json.html |
| `REC-016` | Add subprocess timeout wrappers and centralized runner utility | `scripts/eval_report.py`, `scripts/test_changed.py`, `scripts/run_quality_gates.py` | Multiple subprocess calls run without explicit timeout policy. | https://docs.python.org/3/library/subprocess.html#subprocess.run |
| `REC-017` | Split `validate_workspace_index.py` into focused modules/subcommands | `scripts/validate_workspace_index.py` | The script is large (`~1800` lines) and combines concerns, raising maintenance risk. | https://docs.python.org/3/library/argparse.html#sub-commands |
| `REC-018` | Add incremental mode to heavy index validation (changed-files fast path) | `scripts/validate_workspace_index.py`, `scripts/test_changed.py` | Full scans are expensive for small diffs; incremental mode improves dev feedback loop. | https://git-scm.com/docs/git-diff |
| `REC-019` | Add benchmark harness for expensive scripts | `scripts/validate_workspace_index.py`, `scripts/run_quality_gates.py`, `tests/benchmarks/` (new) | Performance regressions are hard to spot without repeatable benchmarks. | https://pytest-benchmark.readthedocs.io/ |
| `REC-020` | Add OpenTelemetry spans around quality-gate execution and fetch/index steps | `scripts/run_quality_gates.py`, `scripts/fetch_workbench_artifacts.sh`, `scripts/validate_fetch_index.py` | Existing policy references telemetry but script-level instrumentation is still limited. | https://opentelemetry.io/docs/languages/python/instrumentation/ |
| `REC-021` | Normalize CLI output contract (`--json-out` + machine-readable summary) across scripts | `scripts/check_*.py`, `scripts/generate_*.py` | Mixed output formats slow automation composition and downstream parsing. | https://docs.python.org/3/library/argparse.html |
| `REC-022` | Add shared script helper library for path resolution, JSON I/O, and consistent exit reporting | `scripts/_common.py` (new), `scripts/check_*.py` | Many scripts duplicate root resolution and JSON parse patterns. | https://docs.python.org/3/library/pathlib.html |
| `REC-023` | Add deterministic fixtures/factories for repeated report/schema tests | `tests/fixtures/` (new), `tests/test_check_*` | Current tests often inline payload scaffolding; fixtures reduce duplication and drift. | https://docs.pytest.org/en/stable/how-to/fixtures.html |
| `REC-024` | Add cross-platform shell parity checks (`bash` + PowerShell helper paths) | `scripts/fetch_workbench_artifacts.sh`, `*.ps1` helpers | Repo includes both shell ecosystems; parity checks reduce platform-specific breakage. | https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstrategymatrix |
| `REC-025` | Introduce SARIF-producing static checks for plugin risk patterns | `scripts/check_plugin_contracts.py`, `.github/workflows/codeql-actions-security.yml` | Structured security findings integrate better with code scanning surfaces. | https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github |
| `REC-026` | Add dependency freshness SLA report (age + outdated deltas) | `scripts/generate_dependency_inventory.py`, `docs/reports/dependency_snapshot.json` | Snapshot exists; freshness/risk trend overlay is missing. | https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain |
| `REC-027` | Add automated stale-report detection for key research/ops docs | `docs/research/*.md`, `scripts/check_chimera_packets.py` | Some governance docs benefit from explicit max-age checks. | https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands |
| `REC-028` | Add schema-compatible compact mode for large reports | `scripts/generate_run_summary.py`, `scripts/generate_dependency_inventory.py` | Large JSON artifacts can affect diff readability and artifact transfer size. | https://docs.python.org/3/library/json.html |
| `REC-029` | Harden plugin manifest validation with JSON Schema and versioned contract | `scripts/check_plugin_contracts.py`, `plugins/*/manifest.json` | Current validation is custom and field-by-field; schema formalization improves extensibility. | https://json-schema.org/learn/getting-started-step-by-step |
| `REC-030` | Add token-budget and runtime-budget checks for long-running local script chains | `scripts/run_quality_gates.py`, `scripts/eval_report.py` | Large chained checks can exceed developer/local CI budgets without early warning. | https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions |

## Next-Step Rotation Rule

While `docs/SUGGESTIONS_BIN.md` remains capped at `100` `WB-SUG` entries, promote items from this queue by:

1. Archiving an already-implemented low-signal `WB-SUG` row into a dedicated historical archive.
2. Adding the promoted recommendation as a new `WB-SUG` entry with local touchpoints and verification plan.
3. Regenerating and sync-checking `docs/reports/suggestions_bin.json`.
