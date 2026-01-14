. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

$baseDir = "D:\Dev library"
$indexFile = Join-Path $PSScriptRoot "INDEX.md"

$content = "# AAS Project Index`n`n"
$content += "Generated on: $(Get-Date)`n`n"

$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    $readme = Join-Path $p.FullName "README.md"
    if (Test-Path $readme) {
        $content += "## [$($p.Name)](../$($p.Name)/README.md)`n"
        $firstLine = Get-Content $readme -TotalCount 5 | Select-String "Purpose|Description"
        if ($firstLine) {
            $content += "$($firstLine)`n"
        }
        $content += "`n"
    }
}

Set-Content $indexFile $content
Write-AASLog "Generated project index at $indexFile" "SUCCESS"
