. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskDescription
)

$repo = Get-ProjectRoot -ProjectName "lm-studio-parallel-agents"
if (-not $repo) { return }

$python = Get-PythonPath -RepoPath $repo

Write-AASLog "Executing parallel task: $TaskDescription" "INFO"

Push-Location $repo
try {
    # Using the bridge to execute a task via LM Studio agents
    & $python "opencode_lmstudio_bridge.py" --task "$TaskDescription"
}
finally {
    Pop-Location
}
