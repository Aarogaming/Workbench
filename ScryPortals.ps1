. "$PSScriptRoot\log_helper.ps1"

$suitePorts = @{
    "Maelstrom Webhooks" = 9410
    "Maelstrom Admin"    = 9411
    "MyFortress"        = 8100
    "Merlin Backend"     = 8001
    "AAS Hub"            = 8000
}

Write-AASLog "Checking AAS Suite port availability..." "INFO"

foreach ($service in $suitePorts.Keys) {
    $port = $suitePorts[$service]
    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet
    if ($connection) {
        Write-AASLog "$service is ACTIVE on port $port" "SUCCESS"
    } else {
        Write-AASLog "$service is NOT reachable on port $port" "WARN"
    }
}
