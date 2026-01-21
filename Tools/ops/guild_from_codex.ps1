param(
    [Parameter(Mandatory=$true)]
    [string]$InputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $InputPath)) {
    Write-Error "Input file not found: $InputPath"
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $toolsRoot

Write-Host "Running GuildReceptionist..." -ForegroundColor Cyan
dotnet run --project DevTools/GuildReceptionist/GuildReceptionist.csproj -- "$InputPath" --clipboard --zip
$exit = $LASTEXITCODE

if ($exit -eq 0) {
    $guild = Resolve-Path -LiteralPath "GUILD.md"
    $zipPath = "guild_pack.zip"
    Write-Host "Guild ready:" -ForegroundColor Green
    Write-Host "  GUILD.md     -> $guild"
    if (Test-Path $zipPath) {
        $zip = Resolve-Path -LiteralPath $zipPath
        Write-Host "  guild_pack.zip -> $zip"
    }
    Write-Host "Clipboard updated with GUILD.md contents."
} else {
    Write-Host "GuildReceptionist failed (exit $exit)." -ForegroundColor Red
}

exit $exit
