. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [string]$Configuration = "Debug"
)

$projects = @("AaroneousAutomationSuite", "MyFortress", "AndroidApp")

foreach ($p in $projects) {
    $repo = Get-ProjectRoot -ProjectName $p
    if (-not $repo) { continue }

    Write-AASLog "Running tests for $p..." "INFO"
    Push-Location $repo
    try {
        if ($p -eq "AaroneousAutomationSuite") {
            $python = Get-PythonPath -RepoPath $repo
            & $python -m pytest
            & dotnet test --configuration $Configuration
        } elseif ($p -eq "MyFortress") {
            $python = Get-PythonPath -RepoPath $repo
            & $python -m pytest
        } elseif ($p -eq "AndroidApp") {
            & .\gradlew.bat test
        }
    }
    catch {
        Write-AASLog "Tests failed for $p" "ERROR"
    }
    finally {
        Pop-Location
    }
}
