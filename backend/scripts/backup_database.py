import os
import shutil
import sys
from datetime import datetime

# Set paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BACKEND_DIR, "mats.db")
BACKUP_DIR = os.path.join(BACKEND_DIR, "backups")


def backup_database():
    """
    Perform a timestamped local backup of the SQLite database and configuration.
    Designed for single-laptop production deployments.
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Database backup
    if os.path.exists(DB_PATH):
        db_backup_name = f"mats_db_backup_{timestamp}.sqlite"
        db_dest = os.path.join(BACKUP_DIR, db_backup_name)
        shutil.copy2(DB_PATH, db_dest)
        size_kb = os.path.getsize(db_dest) / 1024
        print(f"[SUCCESS] Database backed up to: {db_dest} ({size_kb:.1f} KB)")
    else:
        print(f"[WARNING] Database file not found at: {DB_PATH}")

    # 2. Configuration backup (.env if exists)
    env_path = os.path.join(BACKEND_DIR, ".env")
    if os.path.exists(env_path):
        env_backup_name = f"env_backup_{timestamp}.bak"
        env_dest = os.path.join(BACKUP_DIR, env_backup_name)
        shutil.copy2(env_path, env_dest)
        print(f"[SUCCESS] Environment config backed up to: {env_dest}")

    print(f"\n[BACKUP COMPLETE] Backup snapshot {timestamp} stored in {BACKUP_DIR}")


if __name__ == "__main__":
    backup_database()
