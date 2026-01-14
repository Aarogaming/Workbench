# Simple installer for Maelstrom (x64, self-contained).
param(
    [string]$Source,
    [string]$Destination = "$env:LOCALAPPDATA\\ProjectMaelstrom"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsRoot = Resolve-Path (Join-Path $scriptDir "..")
$aasRoot = Resolve-Path (Join-Path $toolsRoot "..")
$maelstromRoot = Join-Path $aasRoot "Maelstrom"
if (-not $Source) {
    $Source = Join-Path $maelstromRoot "src/ProjectMaelstrom/publish/win-x64"
}

Write-Host "Source: $Source"
Write-Host "Destination: $Destination"

if (!(Test-Path $Source)) {
    Write-Error "Source path not found: $Source"
    exit 1
}

if (Test-Path $Destination) {
    Write-Host "Removing existing install at $Destination"
    Remove-Item -Recurse -Force $Destination
}

Write-Host "Copying files..."
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
Copy-Item -Path (Join-Path $Source '*') -Destination $Destination -Recurse -Force

# Create desktop shortcut
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Project Maelstrom.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $Destination 'ProjectMaelstrom.exe'
$shortcut.WorkingDirectory = $Destination
$shortcut.IconLocation = Join-Path $Destination 'ProjectMaelstrom.exe,0'
$shortcut.Save()

# Create Start Menu shortcut
$startMenu = Join-Path ([Environment]::GetFolderPath('Programs')) 'Project Maelstrom'
New-Item -ItemType Directory -Path $startMenu -Force | Out-Null
$shortcutPath2 = Join-Path $startMenu 'Project Maelstrom.lnk'
$shortcut2 = $shell.CreateShortcut($shortcutPath2)
$shortcut2.TargetPath = $shortcut.TargetPath
$shortcut2.WorkingDirectory = $shortcut.WorkingDirectory
$shortcut2.IconLocation = $shortcut.IconLocation
$shortcut2.Save()

Write-Host "Install complete. Launch via desktop or Start Menu shortcut."
