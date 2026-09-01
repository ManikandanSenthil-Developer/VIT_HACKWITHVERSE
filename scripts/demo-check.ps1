# Pre-Demo Validation Script (PowerShell)
$WorkspaceRoot = (Get-Item -Path $PSScriptRoot).Parent.FullName
$BackendDir = Join-Path $WorkspaceRoot "backend"
$PythonExe = Join-Path $BackendDir "pyenv\python.exe"

Push-Location $BackendDir
try {
    & $PythonExe scripts/demo-check.py
} finally {
    Pop-Location
}
