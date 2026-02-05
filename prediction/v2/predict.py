#!/usr/bin/env python3
"""
Olympic Medal Prediction - Version 2
Bradley-Terry inspired model with position-weighted probabilities

Key differences from V1:
- Softmax probability (not Gumbel noise)
- Position-weighted power: Gold favors top athletes more than bronze
- Temperature parameter to control upset frequency
- Based on Bradley-Terry pairwise comparison model

References:
- Bradley-Terry model (1952) for paired comparisons
- Gracenote Virtual Medal Table methodology
- Dixon-Coles recency weighting concept

Usage: python predict.py
Output: v2_predictions.csv
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

# V2 Model parameters
# Power-weighted probability: P(i) = strength^power / sum(strength^power)
# Higher power = favorites dominate more
GOLD_POWER = 1.5   # Gold heavily favors top athletes
SILVER_POWER = 1.2 # Silver slightly favors top athletes  
BRONZE_POWER = 1.0 # Bronze is most "random" (equal to strength ratio)
TOP_N_CONTENDERS = 20  # Only top N athletes compete for medals


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


def calculate_strength(score, scoring_type):
    """
    Convert raw score to strength rating.
    Bradley-Terry style: strength represents relative ability.
    """
    if scoring_type == "world_ranking":
        # Lower rank = stronger (invert and scale)
        return 1000.0 / max(score, 1)
    else:
        # Higher points = stronger
        return max(float(score), 1)


def power_weighted_select(strengths, power=1.0):
    """
    Select one item using power-weighted probability.
    
    P(athlete i) = strength_i^power / sum(strength_j^power)
    
    Higher power = top athletes win more often.
    Power 1.0 = probability proportional to strength
    Power 2.0 = probability proportional to strength squared (favorites dominate)
    
    Args:
        strengths: list of (id, strength) tuples
        power: exponent applied to strengths
    
    Returns:
        selected id and remaining list
    """
    if not strengths:
        return None, []
    
    if len(strengths) == 1:
        return strengths[0][0], []
    
    # Apply power transformation
    powered = [(aid, s ** power) for aid, s in strengths]
    total = sum(p for _, p in powered)
    
    if total <= 0:
        # Random selection if all strengths are zero
        idx = random.randint(0, len(strengths) - 1)
        selected_id = strengths[idx][0]
        remaining = strengths[:idx] + strengths[idx + 1:]
        return selected_id, remaining
    
    # Weighted random selection
    r = random.random() * total
    cumulative = 0
    selected_idx = 0
    for i, (aid, p) in enumerate(powered):
        cumulative += p
        if r <= cumulative:
            selected_idx = i
            break
    
    selected_id = strengths[selected_idx][0]
    remaining = strengths[:selected_idx] + strengths[selected_idx + 1:]
    
    return selected_id, remaining


def simulate_competition(entries_for_competition, scoring_type):
    """
    Simulate a single competition using Bradley-Terry inspired model.
    
    Key innovation: Different power exponents for each medal position.
    - Gold: Higher power (1.3) - favorites win gold more often
    - Silver: Normal power (1.0) - balanced
    - Bronze: Lower power (0.8) - more upsets, underdogs can medal
    
    Returns (gold_athlete, silver_athlete, bronze_athlete).
    """
    if len(entries_for_competition) < 3:
        athletes = [e["athlete_id"] for e in entries_for_competition]
        while len(athletes) < 3:
            athletes.append(None)
        return tuple(athletes[:3])
    
    # Calculate strengths and sort by strength
    strengths = []
    for entry in entries_for_competition:
        s = calculate_strength(entry["score"], scoring_type)
        strengths.append((entry["athlete_id"], s))
    
    # Sort by strength (highest first) and take top contenders
    strengths.sort(key=lambda x: -x[1])
    strengths = strengths[:TOP_N_CONTENDERS]
    
    # Select gold (heavily favors top athletes)
    gold, remaining = power_weighted_select(strengths, power=GOLD_POWER)
    
    # Select silver (moderately favors top athletes)
    silver, remaining = power_weighted_select(remaining, power=SILVER_POWER)
    
    # Select bronze (proportional to strength - more upsets possible)
    bronze, _ = power_weighted_select(remaining, power=BRONZE_POWER)
    
    return (gold, silver, bronze)


def run_simulation(sports, competitions, athletes, entries):
    """Run Monte Carlo simulation and return medal counts."""
    
    # Group entries by competition
    entries_by_comp = defaultdict(list)
    for entry in entries:
        entries_by_comp[entry["competition_id"]].append(entry)
    
    # Track medal counts
    medal_totals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
    
    # Track per-competition wins
    comp_athlete_medals = defaultdict(lambda: defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0}))
    
    # Track individual simulation results
    simulation_results = []
    
    for sim in range(NUM_SIMULATIONS):
        sim_medals = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
        
        for comp_id, comp_entries in entries_by_comp.items():
            scoring_type = get_scoring_type(comp_id, competitions, sports)
            
            gold, silver, bronze = simulate_competition(comp_entries, scoring_type)
            
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


def get_representative_simulation(simulation_results, countries):
    """Find the simulation closest to median total medals."""
    sim_totals = []
    for i, sim in enumerate(simulation_results):
        total = 0
        for country in countries:
            total += sim.get(country, {}).get("gold", 0)
            total += sim.get(country, {}).get("silver", 0)
            total += sim.get(country, {}).get("bronze", 0)
        sim_totals.append((i, total))
    
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
    print("\nNORDIC MEDAL PREDICTIONS - 2026 Winter Olympics (V2)")
    print("(Bradley-Terry inspired with position-weighted probabilities)")
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
    output_path = output_dir / f"v2_predictions{output_suffix}.csv"
    
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
    
    comp_output_path = output_dir / f"v2_competition_predictions{output_suffix}.csv"
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
    
    print(f"\n=== V2 MODEL PARAMETERS ===")
    print(f"Gold power: {GOLD_POWER} (higher = favorites dominate gold)")
    print(f"Silver power: {SILVER_POWER}")
    print(f"Bronze power: {BRONZE_POWER} (most random)")
    print(f"Top N contenders: {TOP_N_CONTENDERS}")
    
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
