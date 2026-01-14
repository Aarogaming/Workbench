. "$PSScriptRoot\log_helper.ps1"

param(
    [string]$BaseUrl = "http://localhost:9411"
)

$endpoints = @("/healthz", "/bot/api/status")

foreach ($ep in $endpoints) {
    $url = $BaseUrl + $ep
    Write-AASLog "Probing $url..." "INFO"
    try {
        $resp = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 5
        Write-AASLog "Success: $url is UP" "SUCCESS"
        $resp | ConvertTo-Json | Write-Host
    }
    catch {
        Write-AASLog "Failed to reach $url" "ERROR"
    }
}
