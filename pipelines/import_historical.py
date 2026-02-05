"""
Historical Olympics Data Pipeline

Imports historical Winter Olympics medal data (last 4 games) into SQLite.
Creates a separate table for historical performance tracking.

Source: data/historical_olympics.json (compiled from Wikipedia/Olympics.com)
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import get_connection

DATA_FILE = Path(__file__).parent.parent / "data" / "historical_olympics.json"


def init_historical_tables():
    """Create tables for historical Olympics data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Olympics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_olympics (
            id TEXT PRIMARY KEY,
            year INTEGER NOT NULL,
            city TEXT NOT NULL,
            host_country TEXT NOT NULL,
            total_events INTEGER
        )
    """)
    
    # Historical medal results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_medals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            olympics_id TEXT NOT NULL,
            country_code TEXT NOT NULL,
            country_name TEXT NOT NULL,
            rank INTEGER NOT NULL,
            gold INTEGER NOT NULL,
            silver INTEGER NOT NULL,
            bronze INTEGER NOT NULL,
            total INTEGER NOT NULL,
            FOREIGN KEY (olympics_id) REFERENCES historical_olympics(id),
            UNIQUE(olympics_id, country_code)
        )
    """)
    
    conn.commit()
    conn.close()
    print("  Historical tables initialized")


def import_historical_data():
    """Import historical Olympics medal data."""
    print("=" * 60)
    print("HISTORICAL OLYMPICS PIPELINE")
    print("=" * 60)
    
    if not DATA_FILE.exists():
        print(f"  ERROR: Data file not found: {DATA_FILE}")
        return False
    
    # Initialize tables
    init_historical_tables()
    
    # Load data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM historical_medals")
    cursor.execute("DELETE FROM historical_olympics")
    deleted_medals = cursor.rowcount
    print(f"  Cleared existing historical data")
    
    olympics_count = 0
    medals_count = 0
    
    for olympics in data["olympics"]:
        year = olympics["year"]
        city = olympics["city"]
        host = olympics["country"]
        events = olympics.get("total_events", 0)
        
        olympics_id = f"winter-{year}"
        
        # Insert Olympics
        cursor.execute(
            """INSERT OR REPLACE INTO historical_olympics 
               (id, year, city, host_country, total_events) 
               VALUES (?, ?, ?, ?, ?)""",
            (olympics_id, year, city, host, events)
        )
        olympics_count += 1
        
        print(f"\n  {year} {city}:")
        
        # Insert medal results
        for entry in olympics["medal_table"]:
            cursor.execute(
                """INSERT OR REPLACE INTO historical_medals 
                   (olympics_id, country_code, country_name, rank, gold, silver, bronze, total)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    olympics_id,
                    entry["country"],
                    entry["country_name"],
                    entry["rank"],
                    entry["gold"],
                    entry["silver"],
                    entry["bronze"],
                    entry["total"]
                )
            )
            medals_count += 1
        
        # Show top 3
        top3 = olympics["medal_table"][:3]
        for entry in top3:
            print(f"    {entry['rank']}. {entry['country']}: {entry['gold']}G {entry['silver']}S {entry['bronze']}B = {entry['total']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Historical import complete!")
    print(f"  Olympics: {olympics_count}")
    print(f"  Medal entries: {medals_count}")
    
    return True


def get_historical_stats():
    """Get summary statistics from historical data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historical_medals'")
    if not cursor.fetchone():
        conn.close()
        return None
    
    stats = {}
    
    # Total medals by country (last 4 Olympics)
    cursor.execute("""
        SELECT 
            country_code,
            country_name,
            SUM(gold) as total_gold,
            SUM(silver) as total_silver,
            SUM(bronze) as total_bronze,
            SUM(total) as total_medals,
            COUNT(*) as appearances
        FROM historical_medals
        GROUP BY country_code
        ORDER BY total_gold DESC, total_silver DESC, total_bronze DESC
        LIMIT 15
    """)
    stats["top_countries"] = cursor.fetchall()
    
    # Nordic countries performance
    cursor.execute("""
        SELECT 
            hm.country_code,
            ho.year,
            hm.rank,
            hm.gold,
            hm.silver,
            hm.bronze,
            hm.total
        FROM historical_medals hm
        JOIN historical_olympics ho ON hm.olympics_id = ho.id
        WHERE hm.country_code IN ('NOR', 'SWE', 'FIN', 'DEN')
        ORDER BY hm.country_code, ho.year DESC
    """)
    stats["nordic_history"] = cursor.fetchall()
    
    conn.close()
    return stats


if __name__ == "__main__":
    import_historical_data()
    
    # Show stats
    print("\n" + "=" * 60)
    print("HISTORICAL SUMMARY")
    print("=" * 60)
    
    stats = get_historical_stats()
    if stats:
        print("\nTop 10 Countries (Last 4 Winter Olympics combined):")
        print(f"{'Country':<5} {'Gold':>5} {'Silver':>6} {'Bronze':>6} {'Total':>6} {'Apps':>5}")
        print("-" * 40)
        for row in stats["top_countries"][:10]:
            print(f"{row[0]:<5} {row[2]:>5} {row[3]:>6} {row[4]:>6} {row[5]:>6} {row[6]:>5}")
        
        print("\nNordic Countries by Year:")
        current_country = None
        for row in stats["nordic_history"]:
            if row[0] != current_country:
                current_country = row[0]
                print(f"\n  {current_country}:")
            print(f"    {row[1]}: Rank {row[2]:>2} - {row[3]}G {row[4]}S {row[5]}B = {row[6]}")
