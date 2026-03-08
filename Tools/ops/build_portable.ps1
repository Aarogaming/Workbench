param(
    [switch]$IncludeSamples
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Summary {
    param($Included, $Excluded)
    Write-Host "`n=== Portable Build Summary ==="
    Write-Host "Included:"
    $Included | ForEach-Object { Write-Host "  - $_" }
Write-Host "Excluded:"
    $Excluded | ForEach-Object { Write-Host "  - $_" }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsRoot = Resolve-Path (Join-Path $scriptDir "..")
$aasRoot = Resolve-Path (Join-Path $toolsRoot "..")
$maelstromRoot = Join-Path $aasRoot "Maelstrom"
Push-Location $maelstromRoot

$artifacts = Join-Path $aasRoot "artifacts/portable"
if (Test-Path $artifacts) { Remove-Item -Recurse -Force $artifacts }
New-Item -ItemType Directory -Path $artifacts | Out-Null

Write-Host "Building ProjectMaelstrom (Release)..."
dotnet build ProjectMaelstrom.sln -c Release

Write-Host "Publishing ProjectMaelstrom (framework-dependent)..."
$publishDir = Join-Path $artifacts "publish"
dotnet publish src/ProjectMaelstrom/ProjectMaelstrom.csproj -c Release -o $publishDir --no-self-contained

# Copy only runtime essentials
$includeList = @(
    "ProjectMaelstrom.exe",
    "ProjectMaelstrom.dll",
    "ProjectMaelstrom.runtimeconfig.json",
    "execution_policy.conf"
)

Write-Host "Collecting runtime files..."
$files = Get-ChildItem $publishDir
foreach ($item in $files) {
    if ($includeList -contains $item.Name -or $item.Extension -in @(".dll", ".json", ".config")) {
        Copy-Item $item.FullName -Destination $artifacts -Force
    }
}

# Ensure default policy exists (live-enabled default policy)
$policyPath = Join-Path $artifacts "execution_policy.conf"
if (-not (Test-Path $policyPath)) {
    Set-Content $policyPath "ALLOW_LIVE_AUTOMATION=true`nEXECUTION_PROFILE=AcademicSimulation`n"
}

# Plugins folder
$pluginDest = Join-Path $artifacts "plugins"
New-Item -ItemType Directory -Path $pluginDest -Force | Out-Null

if ($IncludeSamples) {
    $samples = Join-Path $maelstromRoot "plugins/_samples"
    if (Test-Path $samples) {
        Copy-Item -Recurse -Force $samples $pluginDest
    }
}

# Exclusions
$excluded = @(
    "Workbench/Tools/DevTools/**",
    "*TestRunner*",
    "plugins/_samples (unless -IncludeSamples)",
    "publish intermediate"
)

$included = @(
    "Core app binaries (Release, framework-dependent)",
    "execution_policy.conf (live-enabled defaults)",
    "plugins/ (empty by default)"
)
if ($IncludeSamples) { $included += "plugins/_samples (SampleReplayAnalyzer, etc.)" }

Write-Summary -Included $included -Excluded $excluded
Write-Host "`nPortable output: $artifacts"

Pop-Location
