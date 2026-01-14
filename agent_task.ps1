. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
)

$repo = Get-ProjectRoot -ProjectName "lm-studio-parallel-agents"
if (-not $repo) {
    Write-AASLog "lm-studio-parallel-agents repo not found." "ERROR"
    return
}

$python = Get-PythonPath -RepoPath $repo

Write-AASLog "Running Parallel Agent task in $repo" "INFO"

Push-Location $repo
try {
    if ($Args.Count -eq 0) {
        & $python "simple_lm_studio_example.py"
    } else {
        & $python @Args
    }
}
finally {
    Pop-Location
}
