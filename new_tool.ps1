. "$PSScriptRoot\log_helper.ps1"

param(
    [Parameter(Mandatory=$true)]
    [string]$Name
)

$fileName = $Name
if ($fileName -notmatch "\.ps1$") { $fileName += ".ps1" }
$targetPath = Join-Path $PSScriptRoot $fileName

if (Test-Path $targetPath) {
    Write-AASLog "Tool $fileName already exists!" "ERROR"
    return
}

$template = @"
. "`$PSScriptRoot\log_helper.ps1"
. "`$PSScriptRoot\AuraSense.ps1"

param(
    [Parameter(ValueFromRemainingArguments = `$true)]
    [string[]] `$Args
)

Write-AASLog "Starting $Name..." "INFO"

# Your logic here

Write-AASLog "$Name complete." "SUCCESS"
"@

Set-Content $targetPath $template
Write-AASLog "Created new tool at $targetPath" "SUCCESS"
