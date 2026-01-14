. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

function Sync-Config {
    param([string]$ProjectName)
    
    $repoPath = Get-ProjectRoot -ProjectName $ProjectName
    if (-not $repoPath) {
        Write-AASLog "Project $ProjectName not found." "ERROR"
        return
    }

    $exampleEnv = Join-Path $repoPath ".env.example"
    $actualEnv = Join-Path $repoPath ".env"

    if (Test-Path $exampleEnv) {
        if (-not (Test-Path $actualEnv)) {
            Write-AASLog "Creating .env from .env.example for $ProjectName" "INFO"
            Copy-Item $exampleEnv $actualEnv
        } else {
            Write-AASLog ".env already exists for $ProjectName. Skipping." "SUCCESS"
        }
    } else {
        Write-AASLog "No .env.example found in $ProjectName" "WARN"
    }
}

$projects = @("AaroneousAutomationSuite", "MyFortress", "AndroidApp")
foreach ($p in $projects) {
    Sync-Config -ProjectName $p
}
