"""
Monte Carlo Simulator

This module runs the base model many times with added randomness
to estimate probabilities through simulation.

The simulator:
1. Takes the base model (PlackettLuceModel)
2. Adds Gumbel noise to log-strengths (Plackett-Luce sampling)
3. Simulates many competition outcomes
4. Aggregates results to estimate probabilities

Key insight: With standard Gumbel noise, simulated probabilities CONVERGE 
to the exact Plackett-Luce probabilities as num_simulations → ∞.

Mathematical basis:
    If we add Gumbel(0,1) noise to log(strength), then:
    P(athlete i wins) = strength_i / sum(strengths)
    
    This is exactly the Plackett-Luce model!
"""

import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

from model import PlackettLuceModel, AthleteStrength, AthletePrediction


@dataclass
class SimulationConfig:
    """Configuration for Monte Carlo simulation."""
    num_simulations: int = 10000
    extra_noise_scale: float = 0.0  # Additional noise beyond Plackett-Luce
    seed: Optional[int] = None      # Random seed for reproducibility


@dataclass
class SimulatedResult:
    """Result of simulation for one athlete in one competition."""
    athlete_id: str
    name: str
    country: str
    
    # From base model (exact)
    exact_gold_prob: float
    exact_silver_prob: float
    exact_bronze_prob: float
    
    # From simulation (estimated)
    sim_gold_prob: float
    sim_silver_prob: float
    sim_bronze_prob: float
    
    @property
    def exact_medal_prob(self) -> float:
        return self.exact_gold_prob + self.exact_silver_prob + self.exact_bronze_prob
    
    @property
    def sim_medal_prob(self) -> float:
        return self.sim_gold_prob + self.sim_silver_prob + self.sim_bronze_prob
    
    @property
    def gold_error(self) -> float:
        """Difference between simulated and exact gold probability."""
        return abs(self.sim_gold_prob - self.exact_gold_prob)


