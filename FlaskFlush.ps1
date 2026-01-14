. "$PSScriptRoot\log_helper.ps1"

$baseDir = "D:\Dev library"
$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    $venvs = Get-ChildItem $p.FullName -Directory | Where-Object { $_.Name -match "^\.venv" }
    foreach ($v in $venvs) {
        $lastWrite = $v.LastWriteTime
        if ($lastWrite -lt (Get-Date).AddMonths(-3)) {
            Write-AASLog "Found old venv in $($p.Name): $($v.Name) (Last modified: $lastWrite)" "WARN"
            # Remove-Item -Recurse -Force $v.FullName
        }
    }
}

Write-AASLog "Venv audit complete. (Deletion commented out for safety)" "SUCCESS"
