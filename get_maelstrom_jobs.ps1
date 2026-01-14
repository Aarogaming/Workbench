. "$PSScriptRoot\log_helper.ps1"

param(
    [string]$BaseUrl = "http://localhost:9411",
    [string]$Token
)

$url = $BaseUrl + "/bot/api/jobs"
Write-AASLog "Fetching jobs from $url..." "INFO"

$headers = @{}
if ($Token) {
    $headers["Authorization"] = "Bearer $Token"
}

try {
    $jobs = Invoke-RestMethod -Uri $url -Method Get -Headers $headers -TimeoutSec 5
    $jobs | Format-Table -Property id, status, type, created_at
}
catch {
    Write-AASLog "Failed to fetch jobs. Ensure token is provided if required." "ERROR"
}
