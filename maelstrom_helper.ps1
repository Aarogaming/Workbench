. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

function Run-MaelstromTask {
    param([string]$TaskName)
    
    $repo = Get-ProjectRoot -ProjectName "AaroneousAutomationSuite"
    $maelstrom = Join-Path $repo "Maelstrom"
    
    if (Test-Path $maelstrom) {
        Write-AASLog "Running Maelstrom task: $TaskName" "INFO"
        # Logic to interface with Maelstrom components
    } else {
        Write-AASLog "Maelstrom not found in AAS repo." "WARN"
    }
}

Export-ModuleMember -Function Run-MaelstromTask
