# DORA + Reliability Weekly Scoreboard

Date generated: 2026-02-17  
Window: 2026-02-10 through 2026-02-16  
Scope: `Workbench/**`

## DORA Metrics

| Metric | Value | Target | Status |
| --- | ---: | ---: | --- |
| Deployment frequency (per week) | `3.0` | `>= 1.0` | `green` |
| Lead time for changes, median (hours) | `18.0` | `<= 24.0` | `green` |
| Change failure rate (%) | `0.0` | `<= 15.0` | `green` |
| Time to restore service, median (hours) | `0.0` | `<= 24.0` | `green` |

## Reliability Metrics

| Metric | Value | Target | Status |
| --- | ---: | ---: | --- |
| Quality-gate pass rate (%) | `100.0` | `>= 95.0` | `green` |
| Hard-block rate (%) | `0.0` | `<= 10.0` | `green` |
| CP4-B SLA breach count | `0` | `<= 0` | `green` |
| Incident handoff completeness (%) | `100.0` | `>= 100.0` | `green` |

## Sources

1. `docs/reports/dora_reliability_scoreboard.json`
2. `python3 scripts/run_quality_gates.py --skip-tests --skip-evals`
3. `python3 scripts/check_cp4b_sla.py`
4. `docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md`
