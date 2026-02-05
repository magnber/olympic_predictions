#!/usr/bin/env python3
"""
Olympic Medal Prediction - Version 3
Monte Carlo with Variance Propagation (Plackett-Luce model)

Key improvements over V1/V2:
- Variance propagation: athlete strength uncertainty is modeled
- Each simulation samples athlete strength from a distribution
- This creates correlated errors within simulations (more realistic)
- Stability comes from mean convergence, NOT fixed random seeds

Based on:
- "Misadventures in Monte Carlo" (Journal of Sports Analytics, 2019)
- Plackett-Luce model for ranking data
- FiveThirtyEight methodology

Usage: python predict.py
Output: v3_predictions.csv, v3_competition_predictions.csv
"""

import json
import math
import random
from collections import defaultdict
from pathlib import Path

# Configuration
NUM_SIMULATIONS = 100000
NORDIC_COUNTRIES = {"NOR", "SWE", "FIN", "DEN"}
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# V3 Model parameters
# Strength uncertainty: models our uncertainty in athlete strength estimates
# This creates correlated errors - same athlete affected across all their events
STRENGTH_UNCERTAINTY = 0.15  # 15% coefficient of variation

# TEMPERATURE: Controls how much noise vs skill determines outcomes
# - Lower temperature = favorites win more consistently
# - Temperature 1.0 = standard Plackett-Luce (Gumbel stddev ~1.28)
# - Temperature 0.3 = reduced noise (Gumbel stddev ~0.38), more realistic
#
# Why 0.3? Our log-strength spread (1st to 5th) is ~0.4
# With temp=1.0, noise (stddev 1.28) is 3x larger than signal
# With temp=0.3, noise (stddev 0.38) matches the signal scale
TEMPERATURE = 0.3

# Gumbel scale for day-to-day performance variation (within a simulation)
PERFORMANCE_VARIANCE = 1.0


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
        return "wc_points"
    sport_id = comp.get("sport_id")
    sport = sports.get(sport_id, {})
    return sport.get("scoring_type", "wc_points")


def calculate_base_strength(score, scoring_type):
    """
    Convert raw score to base strength.
    Higher strength = better athlete.
    """
    if scoring_type == "world_ranking":
        # Lower rank = stronger (rank 1 is best)
        return 1000.0 / max(score, 1)
    else:
        # Higher points = stronger
        return max(score, 1)


def gumbel_noise():
    """
    Generate Gumbel-distributed noise for Plackett-Luce model.
    This models day-to-day performance variation.
    
    Scaled by TEMPERATURE to control signal-to-noise ratio:
    - Standard Gumbel (temp=1.0) has stddev ~1.28
    - With temp=0.3, stddev ~0.38 (matches log-strength spread)
    """
    u = random.random()
    while u == 0:
        u = random.random()
    return -TEMPERATURE * PERFORMANCE_VARIANCE * math.log(-math.log(u))


def sample_strength_multiplier():
    """
    Sample a strength multiplier for variance propagation.
    Uses log-normal distribution to keep strengths positive.
    
    This models our UNCERTAINTY in athlete strength estimates.
    The same multiplier is used for an athlete across all their events
    within a single simulation, creating correlated errors.
    """
    # Log-normal: exp(N(0, σ²)) has mean ≈ 1 and CV ≈ σ
    log_multiplier = random.gauss(0, STRENGTH_UNCERTAINTY)
    return math.exp(log_multiplier)


def simulate_competition(entries_for_competition, scoring_type, athlete_multipliers):
    """
    Simulate a single competition using Plackett-Luce model.
    
    The Plackett-Luce model simulates rankings by:
    1. Assigning each athlete an effective strength (base * uncertainty multiplier)
    2. Adding Gumbel noise to log(strength) for day-to-day variation
    3. Ranking by performance
    
    Args:
        entries_for_competition: List of entry dicts with athlete_id and score
        scoring_type: How to interpret scores
        athlete_multipliers: Dict of athlete_id -> strength multiplier for this simulation
    
    Returns:
        Tuple of (gold_winner_id, silver_winner_id, bronze_winner_id)
    """
    if len(entries_for_competition) < 3:
        athletes = [e["athlete_id"] for e in entries_for_competition]
        while len(athletes) < 3:
            athletes.append(None)
        return tuple(athletes[:3])
    
    performances = []
    for entry in entries_for_competition:
        athlete_id = entry["athlete_id"]
        base_strength = calculate_base_strength(entry["score"], scoring_type)
        
        # Apply athlete-specific uncertainty multiplier (variance propagation)
        multiplier = athlete_multipliers.get(athlete_id, 1.0)
        effective_strength = base_strength * multiplier
        
        # Plackett-Luce: performance = log(strength) + Gumbel noise
        if effective_strength <= 0:
            effective_strength = 0.0001
        performance = math.log(effective_strength) + gumbel_noise()
        
        performances.append((athlete_id, performance))
    
    # Sort by performance (highest = best)
    performances.sort(key=lambda x: -x[1])
    
    gold = performances[0][0]
    silver = performances[1][0]
    bronze = performances[2][0]
    
    return (gold, silver, bronze)


