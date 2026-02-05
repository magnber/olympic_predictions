#!/usr/bin/env python3
"""
Olympic Medal Prediction - Version 1
Monte Carlo simulation based on World Cup standings

Usage: python predict.py
Output: output.csv with medal predictions per country
"""

import json
import math
import random
from collections import defaultdict
from pathlib import Path

# Configuration
NUM_SIMULATIONS = 100000
# Gumbel noise scale - higher = more upsets, lower = favorites always win
# Typical values: 0.5-1.5. Based on rank-ordered logit model literature.
PERFORMANCE_VARIANCE = 1.0
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


def gumbel_noise():
    """
    Generate Gumbel(0, scale) noise for performance simulation.
    Gumbel distribution is used in rank-ordered logit models.
    """
    u = random.random()
    # Avoid log(0)
    while u == 0:
        u = random.random()
    return -PERFORMANCE_VARIANCE * math.log(-math.log(u))


def simulate_competition(probabilities):
    """
    Simulate a single competition using rank-ordered logit model.
    
    Each athlete's performance = log(strength) + Gumbel noise
    Athletes are ranked by simulated performance.
    
    This approach is based on:
    - Plackett-Luce model (probability theory)
    - Rank-ordered logit (econometrics)
    - Used by FiveThirtyEight, academic sports prediction
    
    Returns (gold_athlete, silver_athlete, bronze_athlete).
    """
    if len(probabilities) < 3:
        athletes = [aid for aid, _ in probabilities]
        while len(athletes) < 3:
            athletes.append(None)
        return tuple(athletes[:3])
    
    # Simulate performance for each athlete
    # Performance = log(strength) + Gumbel noise
    performances = []
    for athlete_id, strength in probabilities:
        if strength <= 0:
            strength = 0.0001  # Avoid log(0)
        # Log-strength + random Gumbel noise
        perf = math.log(strength) + gumbel_noise()
        performances.append((athlete_id, perf))
    
    # Sort by performance (highest = winner)
    performances.sort(key=lambda x: -x[1])
    
    # Return top 3
    gold = performances[0][0]
    silver = performances[1][0]
    bronze = performances[2][0]
    
    return (gold, silver, bronze)


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


def get_median_medals(simulation_results, country):
    """Get median medal counts for a country across all simulations."""
    golds = []
    silvers = []
    bronzes = []
    totals = []
    for sim in simulation_results:
        g = sim.get(country, {}).get("gold", 0)
        s = sim.get(country, {}).get("silver", 0)
        b = sim.get(country, {}).get("bronze", 0)
        golds.append(g)
        silvers.append(s)
        bronzes.append(b)
        totals.append(g + s + b)
    golds.sort()
    silvers.sort()
    bronzes.sort()
    totals.sort()
    mid = len(golds) // 2
    return {
        "gold": golds[mid],
        "silver": silvers[mid],
        "bronze": bronzes[mid],
        "total": totals[mid]
    }


def get_representative_simulation(simulation_results, countries):
    """
    Find the simulation closest to median total medals for all countries combined.
    Returns that single simulation's results - showing realistic G/S/B variance.
    """
    # Calculate total Nordic medals for each simulation
    sim_totals = []
    for i, sim in enumerate(simulation_results):
        total = 0
        for country in countries:
            total += sim.get(country, {}).get("gold", 0)
            total += sim.get(country, {}).get("silver", 0)
            total += sim.get(country, {}).get("bronze", 0)
        sim_totals.append((i, total))
    
    # Find median total
    sim_totals.sort(key=lambda x: x[1])
    median_idx = sim_totals[len(sim_totals) // 2][0]
    
    return simulation_results[median_idx]


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


def run_and_output(sports, competitions, athletes, entries, run_name, output_suffix=""):
    """Run simulation and write output files."""
    print(f"\n{'='*60}")
    print(f"RUN: {run_name}")
    print(f"{'='*60}")
    
    print(f"Running {NUM_SIMULATIONS:,} simulations...")
    results, simulation_results, comp_athlete_medals, entries_by_comp = run_simulation(
        sports, competitions, athletes, entries
    )
    
    # Filter to Nordic countries and sort
    nordic_results = {c: r for c, r in results.items() if c in NORDIC_COUNTRIES}
    sorted_results = sorted(nordic_results.items(), key=lambda x: -x[1]["total"])
    
    # Print results
    print("\nNORDIC MEDAL PREDICTIONS - 2026 Winter Olympics")
    print("(Using rank-ordered logit model with Gumbel noise)")
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
    output_path = output_dir / f"v1_predictions{output_suffix}.csv"
    
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
    
    comp_output_path = output_dir / f"v1_competition_predictions{output_suffix}.csv"
    with open(comp_output_path, "w") as f:
        f.write("competition_id,competition_name,sport_id,medal,rank,athlete_id,athlete_name,country,probability,win_count\n")
        for p in sorted(comp_predictions, key=lambda x: (x["competition_name"], x["medal"], x["rank"])):
            f.write(f"{p['competition_id']},{p['competition_name']},{p['sport_id']},{p['medal']},{p['rank']},")
            f.write(f"{p['athlete_id']},{p['athlete_name']},{p['country']},{p['probability']:.1f},{p['win_count']}\n")
    
    print(f"Competition predictions written to {comp_output_path}")
    
    return sorted_results


def main():
    print(f"Loading data from {DATA_DIR}...")
    sports, competitions, athletes, entries = load_data()
    
    print(f"Loaded {len(competitions)} competitions, {len(athletes)} athletes, {len(entries)} entries")
    comps_with_entries = len(set(e["competition_id"] for e in entries))
    print(f"Competitions with athlete data: {comps_with_entries}")
    
    # Run 1 - no fixed seed (truly random)
    results1 = run_and_output(sports, competitions, athletes, entries, "Run 1", "")
    
    # Run 2 - different random state (should produce same MEANS due to law of large numbers)
    results2 = run_and_output(sports, competitions, athletes, entries, "Run 2", "_run_2")
    
    # Compare results - means should be nearly identical with 100k simulations
    print("\n" + "=" * 60)
    print("STABILITY CHECK: Comparing Run 1 vs Run 2")
    print("(With 100k simulations, means should converge to same values)")
    print("=" * 60)
    
    all_stable = True
    for (c1, m1), (c2, m2) in zip(results1, results2):
        g1, s1, b1 = round(m1['gold']), round(m1['silver']), round(m1['bronze'])
        g2, s2, b2 = round(m2['gold']), round(m2['silver']), round(m2['bronze'])
        
        # Check if means are within 0.5 of each other (statistical tolerance)
        mean_diff = abs(m1['gold'] - m2['gold']) + abs(m1['silver'] - m2['silver']) + abs(m1['bronze'] - m2['bronze'])
        stable = mean_diff < 0.5
        if not stable:
            all_stable = False
        
        match = "✓" if (g1, s1, b1) == (g2, s2, b2) else f"~(diff={mean_diff:.2f})"
        print(f"{c1}: Run1({g1}-{s1}-{b1}) vs Run2({g2}-{s2}-{b2}) {match}")
        print(f"      Means: {m1['gold']:.2f}-{m1['silver']:.2f}-{m1['bronze']:.2f} vs {m2['gold']:.2f}-{m2['silver']:.2f}-{m2['bronze']:.2f}")
    
    if all_stable:
        print("\n✓ Means converged - results are statistically stable!")
    else:
        print("\n⚠ Means differ more than expected - consider increasing NUM_SIMULATIONS")


if __name__ == "__main__":
    main()
