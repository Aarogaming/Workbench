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

# GUI tasks often involve Tauri or Tray apps
$tauri = Join-Path $repo "src-tauri"
if (Test-Path $tauri) {
    Write-AASLog "Found Tauri project in $repo" "INFO"
    Push-Location $repo
    try {
        if ($Args.Count -eq 0) {
            & npm run tauri dev
        } else {
            & npm run tauri @Args
        }
    }
    finally {
        Pop-Location
    }
} else {
    Write-AASLog "No Tauri project found. Falling back to generic GUI task." "WARN"
}
