@echo off
REM MATS Platform - One-Click Windows Batch Starter
echo ==================================================
echo MATS PLATFORM - STARTING SERVICES (WINDOWS CMD)
echo ==================================================

cd /d "%~dp0.."
set WORKSPACE=%CD%

echo [*] Starting Backend at http://127.0.0.1:8000 ...
start "MATS Backend API" cmd /k "cd %WORKSPACE%\backend && pyenv\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [*] Starting Frontend at http://localhost:5173 ...
start "MATS Frontend Web" cmd /k "cd %WORKSPACE%\frontend && npm run dev"

echo ==================================================
echo Services launched in separate console windows.
echo ==================================================
pause
