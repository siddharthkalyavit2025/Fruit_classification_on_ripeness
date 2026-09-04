# ==============================================================
# Database Connection — SQLite
# ==============================================================
# Creates and manages the SQLite connection.
# The database file is created automatically on first run.
# No separate database server required.
# ==============================================================

import sqlite3
import logging
import os
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """
    Get a new SQLite connection.

    Uses Row factory so queries return dict-like rows
    instead of plain tuples (easier to work with).
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent read performance
    return conn


def init_database():
    """
    Create the predictions table if it doesn't exist.
    Called once at application startup.
    """
    logger.info(f"Initializing database at: {os.path.abspath(DATABASE_PATH)}")

    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
                predicted_class TEXT    NOT NULL,
                fruit           TEXT    NOT NULL,
                condition       TEXT    NOT NULL,
                confidence      REAL    NOT NULL,
                servo_angle     INTEGER,
                destination     TEXT,
                arduino_command TEXT,
                sorting_status  TEXT    NOT NULL DEFAULT 'PENDING'
            )
        """)
        conn.commit()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        raise
    finally:
        conn.close()
