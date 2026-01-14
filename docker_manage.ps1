. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("up", "down", "restart", "ps")]
    [string]$Action,
    [string]$ProjectName
)

function Manage-Docker {
    param([string]$PName, [string]$Act)
    
    $repoPath = Get-ProjectRoot -ProjectName $PName
    if (-not $repoPath) { return }

    $dockerFile = Join-Path $repoPath "docker-compose.yml"
    if (Test-Path $dockerFile) {
        Write-AASLog "Running docker-compose $Act for $PName" "INFO"
        Push-Location $repoPath
        try {
            & docker-compose $Act
        }
        finally {
            Pop-Location
        }
    } else {
        Write-AASLog "No docker-compose.yml found in $PName" "WARN"
    }
}

if ($ProjectName) {
    Manage-Docker -PName $ProjectName -Act $Action
} else {
    $projects = @("AaroneousAutomationSuite", "MyFortress")
    foreach ($p in $projects) {
        Manage-Docker -PName $p -Act $Action
    }
}
