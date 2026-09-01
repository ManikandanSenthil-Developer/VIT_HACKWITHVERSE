# Reset Demo Environment Script (PowerShell)
$WorkspaceRoot = (Get-Item -Path $PSScriptRoot).Parent.FullName
$BackendDir = Join-Path $WorkspaceRoot "backend"
$PythonExe = Join-Path $BackendDir "pyenv\python.exe"

Write-Host "[*] Resetting demo state to baseline..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    & $PythonExe scripts/seed_demo_data.py
    Write-Host "[✓] Demo environment successfully restored to pristine baseline." -ForegroundColor Green
} finally {
    Pop-Location
}
