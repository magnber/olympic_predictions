#!/usr/bin/env python3
"""
Olympic Prediction Engine

Reads athlete/competition data from SQLite database and runs
Monte Carlo simulation using Plackett-Luce model with temperature scaling.
"""

import math
import random
from collections import defaultdict
from pathlib import Path
import csv

from database import get_connection, DB_PATH

# Configuration
NUM_SIMULATIONS = 10000
TEMPERATURE = 0.3  # Controls noise level (lower = more deterministic)
PERFORMANCE_VARIANCE = 1.0  # Base variance for Gumbel noise

NORDIC_COUNTRIES = {"NOR", "SWE", "FIN", "DEN"}

OUTPUT_DIR = Path(__file__).parent / "output"


def gumbel_noise():
    """Generate Gumbel-distributed noise, scaled by temperature."""
    u = random.random()
    while u == 0:
        u = random.random()
    return -TEMPERATURE * PERFORMANCE_VARIANCE * math.log(-math.log(u))


def load_data_from_db():
    """Load competition, athlete, and entry data from database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get competitions
    cursor.execute("SELECT id, sport_id, name, gender FROM competitions")
    competitions = {}
    for row in cursor.fetchall():
        competitions[row[0]] = {
            "id": row[0],
            "sport_id": row[1],
            "name": row[2],
            "gender": row[3]
        }
    
    # Get athletes (excluding excluded ones)
    cursor.execute("""
        SELECT a.id, a.name, a.country_code 
        FROM athletes a
        LEFT JOIN excluded_athletes e ON a.id = e.athlete_id
        WHERE e.athlete_id IS NULL
    """)
    athletes = {}
    for row in cursor.fetchall():
        athletes[row[0]] = {
            "id": row[0],
            "name": row[1],
            "country": row[2]
        }
    
    # Get entries
    cursor.execute("SELECT athlete_id, competition_id, score FROM entries")
    entries = []
    for row in cursor.fetchall():
        # Skip entries for excluded athletes
        if row[0] in athletes:
            entries.append({
                "athlete_id": row[0],
                "competition_id": row[1],
                "score": row[2]
            })
    
    conn.close()
    
    return competitions, athletes, entries


def build_competition_entries(competitions, athletes, entries):
    """Build mapping of competition -> list of (athlete, score)."""
    comp_entries = defaultdict(list)
    
    for entry in entries:
        athlete_id = entry["athlete_id"]
        comp_id = entry["competition_id"]
        score = entry["score"]
        
        if athlete_id in athletes and comp_id in competitions:
            athlete = athletes[athlete_id]
            comp_entries[comp_id].append({
                "athlete": athlete,
                "score": score,
                "log_strength": math.log(max(score, 0.01))
            })
    
    return comp_entries


def simulate_competition(entries):
    """
    Simulate a single competition using Plackett-Luce model.
    Returns top 3 finishers (gold, silver, bronze).
    """
    if len(entries) < 3:
        return []
    
    # Calculate noisy strengths for this simulation
    noisy = []
    for e in entries:
        perturbed = e["log_strength"] + gumbel_noise()
        noisy.append((perturbed, e["athlete"]))
    
    # Sort by noisy strength (descending)
    noisy.sort(key=lambda x: -x[0])
    
    # Return top 3
    return [noisy[i][1] for i in range(min(3, len(noisy)))]


def run_simulation(competitions, comp_entries):
    """Run full Monte Carlo simulation."""
    # Track medal counts per country
    country_medals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
    
    # Track per-simulation results for confidence intervals
    simulation_results = []
    
    # Competition-level tracking
    comp_results = defaultdict(lambda: defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0}))
    
    for sim in range(NUM_SIMULATIONS):
        sim_medals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
        
        for comp_id, entries in comp_entries.items():
            if len(entries) < 3:
                continue
            
            winners = simulate_competition(entries)
            
            if len(winners) >= 3:
                # Gold
                sim_medals[winners[0]["country"]]["gold"] += 1
                comp_results[comp_id][winners[0]["id"]]["gold"] += 1
                
                # Silver
                sim_medals[winners[1]["country"]]["silver"] += 1
                comp_results[comp_id][winners[1]["id"]]["silver"] += 1
                
                # Bronze
                sim_medals[winners[2]["country"]]["bronze"] += 1
                comp_results[comp_id][winners[2]["id"]]["bronze"] += 1
        
        simulation_results.append(dict(sim_medals))
        
        # Accumulate
        for country, medals in sim_medals.items():
            for medal_type, count in medals.items():
                country_medals[country][medal_type] += count
    
    # Average over simulations
    for country in country_medals:
        for medal_type in ["gold", "silver", "bronze"]:
            country_medals[country][medal_type] /= NUM_SIMULATIONS
    
    # Add totals
    for country in country_medals:
        m = country_medals[country]
        m["total"] = m["gold"] + m["silver"] + m["bronze"]
    
    return dict(country_medals), simulation_results, comp_results


def calculate_confidence_intervals(simulation_results, country, confidence=0.95):
    """Calculate confidence intervals for a country's medals."""
    gold_counts = []
    silver_counts = []
    bronze_counts = []
    
    for sim in simulation_results:
        medals = sim.get(country, {"gold": 0, "silver": 0, "bronze": 0})
        gold_counts.append(medals["gold"])
        silver_counts.append(medals["silver"])
        bronze_counts.append(medals["bronze"])
    
    def percentile(data, p):
        sorted_data = sorted(data)
        idx = int(len(sorted_data) * p)
        return sorted_data[min(idx, len(sorted_data) - 1)]
    
    lower = (1 - confidence) / 2
    upper = 1 - lower
    
    return {
        "gold": (percentile(gold_counts, lower), percentile(gold_counts, upper)),
        "silver": (percentile(silver_counts, lower), percentile(silver_counts, upper)),
        "bronze": (percentile(bronze_counts, lower), percentile(bronze_counts, upper))
    }


