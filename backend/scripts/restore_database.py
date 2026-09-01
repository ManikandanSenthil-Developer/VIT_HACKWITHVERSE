"""
MATS Database Restore & Integrity Verification Utility
Validates database backup snapshots and verifies database integrity.
"""
import os
import sys
import shutil
import sqlite3
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
BACKUP_DIR = BACKEND_DIR / "backups"
PROD_DB = BACKEND_DIR / "mats.db"
TEST_RESTORE_DB = BACKEND_DIR / "mats_restore_test.db"


def restore_and_verify(backup_file: Path = None):
    print("==================================================")
    print("MATS DATABASE RESTORE & INTEGRITY VERIFICATION")
    print("==================================================")

    # 1. Locate backup
    if not backup_file:
        if not BACKUP_DIR.exists():
            print("[*] Backups directory not found. Creating a snapshot from live database...")
            from backup_database import run_backup
            backup_file = run_backup()
        else:
            backups = sorted(BACKUP_DIR.glob("mats_db_backup_*.sqlite"), reverse=True)
            if not backups:
                print("[*] No backups found. Generating fresh snapshot...")
                from backup_database import run_backup
                backup_file = run_backup()
            else:
                backup_file = backups[0]

    print(f"[*] Verifying snapshot: {backup_file.name}")
    if not backup_file.exists():
        print(f"[!] Error: Backup file {backup_file} does not exist.")
        sys.exit(1)

    # 2. Restore to sandbox database
    print(f"[*] Restoring snapshot to sandbox: {TEST_RESTORE_DB.name}...")
    shutil.copy2(backup_file, TEST_RESTORE_DB)

    # 3. Perform SQLite Integrity Checks
    conn = sqlite3.connect(TEST_RESTORE_DB)
    cursor = conn.cursor()

    try:
        # Integrity check
        cursor.execute("PRAGMA integrity_check;")
        integrity = cursor.fetchone()[0]
        print(f"[*] PRAGMA integrity_check: {integrity}")
        if integrity != "ok":
            raise ValueError(f"Integrity check failed: {integrity}")

        # Foreign key check
        cursor.execute("PRAGMA foreign_key_check;")
        fk_errors = cursor.fetchall()
        if fk_errors:
            print(f"[!] Foreign key violations found: {fk_errors}")
            raise ValueError("Foreign key check failed.")
        print("[*] PRAGMA foreign_key_check: PASSED (0 violations)")

        # Verify key tables exist
        required_tables = ["users", "portfolios", "holdings", "market_snapshots", "documents", "alerts", "audit_logs"]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"[*] Found {len(tables)} tables in restored database.")

        for t in required_tables:
            if t not in tables:
                raise ValueError(f"Required table '{t}' is missing from restored database!")
            cursor.execute(f"SELECT COUNT(*) FROM {t};")
            count = cursor.fetchone()[0]
            print(f"    - Table '{t}': {count} records verified")

        print("==================================================")
        print("RESTORE TEST RESULT: 100% SUCCESSFUL")
        print("Database snapshot is valid, consistent, and recoverable.")
        print("==================================================")
        return True

    finally:
        conn.close()
        # Clean up sandbox file
        if TEST_RESTORE_DB.exists():
            os.remove(TEST_RESTORE_DB)


if __name__ == "__main__":
    restore_and_verify()
