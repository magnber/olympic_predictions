"""
ISU Speed Skating API Pipeline

Fetches event-specific standings from the ISU API by aggregating
World Cup results per distance. This provides accurate event-specific
data instead of overall standings.

API: https://api.isuresults.eu
"""

import requests
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import get_connection

BASE_URL = "https://api.isuresults.eu"

# WC points table
WC_POINTS = {1: 100, 2: 80, 3: 60, 4: 50, 5: 45, 6: 40, 7: 36, 8: 32, 9: 29, 10: 26,
             11: 24, 12: 22, 13: 20, 14: 18, 15: 16, 16: 15, 17: 14, 18: 13, 19: 12, 20: 11,
             21: 10, 22: 9, 23: 8, 24: 7, 25: 6, 26: 5, 27: 4, 28: 3, 29: 2, 30: 1}

# Map ISU distance names to our competition IDs
DISTANCE_MAP = {
    "500 Meter": {"M": "speed-skating-m-500m", "F": "speed-skating-w-500m"},
    "1,000 Meter": {"M": "speed-skating-m-1000m", "F": "speed-skating-w-1000m"},
    "1,500 Meter": {"M": "speed-skating-m-1500m", "F": "speed-skating-w-1500m"},
    "3,000 Meter": {"F": "speed-skating-w-3000m"},
    "5,000 Meter": {"M": "speed-skating-m-5000m", "F": "speed-skating-w-5000m"},
    "10,000 Meter": {"M": "speed-skating-m-10000m"},
    "Mass Start (16 Laps)": {"M": "speed-skating-m-mass-start", "F": "speed-skating-w-mass-start"},
}


def create_athlete_id(name: str, country: str) -> str:
    """Create a consistent athlete ID."""
    clean_name = name.lower().replace(" ", "-").replace(".", "").replace(",", "")
    return f"{clean_name}-{country.lower()}"


def fetch_world_cup_events(season: str = "2025"):
    """Fetch World Cup events for the season."""
    try:
        response = requests.get(f"{BASE_URL}/events", params={"season": season}, timeout=30)
        response.raise_for_status()
        data = response.json()
        events = data.get("results", [])
        wc_events = [e for e in events if "World Cup Speed Skating" in e.get("name", "") 
                     and "Junior" not in e.get("name", "")]
        return wc_events
    except requests.RequestException as e:
        print(f"  Error fetching events: {e}")
        return []


def aggregate_wc_standings(wc_events):
    """
    Aggregate WC results across all events to build standings per distance.
    Returns: {distance_key: {skater_id: {name, country, points, isu_id}}}
    """
    standings = {}
    
    for event in wc_events:
        event_id = event["isuId"]
        print(f"  Processing: {event['name']}")
        
        # Get competitions for this event
        try:
            r = requests.get(f"{BASE_URL}/events/{event_id}/competitions/", timeout=30)
            if r.status_code != 200:
                continue
            comps = r.json()
        except Exception as e:
            print(f"    Error: {e}")
            continue
        
        # Only Division A (main competition)
        div_a = [c for c in comps if c.get("division") == "A" and c["category"] in ("M", "F")]
        
        for comp in div_a:
            dist_name = comp["distance"]["name"]
            gender = comp["category"]
            
            # Skip distances not in our map (team events)
            if dist_name not in DISTANCE_MAP:
                continue
            if gender not in DISTANCE_MAP[dist_name]:
                continue
            
            dist_key = DISTANCE_MAP[dist_name][gender]
            
            # Get results
            try:
                r2 = requests.get(comp["resultsUrl"], timeout=30)
                if r2.status_code != 200:
                    continue
                results = r2.json()
            except Exception as e:
                continue
            
            if dist_key not in standings:
                standings[dist_key] = {}
            
            for res in results:
                rank = res.get("rank")
                if not rank or rank > 30:
                    continue
                
                # Extract skater info from competitor.skater
                competitor = res.get("competitor", {})
                skater = competitor.get("skater", {})
                if not skater:
                    continue
                
                isu_id = skater.get("id")
                first_name = skater.get("firstName", "")
                last_name = skater.get("lastName", "")
                country = skater.get("country", "")
                
                if not isu_id or not country:
                    continue
                
                name = f"{first_name} {last_name}".strip()
                points = WC_POINTS.get(rank, 0)
                
                if isu_id not in standings[dist_key]:
                    standings[dist_key][isu_id] = {
                        "name": name,
                        "country": country,
                        "points": 0,
                        "isu_id": isu_id
                    }
                
                standings[dist_key][isu_id]["points"] += points
    
    return standings


def import_isu_data():
    """Import ISU speed skating data into the database."""
    print("=" * 60)
    print("ISU SPEED SKATING PIPELINE")
    print("=" * 60)
    
    # Fetch WC events
    wc_events = fetch_world_cup_events("2025")
    
    if not wc_events:
        print("\n⚠ No World Cup events found.")
        return False
    
    print(f"\n✓ Found {len(wc_events)} World Cup events")
    
    # Aggregate standings
    print("\nAggregating results...")
    standings = aggregate_wc_standings(wc_events)
    
    if not standings:
        print("\n⚠ No standings aggregated.")
        return False
    
    # Import to database
    print("\nImporting to database...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear old ISU entries
    cursor.execute("DELETE FROM entries WHERE source = ?", ("isu_api",))
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"  Cleared {deleted} old ISU entries")
    
    timestamp = datetime.now().isoformat()
    imported = 0
    athletes_added = 0
    
    for dist_key, skaters in standings.items():
        # Sort by points to get top skaters
        sorted_skaters = sorted(skaters.values(), key=lambda x: -x["points"])
        
        for skater in sorted_skaters[:30]:  # Top 30 per distance
            athlete_id = create_athlete_id(skater["name"], skater["country"])
            
            # Ensure athlete exists
            cursor.execute(
                "INSERT OR IGNORE INTO athletes (id, name, country_code) VALUES (?, ?, ?)",
                (athlete_id, skater["name"], skater["country"])
            )
            if cursor.rowcount > 0:
                athletes_added += 1
            
            # Insert entry (replaces any manual entry for this athlete/competition)
            cursor.execute(
                """INSERT OR REPLACE INTO entries 
                   (athlete_id, competition_id, score, source, updated_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (athlete_id, dist_key, skater["points"], "isu_api", timestamp)
            )
            imported += 1
    
    # Also remove manual entries for speed skating (ISU data is better)
    cursor.execute(
        "DELETE FROM entries WHERE source = 'manual' AND competition_id LIKE 'speed-skating-%'"
    )
    removed_manual = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ ISU import complete!")
    print(f"  New athletes: {athletes_added}")
    print(f"  ISU entries: {imported}")
    print(f"  Replaced manual entries: {removed_manual}")
    
    # Print standings summary
    print("\n=== STANDINGS SUMMARY ===")
    for dist_key in sorted(standings.keys()):
        sorted_skaters = sorted(standings[dist_key].values(), key=lambda x: -x["points"])[:3]
        print(f"\n{dist_key}:")
        for i, s in enumerate(sorted_skaters, 1):
            print(f"  {i}. {s['name']} ({s['country']}): {s['points']} pts")
    
    return True


def test_api_connection():
    """Test if ISU API is accessible."""
    print("Testing ISU API connection...")
    try:
        response = requests.get(f"{BASE_URL}/events", params={"limit": 1}, timeout=10)
        if response.status_code == 200:
            print("  ✓ API accessible")
            return True
        else:
            print(f"  ✗ Unexpected status: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"  ✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    if test_api_connection():
        import_isu_data()
    else:
        print("\nCould not connect to ISU API.")