def run_simulation(sports, competitions, athletes, entries):
    """
    Run NUM_SIMULATIONS Monte Carlo simulations with variance propagation.
    
    Key difference from V1/V2:
    - Each simulation samples strength multipliers for ALL athletes
    - These multipliers are held constant within a simulation
    - This creates correlated errors (realistic uncertainty modeling)
    """
    # Group entries by competition
    entries_by_comp = defaultdict(list)
    for entry in entries:
        entries_by_comp[entry["competition_id"]].append(entry)
    
    # Get all unique athlete IDs
    all_athlete_ids = set(e["athlete_id"] for e in entries)
    
    # Track results
    country_medals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
    simulation_results = []
    comp_athlete_medals = defaultdict(lambda: defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0}))
    
    for sim_idx in range(NUM_SIMULATIONS):
        # VARIANCE PROPAGATION: Sample strength multipliers for ALL athletes
        # This is held constant across all competitions in this simulation
        athlete_multipliers = {
            aid: sample_strength_multiplier() 
            for aid in all_athlete_ids
        }
        
        sim_medals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
        
        for comp_id, comp_entries in entries_by_comp.items():
            scoring_type = get_scoring_type(comp_id, competitions, sports)
            gold, silver, bronze = simulate_competition(
                comp_entries, scoring_type, athlete_multipliers
            )
            
            # Award medals
            for medal_type, winner_id in [("gold", gold), ("silver", silver), ("bronze", bronze)]:
                if winner_id:
                    athlete = athletes.get(winner_id, {})
                    country = athlete.get("country", "???")
                    sim_medals[country][medal_type] += 1
                    comp_athlete_medals[comp_id][winner_id][medal_type] += 1
        
        simulation_results.append(dict(sim_medals))
        
        # Accumulate for mean calculation
        for country, medals in sim_medals.items():
            country_medals[country]["gold"] += medals["gold"]
            country_medals[country]["silver"] += medals["silver"]
            country_medals[country]["bronze"] += medals["bronze"]
    
    # Calculate means
    results = {}
    for country, totals in country_medals.items():
        results[country] = {
            "gold": totals["gold"] / NUM_SIMULATIONS,
            "silver": totals["silver"] / NUM_SIMULATIONS,
            "bronze": totals["bronze"] / NUM_SIMULATIONS,
            "total": (totals["gold"] + totals["silver"] + totals["bronze"]) / NUM_SIMULATIONS,
        }
    
    return results, simulation_results, comp_athlete_medals, entries_by_comp


def calculate_confidence_intervals(simulation_results, country):
    """Calculate 95% confidence intervals from simulation results."""
    golds = []
    silvers = []
    bronzes = []
    totals = []
    
    for sim in simulation_results:
        medals = sim.get(country, {"gold": 0, "silver": 0, "bronze": 0})
        g = medals.get("gold", 0)
        s = medals.get("silver", 0)
        b = medals.get("bronze", 0)
        golds.append(g)
        silvers.append(s)
        bronzes.append(b)
        totals.append(g + s + b)
    
    def percentile(data, p):
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f
        return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)
    
    return {
        "gold": (percentile(golds, 2.5), percentile(golds, 97.5)),
        "silver": (percentile(silvers, 2.5), percentile(silvers, 97.5)),
        "bronze": (percentile(bronzes, 2.5), percentile(bronzes, 97.5)),
        "total": (percentile(totals, 2.5), percentile(totals, 97.5)),
    }


