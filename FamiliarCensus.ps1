. "$PSScriptRoot\log_helper.ps1"

param(
    [string]$BaseUrl = "http://localhost:3000"
)

Write-AASLog "Querying AAS Agent status at $BaseUrl..." "INFO"

try {
    $status = Invoke-RestMethod -Uri ($BaseUrl + "/api/agents/status") -Method Get -TimeoutSec 5
    Write-AASLog "AAS Hub is ACTIVE" "SUCCESS"
    $status | ConvertTo-Json | Write-Host
}
catch {
    Write-AASLog "AAS Hub is NOT reachable at $BaseUrl" "ERROR"
}
