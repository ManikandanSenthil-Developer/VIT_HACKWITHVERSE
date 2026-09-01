# MATS Platform — Disaster Recovery & Restore Runbook

This runbook documents how to restore, rebuild, and verify the MATS platform on a single laptop in case of data corruption, system failure, or hardware migration.

---

## 1. Database Restoration

To restore the SQLite database from a previous backup snapshot:

1. **Stop the Backend Process**:
   Ensure no Uvicorn or Python process is currently accessing `mats.db`.
   ```powershell
   Stop-Process -Name python -Force -ErrorAction SilentlyContinue
   ```

2. **Locate the Target Backup**:
   List available snapshots in `backend/backups/`:
   ```powershell
   dir d:\WorkSpace\VIT\mats-platform\backend\backups\
   ```

3. **Restore Database File**:
   Copy the desired snapshot over `mats.db`:
   ```powershell
   Copy-Item "d:\WorkSpace\VIT\mats-platform\backend\backups\mats_db_backup_YYYYMMDD_HHMMSS.sqlite" "d:\WorkSpace\VIT\mats-platform\backend\mats.db" -Force
   ```

4. **Verify Database Integrity**:
   Run SQLite integrity check:
   ```powershell
   & "d:\WorkSpace\VIT\mats-platform\backend\pyenv\python.exe" -c "import sqlite3; con = sqlite3.connect('d:/WorkSpace/VIT/mats-platform/backend/mats.db'); cur = con.cursor(); print(cur.execute('PRAGMA integrity_check;').fetchall()); con.close()"
   ```
   *Expected output: `[('ok',)]`*

---

## 2. Configuration Recovery

To restore `.env` settings:
```powershell
Copy-Item "d:\WorkSpace\VIT\mats-platform\backend\backups\env_backup_YYYYMMDD_HHMMSS.bak" "d:\WorkSpace\VIT\mats-platform\backend\.env" -Force
```

---

## 3. Database Schema Rebuilding & Migrations

If rebuilding the database from scratch:
```powershell
cd d:\WorkSpace\VIT\mats-platform\backend
# Run migrations up to latest revision
& ".\pyenv\python.exe" -m alembic upgrade head
```

---

## 4. Rebuilding Vector & Embedding Indexes

To re-ingest sample financial filings and rebuild 384-dimensional dense semantic vectors:
```powershell
# Re-running test suite automatically verifies embedding generation and vector search
& ".\pyenv\python.exe" -m pytest tests/test_rag.py -v
```

---

## 5. Service Restart Runbook

### Backend Restart:
```powershell
cd d:\WorkSpace\VIT\mats-platform\backend
& ".\pyenv\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Restart:
```powershell
cd d:\WorkSpace\VIT\mats-platform\frontend
npm run dev
```

---

## 6. Health Verification

Verify that all subsystems report healthy:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```
*Expected output: `status: healthy`, with database, cache, market_data_provider, rag_vector_engine, and ai_agents all operational.*