def run_and_output(sports, competitions, athletes, entries, run_name, output_suffix=""):
    """Run simulation and write output files."""
    print(f"\n{'='*60}")
    print(f"RUN: {run_name}")
    print(f"{'='*60}")
    
    print(f"Running {NUM_SIMULATIONS:,} simulations with variance propagation...")
    print(f"  - Strength uncertainty: {STRENGTH_UNCERTAINTY*100:.0f}% CV")
    print(f"  - Temperature: {TEMPERATURE} (noise scale)")
    print(f"  - Effective Gumbel stddev: {TEMPERATURE * 1.28:.2f}")
    
    results, simulation_results, comp_athlete_medals, entries_by_comp = run_simulation(
        sports, competitions, athletes, entries
    )
    
    # Filter to Nordic countries and sort
    nordic_results = {c: r for c, r in results.items() if c in NORDIC_COUNTRIES}
    sorted_results = sorted(nordic_results.items(), key=lambda x: -x[1]["total"])
    
    # Print results
    print("\nNORDIC MEDAL PREDICTIONS - 2026 Winter Olympics (V3)")
    print("(Plackett-Luce model with variance propagation)")
    print(f"Prediction = Expected value (mean) from {NUM_SIMULATIONS:,} simulations\n")
    
    for country, medals in sorted_results:
        ci = calculate_confidence_intervals(simulation_results, country)
        pred_g = round(medals['gold'])
        pred_s = round(medals['silver'])
        pred_b = round(medals['bronze'])
        pred_total = pred_g + pred_s + pred_b
        print(f"{country}: Gold {pred_g:2d} - Silver {pred_s:2d} - Bronze {pred_b:2d} (Total: {pred_total})")
        print(f"  Mean: {medals['gold']:.2f}-{medals['silver']:.2f}-{medals['bronze']:.2f}, 95% CI: G({ci['gold'][0]:.0f}-{ci['gold'][1]:.0f}) S({ci['silver'][0]:.0f}-{ci['silver'][1]:.0f}) B({ci['bronze'][0]:.0f}-{ci['bronze'][1]:.0f})")
    
    # Write CSV output
    output_dir = Path(__file__).parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"v3_predictions{output_suffix}.csv"
    
    with open(output_path, "w") as f:
        f.write("country,gold,silver,bronze,total,gold_mean,silver_mean,bronze_mean,total_mean,gold_low,gold_high,silver_low,silver_high,bronze_low,bronze_high,total_low,total_high\n")
        for country, medals in sorted_results:
            ci = calculate_confidence_intervals(simulation_results, country)
            pred_g = round(medals['gold'])
            pred_s = round(medals['silver'])
            pred_b = round(medals['bronze'])
            pred_total = pred_g + pred_s + pred_b
            f.write(f"{country},{pred_g},{pred_s},{pred_b},{pred_total},")
            f.write(f"{medals['gold']:.2f},{medals['silver']:.2f},{medals['bronze']:.2f},{medals['total']:.2f},")
            f.write(f"{ci['gold'][0]},{ci['gold'][1]},{ci['silver'][0]},{ci['silver'][1]},")
            f.write(f"{ci['bronze'][0]},{ci['bronze'][1]},{ci['total'][0]},{ci['total'][1]}\n")
    
    print(f"\nResults written to {output_path}")
    
    # Output per-competition predictions
    comp_predictions = []
    for comp_id, athlete_medals in comp_athlete_medals.items():
        comp = competitions.get(comp_id, {})
        comp_name = comp.get("name", comp_id)
        sport_id = comp.get("sport_id", "unknown")
        
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
    
    comp_output_path = output_dir / f"v3_competition_predictions{output_suffix}.csv"
    with open(comp_output_path, "w") as f:
        f.write("competition_id,competition_name,sport_id,medal,rank,athlete_id,athlete_name,country,probability,win_count\n")
        for p in sorted(comp_predictions, key=lambda x: (x["competition_name"], x["medal"], x["rank"])):
            f.write(f"{p['competition_id']},{p['competition_name']},{p['sport_id']},{p['medal']},{p['rank']},")
            f.write(f"{p['athlete_id']},{p['athlete_name']},{p['country']},{p['probability']:.1f},{p['win_count']}\n")
    
    print(f"Competition predictions written to {comp_output_path}")
    
    return sorted_results


def main():
    print("=" * 60)
    print("V3 MONTE CARLO WITH VARIANCE PROPAGATION")
    print("=" * 60)
    
    print(f"\nLoading data from {DATA_DIR}...")
    sports, competitions, athletes, entries = load_data()
    
    print(f"Loaded {len(competitions)} competitions, {len(athletes)} athletes, {len(entries)} entries")
    comps_with_entries = len(set(e["competition_id"] for e in entries))
    print(f"Competitions with athlete data: {comps_with_entries}")
    
    print(f"\n=== V3 MODEL PARAMETERS ===")
    print(f"Strength uncertainty: {STRENGTH_UNCERTAINTY*100:.0f}% (models estimation error)")
    print(f"Temperature: {TEMPERATURE} (lower = favorites win more)")
    print(f"Effective noise stddev: {TEMPERATURE * 1.28:.2f} (vs log-spread ~0.4)")
    print(f"Simulations: {NUM_SIMULATIONS:,}")
    
    run_and_output(sports, competitions, athletes, entries, "V3 Simulation", "")


if __name__ == "__main__":
    main()
