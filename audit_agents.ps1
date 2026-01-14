. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

$repo = Get-ProjectRoot -ProjectName "lm-studio-parallel-agents"
if (-not $repo) { return }

Write-AASLog "Auditing Parallel Agent configurations in $repo" "INFO"

$configFile = Join-Path $repo "opencode_lmstudio.json"
if (Test-Path $configFile) {
    $config = Get-Content $configFile | ConvertFrom-Json
    Write-Host "Configured Agents:" -ForegroundColor Cyan
    $config.agents | Select-Object -Property type, model, role | Format-Table
} else {
    Write-AASLog "opencode_lmstudio.json not found." "WARN"
}
