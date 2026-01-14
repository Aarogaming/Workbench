. "$PSScriptRoot\log_helper.ps1"

$patterns = @(
    "AI\w{20,}", "sk-[\w-]{20,}", "ghp_[\w]{36}", "AKIA[\w]{16}"
)

$baseDir = "D:\Dev library"
$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    Write-AASLog "Scanning $p for secrets..." "INFO"
    foreach ($pattern in $patterns) {
        $matches = Get-ChildItem $p.FullName -Recurse -File | Select-String -Pattern $pattern -Exclude "*.exe", "*.dll", "*.png", "*.jpg", "*.ico"
        if ($matches) {
            foreach ($m in $matches) {
                Write-AASLog "Potential secret found in $($m.Path) at line $($m.LineNumber)" "ERROR"
            }
        }
    }
}

Write-AASLog "Secret scan complete." "SUCCESS"
