. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

$repo = Get-ProjectRoot -ProjectName "AaroneousAutomationSuite"
if (-not $repo) { return }

$dbPath = Join-Path $repo "artifacts\bot\db\maelstrombot.db"

if (Test-Path $dbPath) {
    Write-AASLog "Backing up and resetting Maelstrom DB at $dbPath" "WARN"
    Copy-Item $dbPath ($dbPath + ".bak")
    Remove-Item $dbPath
    Write-AASLog "DB reset. Run MaelstromBot.Server with --init-admin-key to re-initialize." "SUCCESS"
} else {
    Write-AASLog "Maelstrom DB not found at $dbPath" "INFO"
}
