function Get-ProjectRoot {
    param([string]$ProjectName)
    $baseDir = "D:\Dev library"
    $path = Join-Path $baseDir $ProjectName
    if (Test-Path $path) {
        return $path
    }
    return $null
}

function Get-PythonPath {
    param([string]$RepoPath)
    $venvPaths = @(
        ".venv\Scripts\python.exe",
        ".venv_win\Scripts\python.exe",
        "venv\Scripts\python.exe"
    )
    
    foreach ($relPath in $venvPaths) {
        $fullPath = Join-Path $RepoPath $relPath
        if (Test-Path $fullPath) {
            return $fullPath
        }
    }
    
    return "python"
}

function Get-NodePath {
    param([string]$RepoPath)
    $nodeModules = Join-Path $RepoPath "node_modules"
    if (Test-Path $nodeModules) {
        return $nodeModules
    }
    return $null
}

# Export functions if called as a script or just provide them for dot-sourcing
Export-ModuleMember -Function Get-ProjectRoot, Get-PythonPath, Get-NodePath
