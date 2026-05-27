"""
database.py
SQLite database setup for the Customer Support Ticketing CRM.
Connects to SQLite, creates the tickets and notes tables,
and auto-generates ticket IDs in the format TKT-001.
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")


def get_connection() -> sqlite3.Connection:
    """
    Returns a new SQLite connection with row_factory set so that
    rows are returned as dict-like objects (sqlite3.Row).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
    return conn


def init_db() -> None:
    """
    Creates the database tables if they don't already exist.
    Safe to call multiple times (idempotent).
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # ------------------------------------------------------------------
        # TICKETS table
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id       TEXT    NOT NULL UNIQUE,          -- e.g. TKT-001
                customer_name   TEXT    NOT NULL,
                customer_email  TEXT    NOT NULL,
                subject         TEXT    NOT NULL,
                description     TEXT    NOT NULL,
                status          TEXT    NOT NULL DEFAULT 'Open'
                                CHECK(status IN ('Open', 'In Progress', 'Closed')),
                created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ------------------------------------------------------------------
        # NOTES table
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id   TEXT    NOT NULL
                                REFERENCES tickets(ticket_id) ON DELETE CASCADE,
                note_text   TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        conn.commit()
    print(f"[database] Tables initialised. DB: {DB_PATH}")


def generate_ticket_id() -> str:
    """
    Generates the next sequential ticket ID in the format TKT-NNN.
    Reads the current maximum ID from the database and increments it.
    Returns 'TKT-001' when the table is empty.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_id FROM tickets ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

    if row is None:
        return "TKT-001"

    # Extract the numeric part and increment
    last_number = int(row["ticket_id"].split("-")[1])
    return f"TKT-{last_number + 1:03d}"


# ---------------------------------------------------------------------------
# Run table creation automatically when the module/script is executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("[database] Initialising database …")
    init_db()
    print("[database] Done.")
