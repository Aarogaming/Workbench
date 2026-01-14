. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
)

$repo = Get-ProjectRoot -ProjectName "AndroidApp"
if (-not $repo) {
    Write-AASLog "AndroidApp repo not found." "ERROR"
    return
}

$gradlew = Join-Path $repo "gradlew.bat"
if (-not (Test-Path $gradlew)) {
    Write-AASLog "gradlew.bat not found in $repo" "ERROR"
    return
}

Write-AASLog "Running Android task in $repo" "INFO"

Push-Location $repo
try {
    if ($Args.Count -eq 0) {
        & .\gradlew.bat assembleDebug
    } else {
        & .\gradlew.bat @Args
    }
}
finally {
    Pop-Location
}
