#!/usr/bin/env python3
"""
Olympic Medal Prediction - Version 1
Monte Carlo simulation based on World Cup standings

Usage: python predict.py
Output: output.csv with medal predictions per country
"""

import json
import random
from collections import defaultdict
from pathlib import Path

# Configuration
NUM_SIMULATIONS = 10000
NORDIC_COUNTRIES = {"NOR", "SWE", "FIN", "DEN"}
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def load_data():
    """Load all data files."""
    with open(DATA_DIR / "sports.json") as f:
        sports = {s["id"]: s for s in json.load(f)}
    
    with open(DATA_DIR / "competitions.json") as f:
        competitions = {c["id"]: c for c in json.load(f)}
    
    with open(DATA_DIR / "athletes.json") as f:
        athletes = {a["id"]: a for a in json.load(f)}
    
    with open(DATA_DIR / "entries.json") as f:
        entries = json.load(f)
    
    return sports, competitions, athletes, entries


def get_scoring_type(competition_id, competitions, sports):
    """Get the scoring type for a competition."""
    comp = competitions.get(competition_id)
    if not comp:
        return "wc_points"  # default
    sport_id = comp.get("sport_id")
    sport = sports.get(sport_id, {})
    return sport.get("scoring_type", "wc_points")


def normalize_scores(entries_for_competition, scoring_type):
    """
    Convert raw scores to probabilities based on scoring type.
    Returns list of (athlete_id, probability) tuples.
    """
    if not entries_for_competition:
        return []
    
    # Extract scores
    scores = [(e["athlete_id"], e["score"]) for e in entries_for_competition]
    
    if scoring_type == "world_ranking":
        # Lower is better - invert
        strengths = [(aid, 1.0 / max(score, 1)) for aid, score in scores]
    else:
        # Higher is better (wc_points, isu_points, season_best)
        strengths = [(aid, max(score, 0)) for aid, score in scores]
    
    # Normalize to sum = 1
    total = sum(s for _, s in strengths)
    if total <= 0:
        # Equal probability if no valid scores
        prob = 1.0 / len(strengths)
        return [(aid, prob) for aid, _ in strengths]
    
    return [(aid, s / total) for aid, s in strengths]


def simulate_competition(probabilities):
    """
    Simulate a single competition.
    Returns (gold_athlete, silver_athlete, bronze_athlete).
    """
    if len(probabilities) < 3:
        # Not enough athletes - return what we have
        athletes = [aid for aid, _ in probabilities]
        while len(athletes) < 3:
            athletes.append(None)
        return tuple(athletes[:3])
    
    # Weighted random selection without replacement
    remaining = list(probabilities)
    results = []
    
    for _ in range(3):  # gold, silver, bronze
        if not remaining:
            results.append(None)
            continue
        
        total = sum(p for _, p in remaining)
        if total <= 0:
            # Random selection if probabilities are zero
            idx = random.randint(0, len(remaining) - 1)
        else:
            r = random.random() * total
            cumulative = 0
            idx = 0
            for i, (_, p) in enumerate(remaining):
                cumulative += p
                if r <= cumulative:
                    idx = i
                    break
        
        winner = remaining.pop(idx)
        results.append(winner[0])
    
    return tuple(results)


def run_simulation(sports, competitions, athletes, entries):
    """Run Monte Carlo simulation and return medal counts."""
    
    # Group entries by competition
    entries_by_comp = defaultdict(list)
    for entry in entries:
        entries_by_comp[entry["competition_id"]].append(entry)
    
    # Track medal counts across all simulations
    # Structure: {country: {"gold": count, "silver": count, "bronze": count}}
    medal_totals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
    
    # Track per-competition medal wins by athlete
    # Structure: {comp_id: {athlete_id: {"gold": count, "silver": count, "bronze": count}}}
    comp_athlete_medals = defaultdict(lambda: defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0}))
    
    # Track individual simulation results for confidence intervals
    simulation_results = []
    
    for sim in range(NUM_SIMULATIONS):
        sim_medals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
        
        for comp_id, comp_entries in entries_by_comp.items():
            scoring_type = get_scoring_type(comp_id, competitions, sports)
            probabilities = normalize_scores(comp_entries, scoring_type)
            
            if not probabilities:
                continue
            
            gold, silver, bronze = simulate_competition(probabilities)
            
            # Award medals
            for medal_type, athlete_id in [("gold", gold), ("silver", silver), ("bronze", bronze)]:
                if athlete_id and athlete_id in athletes:
                    country = athletes[athlete_id]["country"]
                    sim_medals[country][medal_type] += 1
                    medal_totals[country][medal_type] += 1
                    comp_athlete_medals[comp_id][athlete_id][medal_type] += 1
        
        simulation_results.append(dict(sim_medals))
    
    # Calculate averages
    results = {}
    for country, medals in medal_totals.items():
        results[country] = {
            "gold": medals["gold"] / NUM_SIMULATIONS,
            "silver": medals["silver"] / NUM_SIMULATIONS,
            "bronze": medals["bronze"] / NUM_SIMULATIONS,
            "total": (medals["gold"] + medals["silver"] + medals["bronze"]) / NUM_SIMULATIONS
        }
    
    return results, simulation_results, comp_athlete_medals, entries_by_comp


