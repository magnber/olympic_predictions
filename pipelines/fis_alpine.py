"""
FIS Alpine Skiing Pipeline

Scrapes discipline-specific World Cup standings from FIS website.
This fixes the alpine event-specialization problem where athletes
were getting the same score in all alpine events.

Source: https://www.fis-ski.com/DB/alpine-skiing/cup-standings.html
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import get_connection

BASE_URL = "https://www.fis-ski.com/DB/alpine-skiing/cup-standings.html"

# Discipline codes and their Olympic event mappings
DISCIPLINES = {
    "SL": {"M": "alpine-m-slalom", "W": "alpine-w-slalom"},
    "GS": {"M": "alpine-m-giant-slalom", "W": "alpine-w-giant-slalom"},
    "SG": {"M": "alpine-m-super-g", "W": "alpine-w-super-g"},
    "DH": {"M": "alpine-m-downhill", "W": "alpine-w-downhill"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def create_athlete_id(name: str, country: str) -> str:
    """Create a consistent athlete ID."""
    clean_name = name.lower().replace(" ", "-").replace(".", "").replace(",", "")
    return f"{clean_name}-{country.lower()}"


def fetch_discipline_standings(discipline: str, gender: str, season: str = "2025"):
    """
    Fetch World Cup standings for a specific discipline.
    Returns list of {name, country, rank, points}
    """
    params = {
        "sectorcode": "AL",
        "seasoncode": season,
        "cupcode": "WC",
        "disciplinecode": discipline,
        "gendercode": gender
    }
    
    url = f"{BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        
        # Find all athlete rows (each is an <a> tag with class table-row)
        rows = soup.select('a.table-row[href*="athlete-biography"]')
        
        athletes = []
        for row in rows:
            # Extract name
            name_div = row.select_one('.justify-left.bold')
            if not name_div:
                continue
            name_text = name_div.get_text(strip=True)
            
            # Parse name (format: "LASTNAME Firstname")
            parts = name_text.split()
            if len(parts) >= 2:
                last_name = parts[0].title()
                first_name = " ".join(parts[1:]).title()
                name = f"{first_name} {last_name}"
            else:
                name = name_text.title()
            
            # Extract country
            country_span = row.select_one('.country__name-short')
            country = country_span.get_text(strip=True) if country_span else "UNK"
            
            # Find the discipline data - look for the discipline code
            # Each discipline section contains the code (SL, GS, etc.) and rank/points
            disc_sections = row.select('.g-xs-24.g-sm-24.g-md')
            
            rank = None
            points = None
            
            for section in disc_sections:
                # Check if this section is for our discipline
                code_div = section.select_one('.hidden-sm-up.justify-left')
                if code_div and code_div.get_text(strip=True) == discipline:
                    # Found our discipline - get rank and points
                    bold_divs = section.select('.justify-right.bold')
                    if len(bold_divs) >= 2:
                        rank_text = bold_divs[0].get_text(strip=True)
                        points_text = bold_divs[1].get_text(strip=True)
                        if rank_text and points_text:
                            try:
                                rank = int(rank_text)
                                points = int(points_text)
                            except ValueError:
                                pass
                    break
            
            if rank and points:
                athletes.append({
                    "name": name,
                    "country": country,
                    "rank": rank,
                    "points": points
                })
        
        # Sort by rank
        athletes.sort(key=lambda x: x["rank"])
        
        return athletes
        
    except requests.RequestException as e:
        print(f"    Error fetching {discipline} {gender}: {e}")
        return []


def import_fis_alpine_data():
    """Import FIS alpine skiing data into the database."""
    print("=" * 60)
    print("FIS ALPINE SKIING PIPELINE")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear old FIS entries
    cursor.execute("DELETE FROM entries WHERE source = ?", ("fis_alpine",))
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"  Cleared {deleted} old FIS alpine entries")
    
    # Also remove manual alpine entries (FIS data is better)
    cursor.execute("DELETE FROM entries WHERE source = 'manual' AND competition_id LIKE 'alpine-%'")
    removed_manual = cursor.rowcount
    if removed_manual > 0:
        print(f"  Replaced {removed_manual} manual alpine entries")
    
    timestamp = datetime.now().isoformat()
    imported = 0
    athletes_added = 0
    
    for discipline, events in DISCIPLINES.items():
        for gender, comp_id in events.items():
            gender_name = "Men" if gender == "M" else "Women"
            print(f"\n  Fetching {discipline} {gender_name}...")
            
            athletes = fetch_discipline_standings(discipline, gender)
            
            if not athletes:
                print(f"    No data found")
                continue
            
            print(f"    Found {len(athletes)} athletes")
            
            # Import top 30 per discipline
            for athlete in athletes[:30]:
                athlete_id = create_athlete_id(athlete["name"], athlete["country"])
                
                # Ensure athlete exists
                cursor.execute(
                    "INSERT OR IGNORE INTO athletes (id, name, country_code) VALUES (?, ?, ?)",
                    (athlete_id, athlete["name"], athlete["country"])
                )
                if cursor.rowcount > 0:
                    athletes_added += 1
                
                # Insert entry
                cursor.execute(
                    """INSERT OR REPLACE INTO entries 
                       (athlete_id, competition_id, score, source, updated_at) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (athlete_id, comp_id, athlete["points"], "fis_alpine", timestamp)
                )
                imported += 1
            
            # Show top 3
            print(f"    Top 3:")
            for a in athletes[:3]:
                print(f"      {a['rank']}. {a['name']} ({a['country']}): {a['points']} pts")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ FIS Alpine import complete!")
    print(f"  New athletes: {athletes_added}")
    print(f"  Entries: {imported}")
    
    return True


def test_scraping():
    """Test FIS scraping."""
    print("Testing FIS scraping...")
    athletes = fetch_discipline_standings("SL", "W")
    if athletes:
        print(f"✓ Found {len(athletes)} athletes")
        print("Top 5:")
        for a in athletes[:5]:
            print(f"  {a['rank']}. {a['name']} ({a['country']}): {a['points']} pts")
        return True
    else:
        print("✗ No data found")
        return False


if __name__ == "__main__":
    if test_scraping():
        import_fis_alpine_data()
