# Health Protocol Coverage Maintenance

## Purpose

This runbook documents the reusable automation for manager/coordinator health-protocol coverage tracking.

The canonical script lives in Workbench:

- `scripts/maintain_health_protocol_coverage.py`

It scans `AaroneousAutomationSuite/core/` for concrete `*Manager` and `*Coordinator` classes,
verifies `LifecycleStateMixin` adoption, and optionally refreshes Wave 2 documentation counts.

## What it checks

- Total discovered manager/coordinator classes
- Concrete classes (non-`ABC`)
- Adopted classes (`LifecycleStateMixin` present in base list)
- Missing classes (concrete classes without `LifecycleStateMixin`)
- Coverage percentage

## Standard usage

From `Workbench/`:

- Audit only:
  - `python scripts/maintain_health_protocol_coverage.py --repo-root "c:\Dev library\AaroneousAutomationSuite"`

- Fail CI when any concrete class is missing the mixin:
  - `python scripts/maintain_health_protocol_coverage.py --repo-root "c:\Dev library\AaroneousAutomationSuite" --fail-if-missing`

- Refresh Wave 2 docs automatically:
  - `python scripts/maintain_health_protocol_coverage.py --repo-root "c:\Dev library\AaroneousAutomationSuite" --update-docs`

- Dry run doc refresh:
  - `python scripts/maintain_health_protocol_coverage.py --repo-root "c:\Dev library\AaroneousAutomationSuite" --update-docs --dry-run`

- Write machine-readable report JSON:
  - `python scripts/maintain_health_protocol_coverage.py --repo-root "c:\Dev library\AaroneousAutomationSuite" --output-json "artifacts/health_protocol_coverage.json"`

## Exit codes

- `0`: success
- `2`: at least one concrete class is missing `LifecycleStateMixin` (when `--fail-if-missing` is set)

## Updated documentation targets

When `--update-docs` is enabled, the script updates:

- `WAVE2_COMPLETION_REPORT_2026_03_10.md`
- `DUPLICATION_AUDIT_WAVE2_2026_03_09.md`

## Recommended integration

- Add a lightweight CI check in Workbench and/or AAS governance workflows using `--fail-if-missing`.
- Keep `--update-docs` as a release/handoff step (or nightly maintenance) rather than on every PR.
