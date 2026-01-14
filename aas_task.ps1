param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
)

$repo = "D:\Dev library\AaroneousAutomationSuite"
$python = Join-Path $repo ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

Push-Location $repo
& $python "scripts/aas_cli.py" @Args
Pop-Location
