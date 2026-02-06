#!/usr/bin/env python3
"""
Olympic Prediction Engine

Integrates:
- model.py: Plackett-Luce base model (exact probabilities)
- simulator.py: Monte Carlo simulation
- models.py: Output data structures for drilldown

Pipeline:
1. Load data from SQLite
2. Calculate exact probabilities using Plackett-Luce model
3. Run Monte Carlo simulation for confidence intervals
4. Output to structured format supporting country → competition → athlete drilldown
"""

from collections import defaultdict
from pathlib import Path

from database import get_connection
from model import PlackettLuceModel, AthleteStrength, create_athletes_from_scores
from simulator import MonteCarloSimulator, SimulationConfig
from models import (
    AthleteCompetitionResult,
    CompetitionResult,
    CountryCompetitionBreakdown,
    CountrySummary,
    SimulationOutput
)

# ============================================================
# CONFIGURATION
# ============================================================

STRENGTH_POWER = 2.0      # Power transformation for scores
NUM_SIMULATIONS = 100000  # Monte Carlo iterations
EXTRA_NOISE = 0.0         # Extra noise beyond Plackett-Luce (0 = pure model)

OUTPUT_DIR = Path(__file__).parent / "output"


# ============================================================
# DATA LOADING
# ============================================================

def load_data_from_db():
    """Load competition, athlete, and entry data from database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get competitions with sport info
    cursor.execute("""
        SELECT c.id, c.sport_id, c.name, c.gender, s.name as sport_name
        FROM competitions c
        JOIN sports s ON c.sport_id = s.id
    """)
    competitions = {}
    for row in cursor.fetchall():
        competitions[row[0]] = {
            "id": row[0],
            "sport_id": row[1],
            "name": row[2],
            "gender": row[3],
            "sport_name": row[4]
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
    
    # Get entries grouped by competition
    cursor.execute("""
        SELECT e.athlete_id, e.competition_id, e.score
        FROM entries e
    """)
    
    entries_by_comp = defaultdict(list)
    for row in cursor.fetchall():
        athlete_id, comp_id, score = row
        if athlete_id in athletes and comp_id in competitions:
            entries_by_comp[comp_id].append({
                "id": athlete_id,
                "name": athletes[athlete_id]["name"],
                "country": athletes[athlete_id]["country"],
                "score": score
            })
    
    conn.close()
    return competitions, entries_by_comp


# ============================================================
# PREDICTION PIPELINE
# ============================================================

def run_predictions():
    """Run full prediction pipeline."""
    
    print("=" * 70)
    print("OLYMPIC PREDICTIONS 2026")
    print(f"Model: Plackett-Luce (power={STRENGTH_POWER})")
    print(f"Simulation: {NUM_SIMULATIONS:,} iterations")
    print("=" * 70)
    
    # 1. Load data
    print("\n[1/4] Loading data from database...")
    competitions, entries_by_comp = load_data_from_db()
    print(f"      {len(competitions)} competitions")
    print(f"      {sum(len(e) for e in entries_by_comp.values())} total entries")
    
    # 2. Initialize model and simulator
    print("\n[2/4] Initializing model...")
    model = PlackettLuceModel(strength_power=STRENGTH_POWER)
    
    config = SimulationConfig(
        num_simulations=NUM_SIMULATIONS,
        extra_noise_scale=EXTRA_NOISE
    )
    simulator = MonteCarloSimulator(model, config)
    
    # 3. Process each competition
    print(f"\n[3/4] Processing {len(entries_by_comp)} competitions...")
    
    competition_results = []
    country_totals = defaultdict(lambda: {
        "gold": 0, "silver": 0, "bronze": 0,
        "breakdowns": []
    })
    
    comp_count = 0
    for comp_id, entries in entries_by_comp.items():
        if len(entries) < 3:
            continue
        
        comp_info = competitions[comp_id]
        comp_count += 1
        
        # Create AthleteStrength objects
        athletes = create_athletes_from_scores(entries)
        
        # Get exact predictions from model
        exact_predictions = model.predict(athletes)
        
        # Run simulation
        sim_results = simulator.simulate_competition(athletes)
        
        # Build athlete results (using simulation results)
        athlete_results = []
        country_comp_medals = defaultdict(lambda: {
            "gold": 0, "silver": 0, "bronze": 0, "athletes": []
        })
        
        for sim_result in sim_results:
            result = AthleteCompetitionResult(
                athlete_id=sim_result.athlete_id,
                athlete_name=sim_result.name,
                country=sim_result.country,
                score=0,  # Will get from exact predictions
                relative_score=0,
                strength=0,
                gold_prob=sim_result.sim_gold_prob,
                silver_prob=sim_result.sim_silver_prob,
                bronze_prob=sim_result.sim_bronze_prob
            )
            
            # Get score/strength from exact predictions
            for ep in exact_predictions:
                if ep.athlete_id == sim_result.athlete_id:
                    result.score = ep.score
                    result.strength = ep.strength
                    break
            
            athlete_results.append(result)
            
            # Aggregate by country for this competition
            country = sim_result.country
            country_comp_medals[country]["gold"] += sim_result.sim_gold_prob
            country_comp_medals[country]["silver"] += sim_result.sim_silver_prob
            country_comp_medals[country]["bronze"] += sim_result.sim_bronze_prob
            country_comp_medals[country]["athletes"].append({
                "name": sim_result.name,
                "gold_prob": sim_result.sim_gold_prob
            })
            
            # Add to country totals
            country_totals[country]["gold"] += sim_result.sim_gold_prob
            country_totals[country]["silver"] += sim_result.sim_silver_prob
            country_totals[country]["bronze"] += sim_result.sim_bronze_prob
        
        # Sort by gold probability
        athlete_results.sort(key=lambda x: -x.gold_prob)
        
        # Create CompetitionResult
        competition_results.append(CompetitionResult(
            competition_id=comp_id,
            competition_name=comp_info["name"],
            sport=comp_info["sport_name"],
            gender=comp_info["gender"],
            athlete_results=athlete_results
        ))
        
        # Create CountryCompetitionBreakdown for each country
        for country, medals in country_comp_medals.items():
            total = medals["gold"] + medals["silver"] + medals["bronze"]
            if total < 0.01:
                continue
            
            top_athlete = max(medals["athletes"], key=lambda x: x["gold_prob"])
            
            breakdown = CountryCompetitionBreakdown(
                country=country,
                sport=comp_info["sport_name"],
                competition=comp_info["name"],
                competition_id=comp_id,
                expected_gold=medals["gold"],
                expected_silver=medals["silver"],
                expected_bronze=medals["bronze"],
                top_athlete=top_athlete["name"],
                top_athlete_gold_prob=top_athlete["gold_prob"]
            )
            country_totals[country]["breakdowns"].append(breakdown)
        
        if comp_count % 20 == 0:
            print(f"      Processed {comp_count} competitions...")
    
    print(f"      Processed {comp_count} competitions total")
    
    # 4. Build country summaries
    print("\n[4/4] Building output...")
    
    country_summaries = []
    for country, data in country_totals.items():
        summary = CountrySummary(
            country=country,
            gold=data["gold"],
            silver=data["silver"],
            bronze=data["bronze"],
            competition_breakdown=data["breakdowns"]
        )
        country_summaries.append(summary)
    
    # Sort by total medals
    country_summaries.sort(key=lambda x: -x.total)
    
    # Create SimulationOutput
    output = SimulationOutput(
        num_simulations=NUM_SIMULATIONS,
        strength_power=STRENGTH_POWER,
        noise_scale=EXTRA_NOISE,
        country_summaries=country_summaries,
        competition_results=competition_results
    )
    
    return output


def main():
    """Main entry point."""
    output = run_predictions()
    
    # Save outputs
    print("\nSaving outputs...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    output.save_all(OUTPUT_DIR)
    
    # Print summary
    output.print_summary()
    
    # Show drilldown example
    print("\n" + "=" * 70)
    print("DRILLDOWN EXAMPLE: Norway")
    print("=" * 70)
    
    norway = output.get_country("NOR")
    if norway:
        print(f"\nTotal: {norway.total:.1f} medals (G:{norway.gold:.1f} S:{norway.silver:.1f} B:{norway.bronze:.1f})")
        print(f"\nTop 10 competitions contributing to Norway's medals:")
        print(f"{'Competition':<35}{'Sport':<15}{'E[G]':>8}{'E[Total]':>10}{'Top Athlete':<25}")
        print("-" * 95)
        
        for comp in norway.get_top_competitions(10):
            print(f"{comp.competition[:34]:<35}{comp.sport[:14]:<15}"
                  f"{comp.expected_gold:>8.2f}{comp.expected_total:>10.2f}"
                  f"{comp.top_athlete[:24]:<25}")


if __name__ == "__main__":
    main()
