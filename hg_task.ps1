. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
)

$repo = Get-ProjectRoot -ProjectName "MyFortress"
if (-not $repo) {
    Write-AASLog "MyFortress repo not found." "ERROR"
    return
}

$python = Get-PythonPath -RepoPath $repo

Write-AASLog "Running MyFortress task with $python" "INFO"

Push-Location $repo
try {
    if ($Args.Count -eq 0) {
        # Default to running the service
        & $python -m gateway
    } else {
        & $python -m gateway.cli @Args
    }
}
finally {
    Pop-Location
}
