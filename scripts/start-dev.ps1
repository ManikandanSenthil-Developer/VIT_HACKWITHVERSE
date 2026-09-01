# MATS Platform - One-Command Local Development Startup Script (PowerShell)
# Verifies Python, Node, environment files, applies migrations, and launches backend & frontend.

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "MATS PLATFORM - STARTING LOCAL DEVELOPMENT SERVICES" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$WorkspaceRoot = (Get-Item -Path $PSScriptRoot).Parent.FullName
$BackendDir = Join-Path $WorkspaceRoot "backend"
$FrontendDir = Join-Path $WorkspaceRoot "frontend"
$PythonExe = Join-Path $BackendDir "pyenv\python.exe"

# 1. Verify Environment
Write-Host "[1/4] Checking environment configurations..." -ForegroundColor Yellow
if (-not (Test-Path "$BackendDir\.env")) {
    Write-Host "      Copying .env.development to .env..."
    Copy-Item "$BackendDir\.env.development" "$BackendDir\.env"
}

# 2. Apply Database Migrations
Write-Host "[2/4] Verifying database migrations..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    & $PythonExe -m alembic upgrade head
} finally {
    Pop-Location
}

# 3. Seed Demo Baseline if database is empty
Write-Host "[3/4] Checking demo dataset baseline..." -ForegroundColor Yellow
Push-Location $BackendDir
try {
    & $PythonExe scripts/seed_demo_data.py
} finally {
    Pop-Location
}

# 4. Launch Services
Write-Host "[4/4] Launching Backend & Frontend services..." -ForegroundColor Green
Write-Host "      Backend will run at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "      Frontend will run at: http://localhost:5173" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop services." -ForegroundColor Cyan

Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $BackendDir
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory $FrontendDir