def output_results(results, simulation_results, competitions, comp_results, athletes):
    """Output prediction results."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Sort by total medals
    sorted_results = sorted(results.items(), key=lambda x: -x[1]["total"])
    
    print("\n" + "=" * 60)
    print("MEDAL PREDICTIONS - 2026 Winter Olympics")
    print("(Plackett-Luce model with temperature scaling)")
    print(f"Data source: SQLite database")
    print(f"Simulations: {NUM_SIMULATIONS:,}, Temperature: {TEMPERATURE}")
    print("=" * 60)
    
    # Top 15 countries
    print("\n=== TOP 15 COUNTRIES ===")
    for rank, (country, medals) in enumerate(sorted_results[:15], 1):
        ci = calculate_confidence_intervals(simulation_results, country)
        pred_g = round(medals['gold'])
        pred_s = round(medals['silver'])
        pred_b = round(medals['bronze'])
        pred_total = pred_g + pred_s + pred_b
        nordic_marker = " *" if country in NORDIC_COUNTRIES else ""
        print(f"{rank:2d}. {country}: Gold {pred_g:2d} - Silver {pred_s:2d} - Bronze {pred_b:2d} (Total: {pred_total}){nordic_marker}")
    
    # Nordic detail
    print("\n=== NORDIC COUNTRIES DETAIL ===")
    nordic_results = [(c, r) for c, r in sorted_results if c in NORDIC_COUNTRIES]
    for country, medals in nordic_results:
        ci = calculate_confidence_intervals(simulation_results, country)
        pred_g = round(medals['gold'])
        pred_s = round(medals['silver'])
        pred_b = round(medals['bronze'])
        pred_total = pred_g + pred_s + pred_b
        print(f"{country}: Gold {pred_g:2d} - Silver {pred_s:2d} - Bronze {pred_b:2d} (Total: {pred_total})")
        print(f"  95% CI: G({ci['gold'][0]:.0f}-{ci['gold'][1]:.0f}) S({ci['silver'][0]:.0f}-{ci['silver'][1]:.0f}) B({ci['bronze'][0]:.0f}-{ci['bronze'][1]:.0f})")
    
    # Write country predictions CSV
    pred_file = OUTPUT_DIR / "predictions.csv"
    with open(pred_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["country", "gold", "silver", "bronze", "total"])
        for country, medals in sorted_results:
            writer.writerow([
                country,
                round(medals["gold"]),
                round(medals["silver"]),
                round(medals["bronze"]),
                round(medals["total"])
            ])
    print(f"\n✓ Country predictions: {pred_file}")
    
    # Write competition predictions CSV
    comp_file = OUTPUT_DIR / "competition_predictions.csv"
    with open(comp_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["competition", "athlete_id", "athlete_name", "country", "gold_prob", "silver_prob", "bronze_prob", "medal_prob"])
        
        for comp_id in sorted(comp_results.keys()):
            comp = competitions.get(comp_id, {"name": comp_id})
            for athlete_id, counts in comp_results[comp_id].items():
                athlete = athletes.get(athlete_id, {"name": athlete_id, "country": "UNK"})
                gold_prob = counts["gold"] / NUM_SIMULATIONS
                silver_prob = counts["silver"] / NUM_SIMULATIONS
                bronze_prob = counts["bronze"] / NUM_SIMULATIONS
                medal_prob = gold_prob + silver_prob + bronze_prob
                
                writer.writerow([
                    comp.get("name", comp_id),
                    athlete_id,
                    athlete["name"],
                    athlete["country"],
                    f"{gold_prob:.4f}",
                    f"{silver_prob:.4f}",
                    f"{bronze_prob:.4f}",
                    f"{medal_prob:.4f}"
                ])
    print(f"✓ Competition predictions: {comp_file}")
    
    return results


def main():
    print("=" * 60)
    print("OLYMPIC PREDICTION ENGINE")
    print("=" * 60)
    
    # Check database exists
    if not DB_PATH.exists():
        print(f"\n✗ Database not found: {DB_PATH}")
        print("  Run 'python run_pipeline.py' first to create the database.")
        return
    
    print(f"\nLoading data from: {DB_PATH}")
    
    # Load data
    competitions, athletes, entries = load_data_from_db()
    print(f"  Competitions: {len(competitions)}")
    print(f"  Athletes: {len(athletes)}")
    print(f"  Entries: {len(entries)}")
    
    # Build competition entries
    comp_entries = build_competition_entries(competitions, athletes, entries)
    print(f"  Competitions with entries: {len(comp_entries)}")
    
    # Run simulation
    print(f"\nRunning {NUM_SIMULATIONS:,} simulations...")
    results, simulation_results, comp_results = run_simulation(competitions, comp_entries)
    
    # Output results
    output_results(results, simulation_results, competitions, comp_results, athletes)
    
    print("\n✓ Prediction complete!")


if __name__ == "__main__":
    main()
