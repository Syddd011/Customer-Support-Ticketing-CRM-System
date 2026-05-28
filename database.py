# database.py - sets up SQLite and creates the tables

import sqlite3
import os
from datetime import datetime

db_file = os.path.join(os.path.dirname(__file__), "crm.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory enabled."""
    # using row_factory so I don't have to use row[0], row[1]
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist yet."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # tickets table
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

        # notes are optional but helpful for tracking ticket progress
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
    print(f"Tables ready. DB: {db_file}")


def generate_ticket_id() -> str:
    """Generate the next ticket ID like TKT-001, TKT-002, etc."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_id FROM tickets ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

    if row is None:
        return "TKT-001"

    # padded to 3 digits so sorting works correctly
    last_number = int(row["ticket_id"].split("-")[1])
    return f"TKT-{last_number + 1:03d}"


# run directly to initialise the database
if __name__ == "__main__":
    print("Setting up database...")
    init_db()
    print("Done.")
