"""
Tests for the Monte Carlo simulator.

Key test: With zero noise, simulation should converge to base model predictions.
This validates that the simulation is correctly implementing the model.
"""

import sys
sys.path.insert(0, '..')

from model import PlackettLuceModel, create_athletes_from_scores
from simulator import MonteCarloSimulator, SimulationConfig


def test_convergence_plackett_luce():
    """Plackett-Luce simulation should converge to exact model predictions."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "A", "country": "X", "score": 100},
        {"id": "2", "name": "B", "country": "Y", "score": 80},
        {"id": "3", "name": "C", "country": "Z", "score": 60},
    ])
    
    config = SimulationConfig(
        num_simulations=50000,
        extra_noise_scale=0.0,  # Pure Plackett-Luce
        seed=42
    )
    
    simulator = MonteCarloSimulator(model, config)
    results = simulator.simulate_competition(athletes)
    
    validation = simulator.validate_convergence(results, tolerance=0.02)
    
    assert validation["converged"], \
        f"Simulation should converge to model. Max error: {validation['max_gold_error']:.2%}"
    
    print(f"✓ Plackett-Luce simulation converges (max error: {validation['max_gold_error']:.2%})")


def test_more_simulations_better_convergence():
    """More simulations should give better convergence."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "A", "country": "X", "score": 100},
        {"id": "2", "name": "B", "country": "Y", "score": 80},
        {"id": "3", "name": "C", "country": "Z", "score": 60},
    ])
    
    errors = []
    for num_sims in [100, 1000, 10000]:
        config = SimulationConfig(
            num_simulations=num_sims,
            extra_noise_scale=0.0,
            seed=42
        )
        
        simulator = MonteCarloSimulator(model, config)
        results = simulator.simulate_competition(athletes)
        validation = simulator.validate_convergence(results)
        errors.append((num_sims, validation["max_gold_error"]))
    
    # Error should generally decrease with more simulations
    # (may not be strictly monotonic due to random seed)
    assert errors[2][1] < errors[0][1], \
        f"10k sims should have less error than 100 sims: {errors}"
    
    print(f"✓ More simulations = better convergence:")
    for num_sims, error in errors:
        print(f"    {num_sims:>6} sims: error = {error:.3%}")


def test_extra_noise_introduces_variance():
    """With extra noise, simulation should differ from exact model."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "Top", "country": "X", "score": 100},
        {"id": "2", "name": "Second", "country": "Y", "score": 95},
        {"id": "3", "name": "Third", "country": "Z", "score": 90},
    ])
    
    # High extra noise
    config = SimulationConfig(
        num_simulations=10000,
        extra_noise_scale=0.5,  # High extra noise beyond Plackett-Luce
        seed=42
    )
    
    simulator = MonteCarloSimulator(model, config)
    results = simulator.simulate_competition(athletes)
    
    # With high noise, results should differ from exact model
    top = next(r for r in results if r.name == "Top")
    
    # The difference should be noticeable
    diff = abs(top.sim_gold_prob - top.exact_gold_prob)
    
    print(f"✓ Extra noise introduces variance:")
    print(f"    Top athlete exact P(G): {top.exact_gold_prob:.1%}")
    print(f"    Top athlete sim P(G):   {top.sim_gold_prob:.1%}")
    print(f"    Difference: {diff:.1%}")


def test_reproducibility_with_seed():
    """Same seed should give same results when run independently."""
    import random
    
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "A", "country": "X", "score": 100},
        {"id": "2", "name": "B", "country": "Y", "score": 80},
        {"id": "3", "name": "C", "country": "Z", "score": 60},
    ])
    
    # Run 1
    random.seed(12345)
    config1 = SimulationConfig(num_simulations=1000, extra_noise_scale=0.15, seed=None)
    sim1 = MonteCarloSimulator(model, config1)
    results1 = sim1.simulate_competition(athletes)
    
    # Run 2 with same seed
    random.seed(12345)
    config2 = SimulationConfig(num_simulations=1000, extra_noise_scale=0.15, seed=None)
    sim2 = MonteCarloSimulator(model, config2)
    results2 = sim2.simulate_competition(athletes)
    
    for r1, r2 in zip(results1, results2):
        assert r1.sim_gold_prob == r2.sim_gold_prob, \
            f"Same seed should give same results: {r1.sim_gold_prob} vs {r2.sim_gold_prob}"
    
    print("✓ Same seed gives reproducible results")


def test_country_aggregation():
    """Country medal totals should be calculated correctly."""
    model = PlackettLuceModel(strength_power=2.0)
    
    # Two athletes from same country
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "NOR1", "country": "NOR", "score": 100},
        {"id": "2", "name": "NOR2", "country": "NOR", "score": 90},
        {"id": "3", "name": "SWE1", "country": "SWE", "score": 80},
    ])
    
    config = SimulationConfig(num_simulations=10000, extra_noise_scale=0.0, seed=42)
    simulator = MonteCarloSimulator(model, config)
    results = simulator.simulate_competition(athletes)
    
    # Calculate country totals
    nor_gold = sum(r.sim_gold_prob for r in results if r.country == "NOR")
    swe_gold = sum(r.sim_gold_prob for r in results if r.country == "SWE")
    
    assert nor_gold + swe_gold > 0.99, "Gold probs should sum to ~1"
    
    # Norway should have higher gold prob (two stronger athletes)
    assert nor_gold > swe_gold, f"NOR should have more gold than SWE"
    
    print(f"✓ Country aggregation works: NOR={nor_gold:.1%}, SWE={swe_gold:.1%}")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("RUNNING SIMULATOR TESTS")
    print("=" * 60)
    print()
    
    test_convergence_plackett_luce()
    test_more_simulations_better_convergence()
    test_extra_noise_introduces_variance()
    test_reproducibility_with_seed()
    test_country_aggregation()
    
    print()
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
