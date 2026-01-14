. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

$logFiles = @()

$projects = @("AaroneousAutomationSuite", "MyFortress", "Merlin")
foreach ($p in $projects) {
    $repo = Get-ProjectRoot -ProjectName $p
    if ($repo) {
        $logDir = Join-Path $repo "logs"
        if (Test-Path $logDir) {
            $latestLog = Get-ChildItem $logDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($latestLog) {
                $logFiles += $latestLog.FullName
            }
        }
    }
}

if ($logFiles.Count -eq 0) {
    Write-AASLog "No log files found to tail." "WARN"
    return
}

Write-AASLog "Tailing $($logFiles.Count) log files..." "SUCCESS"
Get-Content -Path $logFiles -Wait -Tail 10
