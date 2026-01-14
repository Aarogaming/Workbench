# ChoreBoy (Dev-only)

Console tool to verify Aaroneous Automation Suite core behavior (policy enforcement, executor selection, plugin gating, failure safety) with no UI and no live execution.

## Build
```pwsh
dotnet build DevTools/ChoreBoy/ChoreBoy.csproj -c Debug
```

## Run
```pwsh
dotnet run --project DevTools/ChoreBoy/ChoreBoy.csproj
```

## What it does
- Writes test-local policy files in the tool’s cache (under its bin folder).
- Reloads policy, executor, and plugins via reflection (no runtime code changes).
- Installs sample plugin manifests in the test-local plugin root:
  - SampleOverlay (allowed)
  - SampleLiveIntegration (blocked when live is disabled)
  - CorruptPlugin (invalid manifest)
- Executes functional scenarios and prints PASS/FAIL lines, then a summary.

## Safety
- No WinForms, no live execution, no OS input.
- Uses the tool’s own cache/plugins folder (does not touch user data).
- Missing/failed scenarios are reported; process exits normally.
