. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod", "experimental")]
    [string]$Profile
)

function Switch-ProjectProfile {
    param([string]$ProjectName, [string]$Prof)
    
    $repo = Get-ProjectRoot -ProjectName $ProjectName
    if (-not $repo) { return }

    $envFile = Join-Path $repo ".env"
    if (Test-Path $envFile) {
        Write-AASLog "Switching $ProjectName to $Prof profile..." "INFO"
        $content = Get-Content $envFile
        if ($content -match "MAELSTROM_PROFILE=") {
            $content = $content -replace "MAELSTROM_PROFILE=.*", "MAELSTROM_PROFILE=$Prof"
        } else {
            $content += "`nMAELSTROM_PROFILE=$Prof"
        }
        Set-Content $envFile $content
        Write-AASLog "Profile updated for $ProjectName" "SUCCESS"
    }
}

$projects = @("AaroneousAutomationSuite", "Maelstrom", "MyFortress")
foreach ($p in $projects) {
    Switch-ProjectProfile -ProjectName $p -Prof $Profile
}
