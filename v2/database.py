"""
Database setup and operations for V2 pipeline.
Uses SQLite for simplicity.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "olympics.db"


def get_connection():
    """Get database connection."""
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize database with schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Countries
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            code TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    
    # Sports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sports (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    
    # Competitions (Olympic events)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitions (
            id TEXT PRIMARY KEY,
            sport_id TEXT,
            name TEXT,
            gender TEXT,
            FOREIGN KEY (sport_id) REFERENCES sports(id)
        )
    """)
    
    # Athletes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS athletes (
            id TEXT PRIMARY KEY,
            name TEXT,
            country_code TEXT,
            FOREIGN KEY (country_code) REFERENCES countries(code)
        )
    """)
    
    # Entries (athlete scores per competition)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id TEXT,
            competition_id TEXT,
            score REAL,
            source TEXT,
            updated_at TEXT,
            FOREIGN KEY (athlete_id) REFERENCES athletes(id),
            FOREIGN KEY (competition_id) REFERENCES competitions(id),
            UNIQUE(athlete_id, competition_id)
        )
    """)
    
    # Excluded athletes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS excluded_athletes (
            athlete_id TEXT PRIMARY KEY,
            reason TEXT,
            FOREIGN KEY (athlete_id) REFERENCES athletes(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def clear_entries_by_source(source: str):
    """Clear entries from a specific source before re-importing."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE source = ?", (source,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


def get_stats():
    """Get database statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    for table in ["countries", "sports", "competitions", "athletes", "entries", "excluded_athletes"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    
    # Entries by source
    cursor.execute("SELECT source, COUNT(*) FROM entries GROUP BY source")
    stats["entries_by_source"] = dict(cursor.fetchall())
    
    conn.close()
    return stats


if __name__ == "__main__":
    init_db()
    print("Stats:", get_stats())
