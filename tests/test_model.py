"""
Tests for the Plackett-Luce base model.

These tests verify that the model calculates correct probabilities
WITHOUT any simulation or randomness.
"""

import sys
sys.path.insert(0, '..')

from model import PlackettLuceModel, AthleteStrength, create_athletes_from_scores


def test_probabilities_sum_to_one():
    """Gold, silver, and bronze probabilities should each sum to 1.0."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "A", "country": "X", "score": 100},
        {"id": "2", "name": "B", "country": "Y", "score": 80},
        {"id": "3", "name": "C", "country": "Z", "score": 60},
        {"id": "4", "name": "D", "country": "X", "score": 40},
    ])
    
    predictions = model.predict(athletes)
    validation = model.validate_predictions(predictions)
    
    assert validation["all_valid"], f"Probabilities don't sum to 1: {validation}"
    print("✓ Probabilities sum to 1.0")


def test_stronger_athlete_wins_more():
    """Athlete with highest score should have highest gold probability."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "Strong", "country": "X", "score": 100},
        {"id": "2", "name": "Medium", "country": "Y", "score": 50},
        {"id": "3", "name": "Weak", "country": "Z", "score": 25},
    ])
    
    predictions = model.predict(athletes)
    
    strong = next(p for p in predictions if p.name == "Strong")
    medium = next(p for p in predictions if p.name == "Medium")
    weak = next(p for p in predictions if p.name == "Weak")
    
    assert strong.gold_prob > medium.gold_prob > weak.gold_prob, \
        f"Expected Strong > Medium > Weak, got {strong.gold_prob}, {medium.gold_prob}, {weak.gold_prob}"
    print("✓ Stronger athletes have higher gold probability")


def test_power_affects_dominance():
    """Higher power should give more advantage to top athlete."""
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "Top", "country": "X", "score": 100},
        {"id": "2", "name": "Second", "country": "Y", "score": 90},
        {"id": "3", "name": "Third", "country": "Z", "score": 80},
    ])
    
    model_low = PlackettLuceModel(strength_power=1.0)
    model_high = PlackettLuceModel(strength_power=3.0)
    
    pred_low = model_low.predict(athletes)
    pred_high = model_high.predict(athletes)
    
    top_low = next(p for p in pred_low if p.name == "Top")
    top_high = next(p for p in pred_high if p.name == "Top")
    
    assert top_high.gold_prob > top_low.gold_prob, \
        f"Higher power should increase top athlete's advantage"
    print(f"✓ Power affects dominance: power=1 gives {top_low.gold_prob:.1%}, power=3 gives {top_high.gold_prob:.1%}")


def test_equal_scores_equal_probs():
    """Athletes with equal scores should have equal probabilities."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "A", "country": "X", "score": 100},
        {"id": "2", "name": "B", "country": "Y", "score": 100},
        {"id": "3", "name": "C", "country": "Z", "score": 100},
    ])
    
    predictions = model.predict(athletes)
    
    gold_probs = [p.gold_prob for p in predictions]
    
    # All should be approximately 1/3
    for p in gold_probs:
        assert abs(p - 1/3) < 0.001, f"Expected ~33.3%, got {p:.1%}"
    
    print("✓ Equal scores give equal probabilities")


def test_dominant_athlete():
    """With very dominant athlete, they should have very high gold prob."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": "1", "name": "Dominant", "country": "X", "score": 1000},
        {"id": "2", "name": "Average1", "country": "Y", "score": 100},
        {"id": "3", "name": "Average2", "country": "Z", "score": 100},
        {"id": "4", "name": "Average3", "country": "W", "score": 100},
    ])
    
    predictions = model.predict(athletes)
    dominant = next(p for p in predictions if p.name == "Dominant")
    
    # With 10x score and power=2, should have very high gold prob
    assert dominant.gold_prob > 0.9, f"Dominant athlete should have >90% gold prob, got {dominant.gold_prob:.1%}"
    
    # And relatively low bronze prob (usually wins, doesn't come 3rd)
    assert dominant.bronze_prob < 0.01, f"Dominant athlete should rarely get bronze, got {dominant.bronze_prob:.1%}"
    
    print(f"✓ Dominant athlete: Gold={dominant.gold_prob:.1%}, Bronze={dominant.bronze_prob:.3%}")


def test_medal_probabilities_consistent():
    """Each athlete's G + S + B <= 1 (can only win one medal per competition)."""
    model = PlackettLuceModel(strength_power=2.0)
    
    athletes = create_athletes_from_scores([
        {"id": str(i), "name": f"Athlete{i}", "country": "X", "score": 100 - i*5}
        for i in range(10)
    ])
    
    predictions = model.predict(athletes)
    
    for p in predictions:
        total = p.gold_prob + p.silver_prob + p.bronze_prob
        assert total <= 1.001, f"{p.name} has medal prob > 1: {total}"
    
    print("✓ All medal probabilities are consistent")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("RUNNING MODEL TESTS")
    print("=" * 60)
    print()
    
    test_probabilities_sum_to_one()
    test_stronger_athlete_wins_more()
    test_power_affects_dominance()
    test_equal_scores_equal_probs()
    test_dominant_athlete()
    test_medal_probabilities_consistent()
    
    print()
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
