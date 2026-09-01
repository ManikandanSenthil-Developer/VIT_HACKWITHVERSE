# MATS Production Deployment Guide

## 1. Prerequisites
- Python 3.11+
- Node.js 20+ & npm
- PostgreSQL 16+ (or local embedded SQLite for single-laptop production mode)
- Modern Web Browser (Chrome, Edge, Firefox, Safari)

## 2. Environment Configuration
Copy `.env.production.example` to `backend/.env`:
```powershell
cp backend/.env.production.example backend/.env
```
Ensure `JWT_SECRET` is set to a secure, randomly generated string.

## 3. Database Setup & Migration
Run database migrations using Alembic:
```powershell
cd backend
& ".\pyenv\python.exe" -m alembic upgrade head
```

## 4. Seed Baseline Dataset
Seed the deterministic financial companies, price history, and regulatory SEC 10-Ks:
```powershell
& ".\pyenv\python.exe" scripts/seed_demo_data.py
```

## 5. Backend Production Launch
Start the production ASGI server with multi-worker concurrency:
```powershell
& ".\pyenv\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 6. Frontend Production Build & Hosting
Compile the static production bundle:
```powershell
cd ../frontend
npm run build
```
Serve with any static file server or preview via Vite:
```powershell
npm run preview -- --port 5173 --host 0.0.0.0
```

## 7. Health Check Verification
Verify operational status:
```powershell
curl -i http://localhost:8000/health
curl -i http://localhost:8000/health/live
curl -i http://localhost:8000/health/ready
```

## 8. Rollback Procedure
If a migration failure occurs:
```powershell
& ".\pyenv\python.exe" -m alembic downgrade -1
& ".\pyenv\python.exe" scripts/restore_database.py
```
