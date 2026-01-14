. "$PSScriptRoot\log_helper.ps1"

param(
    [string]$BaseUrl = "http://localhost:1234"
)

Write-AASLog "Checking LM Studio health at $BaseUrl..." "INFO"

try {
    $models = Invoke-RestMethod -Uri ($BaseUrl + "/v1/models") -Method Get -TimeoutSec 5
    Write-AASLog "LM Studio is ACTIVE" "SUCCESS"
    Write-Host "Loaded Models:" -ForegroundColor Cyan
    $models.data | Select-Object -Property id, owned_by | Format-Table
}
catch {
    Write-AASLog "LM Studio is NOT reachable at $BaseUrl" "ERROR"
}
