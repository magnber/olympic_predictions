"""
Import existing JSON data into the database.
This preserves our current data as a baseline.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import get_connection, init_db
from excluded_athletes import get_excluded_set, get_excluded_with_reasons

# Paths to legacy data
LEGACY_DATA_DIR = Path(__file__).parent.parent / "data"


def import_legacy_data():
    """Import all legacy JSON data into the database."""
    print("=" * 60)
    print("IMPORTING LEGACY DATA")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Load legacy JSON files
    with open(LEGACY_DATA_DIR / "sports.json") as f:
        sports = json.load(f)
    
    with open(LEGACY_DATA_DIR / "competitions.json") as f:
        competitions = json.load(f)
    
    with open(LEGACY_DATA_DIR / "athletes.json") as f:
        athletes = json.load(f)
    
    with open(LEGACY_DATA_DIR / "entries.json") as f:
        entries = json.load(f)
    
    # Import sports
    print(f"\nImporting {len(sports)} sports...")
    for sport in sports:
        cursor.execute(
            "INSERT OR REPLACE INTO sports (id, name) VALUES (?, ?)",
            (sport["id"], sport["name"])
        )
    
    # Import competitions
    print(f"Importing {len(competitions)} competitions...")
    for comp in competitions:
        gender = "M" if "-m-" in comp["id"] or "-men" in comp["id"] else "W"
        cursor.execute(
            "INSERT OR REPLACE INTO competitions (id, sport_id, name, gender) VALUES (?, ?, ?, ?)",
            (comp["id"], comp["sport_id"], comp["name"], gender)
        )
    
    # Extract unique countries from athletes
    countries = set()
    for athlete in athletes:
        countries.add(athlete["country"])
    
    print(f"Importing {len(countries)} countries...")
    for code in countries:
        cursor.execute(
            "INSERT OR REPLACE INTO countries (code, name) VALUES (?, ?)",
            (code, code)  # We don't have full names in legacy data
        )
    
    # Import athletes (excluding excluded ones)
    print(f"Importing athletes...")
    imported_athletes = 0
    excluded_count = 0
    
    # Get excluded athletes with reasons
    excluded_set = get_excluded_set()
    excluded_reasons = {(name, country): reason for name, country, reason in get_excluded_with_reasons()}
    
    for athlete in athletes:
        # Check if excluded
        key = (athlete["name"], athlete["country"])
        is_excluded = key in excluded_set
        
        cursor.execute(
            "INSERT OR REPLACE INTO athletes (id, name, country_code) VALUES (?, ?, ?)",
            (athlete["id"], athlete["name"], athlete["country"])
        )
        
        if is_excluded:
            reason = excluded_reasons.get(key, "injury/retired")
            cursor.execute(
                "INSERT OR REPLACE INTO excluded_athletes (athlete_id, reason) VALUES (?, ?)",
                (athlete["id"], reason)
            )
            excluded_count += 1
        
        imported_athletes += 1
    
    print(f"  Imported: {imported_athletes}, Excluded: {excluded_count}")
    
    # Clear old legacy entries before re-importing
    cursor.execute("DELETE FROM entries WHERE source = ?", ("manual",))
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"  Cleared {deleted} old manual entries")
    
    # Import entries (excluding entries for excluded athletes)
    print(f"Importing entries...")
    
    # Get excluded athlete IDs
    cursor.execute("SELECT athlete_id FROM excluded_athletes")
    excluded_ids = set(row[0] for row in cursor.fetchall())
    
    imported_entries = 0
    skipped_entries = 0
    timestamp = datetime.now().isoformat()
    
    for entry in entries:
        if entry["athlete_id"] in excluded_ids:
            skipped_entries += 1
            continue
        
        cursor.execute(
            """INSERT OR REPLACE INTO entries 
               (athlete_id, competition_id, score, source, updated_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (entry["athlete_id"], entry["competition_id"], entry["score"], "manual", timestamp)
        )
        imported_entries += 1
    
    print(f"  Imported: {imported_entries}, Skipped (excluded): {skipped_entries}")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Legacy import complete!")
    
    # Print stats
    from database import get_stats
    stats = get_stats()
    print(f"\nDatabase stats:")
    for table, count in stats.items():
        if table != "entries_by_source":
            print(f"  {table}: {count}")
    print(f"  entries by source: {stats['entries_by_source']}")


if __name__ == "__main__":
    import_legacy_data()