class MonteCarloSimulator:
    """
    Monte Carlo simulator for competition outcomes.
    
    Uses the base PlackettLuceModel and adds noise to simulate
    race-day variability.
    
    Example:
        >>> model = PlackettLuceModel(strength_power=2.0)
        >>> simulator = MonteCarloSimulator(model, config)
        >>> results = simulator.simulate_competition(athletes)
    """
    
    def __init__(self, model: PlackettLuceModel, config: SimulationConfig):
        self.model = model
        self.config = config
        
        if config.seed is not None:
            random.seed(config.seed)
    
    def gumbel_noise(self) -> float:
        """
        Generate standard Gumbel(0,1) noise.
        
        This is the key to Plackett-Luce sampling:
        If X = log(strength) + Gumbel(0,1), then
        P(argmax X = i) = strength_i / sum(strengths)
        """
        u = random.random()
        while u == 0:
            u = random.random()
        return -math.log(-math.log(u))
    
    def simulate_once(self, athletes: List[AthleteStrength]) -> Tuple[str, str, str]:
        """
        Simulate one competition outcome using Plackett-Luce sampling.
        
        Method: Add Gumbel(0,1) noise to log(strength), then sort.
        This gives exact Plackett-Luce probabilities.
        
        Optional: Add extra Gaussian noise for more variance.
        
        Returns:
            (gold_id, silver_id, bronze_id) - athlete IDs of medal winners
        """
        noisy_results = []
        
        for a in athletes:
            # Plackett-Luce: log(strength) + Gumbel(0,1)
            log_strength = math.log(max(a.strength, 0.0001))
            gumbel = self.gumbel_noise()
            
            # Optional extra noise (for more variance than pure Plackett-Luce)
            extra_noise = 0.0
            if self.config.extra_noise_scale > 0:
                extra_noise = random.gauss(0, self.config.extra_noise_scale)
            
            noisy_value = log_strength + gumbel + extra_noise
            noisy_results.append((noisy_value, a.athlete_id))
        
        # Sort by noisy value (descending)
        noisy_results.sort(key=lambda x: -x[0])
        
        # Return top 3 athlete IDs
        return noisy_results[0][1], noisy_results[1][1], noisy_results[2][1]
    
    def simulate_competition(self, athletes: List[AthleteStrength]) -> List[SimulatedResult]:
        """
        Run full simulation for a competition.
        
        1. Calculate exact probabilities using base model
        2. Run num_simulations to estimate probabilities
        3. Compare exact vs simulated
        
        Returns:
            List of SimulatedResult with both exact and simulated probabilities
        """
        if len(athletes) < 3:
            return []
        
        # Ensure strengths are calculated
        athletes = self.model.calculate_strengths(athletes)
        
        # Get exact predictions from base model
        exact_predictions = self.model.predict(athletes)
        exact_by_id = {p.athlete_id: p for p in exact_predictions}
        
        # Run simulations
        medal_counts = defaultdict(lambda: {"gold": 0, "silver": 0, "bronze": 0})
        
        for _ in range(self.config.num_simulations):
            gold_id, silver_id, bronze_id = self.simulate_once(athletes)
            medal_counts[gold_id]["gold"] += 1
            medal_counts[silver_id]["silver"] += 1
            medal_counts[bronze_id]["bronze"] += 1
        
        # Build results
        results = []
        for athlete in athletes:
            aid = athlete.athlete_id
            exact = exact_by_id[aid]
            
            sim_gold = medal_counts[aid]["gold"] / self.config.num_simulations
            sim_silver = medal_counts[aid]["silver"] / self.config.num_simulations
            sim_bronze = medal_counts[aid]["bronze"] / self.config.num_simulations
            
            results.append(SimulatedResult(
                athlete_id=aid,
                name=athlete.name,
                country=athlete.country,
                exact_gold_prob=exact.gold_prob,
                exact_silver_prob=exact.silver_prob,
                exact_bronze_prob=exact.bronze_prob,
                sim_gold_prob=sim_gold,
                sim_silver_prob=sim_silver,
                sim_bronze_prob=sim_bronze
            ))
        
        return results
    
    def validate_convergence(self, results: List[SimulatedResult], tolerance: float = 0.02) -> Dict:
        """
        Check if simulated probabilities converge to exact model predictions.
        
        With enough simulations and symmetric noise, they should converge.
        
        Args:
            results: Simulation results
            tolerance: Maximum allowed difference (e.g., 0.02 = 2%)
        
        Returns:
            Validation summary
        """
        gold_errors = [r.gold_error for r in results]
        max_error = max(gold_errors)
        avg_error = sum(gold_errors) / len(gold_errors)
        
        converged = max_error < tolerance
        
        return {
            "converged": converged,
            "max_gold_error": max_error,
            "avg_gold_error": avg_error,
            "tolerance": tolerance,
            "num_simulations": self.config.num_simulations
        }


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":
    from model import create_athletes_from_scores
    
    print("=" * 70)
    print("MONTE CARLO SIMULATOR - DEMO")
    print("=" * 70)
    
    # Sample data
    athletes_data = [
        {"id": "1", "name": "Johannes Klæbo", "country": "NOR", "score": 927},
        {"id": "2", "name": "Erik Valnes", "country": "NOR", "score": 828},
        {"id": "3", "name": "Edvin Anger", "country": "SWE", "score": 784},
        {"id": "4", "name": "Lucas Chanavat", "country": "FRA", "score": 731},
        {"id": "5", "name": "Even Northug", "country": "NOR", "score": 699},
        {"id": "6", "name": "Federico Pellegrino", "country": "ITA", "score": 694},
    ]
    
    athletes = create_athletes_from_scores(athletes_data)
    
    # Create model and simulator
    model = PlackettLuceModel(strength_power=2.0)
    
    # Test with different simulation counts
    for num_sims in [100, 1000, 10000, 100000]:
        print(f"\n{'=' * 70}")
        print(f"NUM_SIMULATIONS = {num_sims:,}")
        print(f"{'=' * 70}")
        
        config = SimulationConfig(
            num_simulations=num_sims,
            noise_scale=0.0,  # No noise = should match exactly
            seed=42
        )
        
        simulator = MonteCarloSimulator(model, config)
        results = simulator.simulate_competition(athletes)
        
        # Check convergence
        validation = simulator.validate_convergence(results)
        print(f"\nConvergence (noise=0): {validation['converged']}")
        print(f"  Max error: {validation['max_gold_error']*100:.2f}%")
        print(f"  Avg error: {validation['avg_gold_error']*100:.2f}%")
        
        # Show comparison
        print(f"\n{'Athlete':<20}{'Exact P(G)':>12}{'Sim P(G)':>12}{'Error':>10}")
        print("-" * 55)
        
        for r in sorted(results, key=lambda x: -x.exact_gold_prob):
            error_pct = abs(r.sim_gold_prob - r.exact_gold_prob) * 100
            print(f"{r.name:<20}{r.exact_gold_prob*100:>11.1f}%"
                  f"{r.sim_gold_prob*100:>11.1f}%{error_pct:>9.1f}%")
    
    # Test with noise
    print(f"\n{'=' * 70}")
    print("WITH NOISE (noise_scale=0.15)")
    print("=" * 70)
    
    config = SimulationConfig(
        num_simulations=100000,
        noise_scale=0.15,
        seed=42
    )
    
    simulator = MonteCarloSimulator(model, config)
    results = simulator.simulate_competition(athletes)
    
    print(f"\n{'Athlete':<20}{'Exact P(G)':>12}{'Sim P(G)':>12}{'Diff':>10}")
    print("-" * 55)
    
    for r in sorted(results, key=lambda x: -x.exact_gold_prob):
        diff = (r.sim_gold_prob - r.exact_gold_prob) * 100
        print(f"{r.name:<20}{r.exact_gold_prob*100:>11.1f}%"
              f"{r.sim_gold_prob*100:>11.1f}%{diff:>+9.1f}%")
    
    print("\nNote: With noise, simulated probabilities will differ from exact model.")
    print("This represents race-day variability and potential upsets.")
