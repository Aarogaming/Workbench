. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

function Check-Policy {
    param([string]$ProjectName)
    
    $repo = Get-ProjectRoot -ProjectName $ProjectName
    if (-not $repo) { return }

    $envFile = Join-Path $repo ".env"
    if (Test-Path $envFile) {
        $content = Get-Content $envFile
        if ($content -match "ALLOW_LIVE_AUTOMATION=false") {
            Write-AASLog "WARNING: Live automation DISABLED in $ProjectName" "WARN"
        } else {
            Write-AASLog "Policy check passed for $ProjectName (Live automation enabled)" "SUCCESS"
        }
    }
}

$projects = @("AaroneousAutomationSuite", "Maelstrom")
foreach ($p in $projects) {
    Check-Policy -ProjectName $p
}
