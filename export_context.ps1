. "$PSScriptRoot\log_helper.ps1"

$baseDir = "D:\Dev library"
$exportFile = Join-Path $PSScriptRoot "FULL_CONTEXT_PACK.md"

$content = "# AAS Full Suite Context Pack`n`n"
$content += "Generated on: $(Get-Date)`n`n"

$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    $content += "================================================================================`n"
    $content += "PROJECT: $($p.Name)`n"
    $content += "================================================================================`n`n"
    
    $readme = Join-Path $p.FullName "README.md"
    if (Test-Path $readme) {
        $content += Get-Content $readme -Raw
        $content += "`n`n"
    }
    
    $content += "DIRECTORY STRUCTURE:`n"
    $files = Get-ChildItem $p.FullName -Depth 1 | Select-Object -ExpandProperty FullName
    foreach ($f in $files) {
        $content += "- $f`n"
    }
    $content += "`n"
}

Set-Content $exportFile $content
Write-AASLog "Exported full context pack to $exportFile" "SUCCESS"
