"""
FIS Cross-Country Skiing Pipeline

Scrapes discipline-specific World Cup standings from FIS website.
Separates sprint specialists from distance specialists.

Source: https://www.fis-ski.com/DB/cross-country/cup-standings.html
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import get_connection

BASE_URL = "https://www.fis-ski.com/DB/cross-country/cup-standings.html"

# Discipline codes and their Olympic event mappings
# Sprint events use SP standings, distance events use DI standings
# NOTE: IDs must match the competitions table in the database
DISCIPLINES = {
    "SP": {  # Sprint standings
        "M": [
            "cross-country-m-sprint",
            "cross-country-m-team-sprint",
        ],
        "W": [
            "cross-country-w-sprint",
            "cross-country-w-team-sprint",
        ]
    },
    "DI": {  # Distance standings
        "M": [
            "cross-country-m-skiathlon",
            "cross-country-m-15km",
            "cross-country-m-50km-mass",  # Matches DB: cross-country-m-50km-mass
            "cross-country-m-relay",       # Matches DB: cross-country-m-relay
        ],
        "W": [
            "cross-country-w-skiathlon",
            "cross-country-w-10km",
            "cross-country-w-50km-mass",  # Matches DB: cross-country-w-50km-mass
            "cross-country-w-relay",       # Matches DB: cross-country-w-relay
        ]
    }
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
    Fetch World Cup standings for a specific discipline (SP or DI).
    Returns list of {name, country, rank, points}
    """
    params = {
        "sectorcode": "CC",
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
        
        # Find all athlete rows
        rows = soup.select('a.table-row[href*="athlete-biography"]')
        
        athletes = []
        for row in rows:
            # Extract name from the bold div
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
            
            # Find the discipline-specific rank and points
            # Look for the section with our discipline code
            disc_sections = row.select('.g-xs-24.g-sm-24.g-md')
            
            rank = None
            points = None
            
            for section in disc_sections:
                code_div = section.select_one('.hidden-sm-up.justify-left')
                if code_div and code_div.get_text(strip=True) == discipline:
                    bold_divs = section.select('.justify-right.bold')
                    if len(bold_divs) >= 2:
                        rank_text = bold_divs[0].get_text(strip=True)
                        points_text = bold_divs[1].get_text(strip=True)
                        if rank_text and points_text:
                            # Remove thousand separators
                            points_text = points_text.replace("'", "").replace(",", "")
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


def import_fis_cross_country_data():
    """Import FIS cross-country skiing data into the database."""
    print("=" * 60)
    print("FIS CROSS-COUNTRY SKIING PIPELINE")
    print("=" * 60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear old FIS cross-country entries
    cursor.execute("DELETE FROM entries WHERE source = ?", ("fis_xc",))
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"  Cleared {deleted} old FIS cross-country entries")
    
    # Remove manual cross-country entries (FIS data is better)
    cursor.execute("DELETE FROM entries WHERE source = 'manual' AND competition_id LIKE 'cross-country-%'")
    removed_manual = cursor.rowcount
    if removed_manual > 0:
        print(f"  Replaced {removed_manual} manual cross-country entries")
    
    timestamp = datetime.now().isoformat()
    imported = 0
    athletes_added = 0
    
    for discipline, genders in DISCIPLINES.items():
        disc_name = "Sprint" if discipline == "SP" else "Distance"
        
        for gender, competitions in genders.items():
            gender_name = "Men" if gender == "M" else "Women"
            print(f"\n  Fetching {disc_name} {gender_name}...")
            
            athletes = fetch_discipline_standings(discipline, gender)
            
            if not athletes:
                print(f"    No data found")
                continue
            
            print(f"    Found {len(athletes)} athletes")
            
            # Import top 30 athletes for each competition in this discipline
            for athlete in athletes[:30]:
                athlete_id = create_athlete_id(athlete["name"], athlete["country"])
                
                # Ensure athlete exists
                cursor.execute(
                    "INSERT OR IGNORE INTO athletes (id, name, country_code) VALUES (?, ?, ?)",
                    (athlete_id, athlete["name"], athlete["country"])
                )
                if cursor.rowcount > 0:
                    athletes_added += 1
                
                # Insert entry for each competition in this discipline category
                for comp_id in competitions:
                    cursor.execute(
                        """INSERT OR REPLACE INTO entries 
                           (athlete_id, competition_id, score, source, updated_at) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (athlete_id, comp_id, athlete["points"], "fis_xc", timestamp)
                    )
                    imported += 1
            
            # Show top 3
            print(f"    Top 3:")
            for a in athletes[:3]:
                print(f"      {a['rank']}. {a['name']} ({a['country']}): {a['points']} pts")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ FIS Cross-Country import complete!")
    print(f"  New athletes: {athletes_added}")
    print(f"  Entries: {imported}")
    
    return True


def test_scraping():
    """Test FIS cross-country scraping."""
    print("Testing FIS cross-country scraping...")
    
    # Test sprint
    athletes_sp = fetch_discipline_standings("SP", "M")
    if athletes_sp:
        print(f"✓ Sprint Men: {len(athletes_sp)} athletes")
        print("  Top 3:")
        for a in athletes_sp[:3]:
            print(f"    {a['rank']}. {a['name']} ({a['country']}): {a['points']} pts")
    else:
        print("✗ Sprint Men: No data")
        return False
    
    # Test distance
    athletes_di = fetch_discipline_standings("DI", "M")
    if athletes_di:
        print(f"✓ Distance Men: {len(athletes_di)} athletes")
        print("  Top 3:")
        for a in athletes_di[:3]:
            print(f"    {a['rank']}. {a['name']} ({a['country']}): {a['points']} pts")
    else:
        print("✗ Distance Men: No data")
        return False
    
    return True


if __name__ == "__main__":
    if test_scraping():
        import_fis_cross_country_data()
