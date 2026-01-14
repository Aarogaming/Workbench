. "$PSScriptRoot\log_helper.ps1"

$baseDir = "D:\Dev library"
$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    $gitDir = Join-Path $p.FullName ".git"
    if (Test-Path $gitDir) {
        Write-Host "`n--- $($p.Name) ---" -ForegroundColor Cyan
        Push-Location $p.FullName
        try {
            $branch = git rev-parse --abbrev-ref HEAD
            $status = git status --short
            Write-Host "Branch: $branch"
            if ($status) {
                Write-Host "Changes:`n$status" -ForegroundColor Yellow
            } else {
                Write-Host "Clean" -ForegroundColor Green
            }
        }
        finally {
            Pop-Location
        }
    }
}
