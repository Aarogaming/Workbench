# Plugin Contract Ownership

## Ownership model

- Default owner: `AAS`
- Contract authority: manifest schema (`PluginManifest`) + `extensions.aas.exports`
- Runtime contract: `Plugin.commands()` must expose declared capabilities

## Validation commands

1. Contract audit:
   - `python3 scripts/check_plugin_contracts.py`
2. Targeted test execution for changed files:
   - `python3 scripts/test_changed.py --fallback-all`
3. Full quality gate:
   - `python3 scripts/run_quality_gates.py`

## Expected plugin package structure

Each plugin directory under `plugins/` should include:

1. `manifest.json` with:
   - `schemaName: PluginManifest`
   - `entry`
   - `capabilities`
   - `extensions.aas.exports`
2. Entry file (typically `plugin.py`) containing:
   - `class Plugin`
   - `commands()` method

## Escalation

Escalate to maintainers when:

1. A capability is exported by multiple plugins.
2. Manifest capabilities and exports diverge.
3. Entry points are missing or fail static contract checks.
