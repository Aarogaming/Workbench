. "$PSScriptRoot\log_helper.ps1"

param(
    [Parameter(Mandatory=$true)]
    [string]$Query
)

$baseDir = "D:\Dev library"
$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

Write-AASLog "Searching for '$Query' across all projects..." "INFO"

foreach ($p in $projects) {
    Write-Host "`n--- $($p.Name) ---" -ForegroundColor Cyan
    $results = Get-ChildItem $p.FullName -Recurse -File | 
               Where-Object { $_.FullName -notmatch "node_modules|\.venv|bin|obj|dist|build|\.git" } |
               Select-String -Pattern $Query
    
    if ($results) {
        foreach ($r in $results) {
            $relPath = $r.Path.Replace($baseDir, "")
            Write-Host "$relPath : $($r.LineNumber) : $($r.Line.Trim())"
        }
    } else {
        Write-Host "No matches found." -ForegroundColor Gray
    }
}