def calculate_confidence_intervals(simulation_results, country):
    """Calculate 95% confidence interval for a country's medals."""
    golds = []
    silvers = []
    bronzes = []
    totals = []
    
    for sim in simulation_results:
        if country in sim:
            g = sim[country]["gold"]
            s = sim[country]["silver"]
            b = sim[country]["bronze"]
        else:
            g = s = b = 0
        golds.append(g)
        silvers.append(s)
        bronzes.append(b)
        totals.append(g + s + b)
    
    def percentile(data, p):
        sorted_data = sorted(data)
        idx = int(len(sorted_data) * p / 100)
        return sorted_data[min(idx, len(sorted_data) - 1)]
    
    return {
        "gold": (percentile(golds, 2.5), percentile(golds, 97.5)),
        "silver": (percentile(silvers, 2.5), percentile(silvers, 97.5)),
        "bronze": (percentile(bronzes, 2.5), percentile(bronzes, 97.5)),
        "total": (percentile(totals, 2.5), percentile(totals, 97.5)),
    }


def main():
    print(f"Loading data from {DATA_DIR}...")
    sports, competitions, athletes, entries = load_data()
    
    print(f"Loaded {len(competitions)} competitions, {len(athletes)} athletes, {len(entries)} entries")
    
    # Count competitions with entries
    comps_with_entries = len(set(e["competition_id"] for e in entries))
    print(f"Competitions with athlete data: {comps_with_entries}")
    
    print(f"\nRunning {NUM_SIMULATIONS:,} simulations...")
    results, simulation_results, comp_athlete_medals, entries_by_comp = run_simulation(sports, competitions, athletes, entries)
    
    # Filter to Nordic countries and sort
    nordic_results = {c: r for c, r in results.items() if c in NORDIC_COUNTRIES}
    
    # Sort by expected total medals
    sorted_results = sorted(nordic_results.items(), key=lambda x: -x[1]["total"])
    
    # Print results
    print("\n" + "=" * 60)
    print("NORDIC MEDAL PREDICTIONS - 2026 Winter Olympics")
    print("=" * 60)
    
    for country, medals in sorted_results:
        ci = calculate_confidence_intervals(simulation_results, country)
        print(f"\n{country}:")
        print(f"  Gold:   {medals['gold']:5.1f}  (95% CI: {ci['gold'][0]:4.0f} - {ci['gold'][1]:4.0f})")
        print(f"  Silver: {medals['silver']:5.1f}  (95% CI: {ci['silver'][0]:4.0f} - {ci['silver'][1]:4.0f})")
        print(f"  Bronze: {medals['bronze']:5.1f}  (95% CI: {ci['bronze'][0]:4.0f} - {ci['bronze'][1]:4.0f})")
        print(f"  Total:  {medals['total']:5.1f}  (95% CI: {ci['total'][0]:4.0f} - {ci['total'][1]:4.0f})")
    
    # Write CSV output
    output_dir = Path(__file__).parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "v1_predictions.csv"
    with open(output_path, "w") as f:
        f.write("country,gold,silver,bronze,total,gold_low,gold_high,silver_low,silver_high,bronze_low,bronze_high,total_low,total_high\n")
        for country, medals in sorted_results:
            ci = calculate_confidence_intervals(simulation_results, country)
            f.write(f"{country},{medals['gold']:.1f},{medals['silver']:.1f},{medals['bronze']:.1f},{medals['total']:.1f},")
            f.write(f"{ci['gold'][0]},{ci['gold'][1]},{ci['silver'][0]},{ci['silver'][1]},")
            f.write(f"{ci['bronze'][0]},{ci['bronze'][1]},{ci['total'][0]},{ci['total'][1]}\n")
    
    print(f"\nResults written to {output_path}")
    
    # Also output rounded predictions for the challenge
    print("\n" + "=" * 60)
    print("ROUNDED PREDICTIONS (for submission)")
    print("=" * 60)
    for country, medals in sorted_results:
        g = round(medals['gold'])
        s = round(medals['silver'])
        b = round(medals['bronze'])
        print(f"{country}: Gold {g} - Silver {s} - Bronze {b}")
    
    # Output per-competition predictions
    comp_predictions = []
    for comp_id, athlete_medals in comp_athlete_medals.items():
        comp = competitions.get(comp_id, {})
        comp_name = comp.get("name", comp_id)
        sport_id = comp.get("sport_id", "unknown")
        
        # Find top athletes for each medal type
        for medal_type in ["gold", "silver", "bronze"]:
            medal_counts = [(aid, m[medal_type]) for aid, m in athlete_medals.items()]
            medal_counts.sort(key=lambda x: -x[1])
            
            for rank, (athlete_id, count) in enumerate(medal_counts[:3], 1):
                athlete = athletes.get(athlete_id, {})
                probability = count / NUM_SIMULATIONS * 100
                
                comp_predictions.append({
                    "competition_id": comp_id,
                    "competition_name": comp_name,
                    "sport_id": sport_id,
                    "medal": medal_type,
                    "rank": rank,
                    "athlete_id": athlete_id,
                    "athlete_name": athlete.get("name", "Unknown"),
                    "country": athlete.get("country", "???"),
                    "probability": probability,
                    "win_count": count
                })
    
    # Write per-competition CSV
    comp_output_path = output_dir / "v1_competition_predictions.csv"
    with open(comp_output_path, "w") as f:
        f.write("competition_id,competition_name,sport_id,medal,rank,athlete_id,athlete_name,country,probability,win_count\n")
        for p in sorted(comp_predictions, key=lambda x: (x["competition_name"], x["medal"], x["rank"])):
            f.write(f"{p['competition_id']},{p['competition_name']},{p['sport_id']},{p['medal']},{p['rank']},")
            f.write(f"{p['athlete_id']},{p['athlete_name']},{p['country']},{p['probability']:.1f},{p['win_count']}\n")
    
    print(f"Competition predictions written to {comp_output_path}")


if __name__ == "__main__":
    main()
