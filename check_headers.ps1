. "$PSScriptRoot\log_helper.ps1"

$header = "# Copyright (c) AAS. All rights reserved."

function Check-Header {
    param([string]$FilePath)
    $content = Get-Content $FilePath -TotalCount 1
    if ($content -notmatch "Copyright") {
        Write-AASLog "Missing license header in $FilePath" "WARN"
    }
}

$baseDir = "D:\Dev library"
$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    $files = Get-ChildItem $p.FullName -Recurse -File -Include "*.py", "*.ps1", "*.cs", "*.js", "*.ts"
    foreach ($f in $files) {
        Check-Header -FilePath $f.FullName
    }
}

Write-AASLog "Header check complete." "SUCCESS"
