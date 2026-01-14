. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
)

$repo = Get-ProjectRoot -ProjectName "Merlin"
if (-not $repo) {
    Write-AASLog "Merlin repo not found." "ERROR"
    return
}

$python = Get-PythonPath -RepoPath $repo

Push-Location $repo
try {
    if ($Args.Count -eq 0) {
        Write-AASLog "Launching Merlin Unified Launcher in $repo" "INFO"
        & $python merlin_launcher.py
    } else {
        Write-AASLog "Executing Merlin CLI: merlin_cli.py $($Args -join ' ')" "INFO"
        & $python merlin_cli.py @Args
    }
}
finally {
    Pop-Location
}
