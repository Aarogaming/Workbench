. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
)

$repo = Get-ProjectRoot -ProjectName "AaroneousAutomationSuite"
if (-not $repo) {
    Write-AASLog "AAS repo not found." "ERROR"
    return
}

$python = Get-PythonPath -RepoPath $repo

if ($Args.Contains("--interactive")) {
    Write-AASLog "Launching AAS Hub in Interactive Mode..." "SUCCESS"
    # Logic for interactive selection could go here
}

Push-Location $repo
try {
    & $python "hub.py" @Args
}
finally {
    Pop-Location
}
