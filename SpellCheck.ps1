. "$PSScriptRoot\log_helper.ps1"

function Check-Runtime {
    param([string]$Name, [string]$Command, [string]$ExpectedVersion)
    
    Write-AASLog "Checking $Name..." "INFO"
    try {
        $version = & $Command --version 2>&1
        Write-AASLog "$Name found: $version" "SUCCESS"
    }
    catch {
        Write-AASLog "$Name NOT found. Expected $ExpectedVersion" "ERROR"
    }
}

Check-Runtime -Name ".NET" -Command "dotnet" -ExpectedVersion "9.x"
Check-Runtime -Name "Python" -Command "python" -ExpectedVersion "3.12.x"
Check-Runtime -Name "Node.js" -Command "node" -ExpectedVersion "20.x"
Check-Runtime -Name "Java" -Command "java" -ExpectedVersion "17.x"
Check-Runtime -Name "Git" -Command "git" -ExpectedVersion "Latest"
