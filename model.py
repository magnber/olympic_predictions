"""
Base Competition Model - Plackett-Luce

This module contains the deterministic model for predicting competition outcomes.
It calculates EXACT probabilities without simulation.

The Plackett-Luce model is a probabilistic model for rankings:
- Each athlete has a "strength" parameter
- P(athlete i wins) = strength_i / sum(all strengths)
- For subsequent positions, remove the winner and repeat

Key property: We can calculate exact gold/silver/bronze probabilities
without Monte Carlo simulation!
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import math


@dataclass
class AthleteStrength:
    """Athlete with calculated strength for a competition."""
    athlete_id: str
    name: str
    country: str
    score: float
    strength: float  # Transformed score for model


@dataclass
class CompetitionPrediction:
    """Exact model predictions for a competition (no simulation)."""
    competition_id: str
    competition_name: str
    sport: str
    athletes: List['AthletePrediction']
    
    def get_by_country(self, country: str) -> List['AthletePrediction']:
        return [a for a in self.athletes if a.country == country]


@dataclass
class AthletePrediction:
    """Exact predicted probabilities for one athlete."""
    athlete_id: str
    name: str
    country: str
    score: float
    strength: float
    gold_prob: float
    silver_prob: float
    bronze_prob: float
    
    @property
    def medal_prob(self) -> float:
        return self.gold_prob + self.silver_prob + self.bronze_prob


class PlackettLuceModel:
    """
    Plackett-Luce competition model.
    
    Calculates exact probabilities for gold, silver, bronze positions.
    
    Parameters:
        strength_power: Exponent to apply to normalized scores.
                       Higher = more advantage for top athletes.
                       1.0 = linear (scores are strengths)
                       2.0 = quadratic (gaps amplified)
    
    Example:
        >>> model = PlackettLuceModel(strength_power=2.0)
        >>> athletes = [
        ...     AthleteStrength("1", "Klæbo", "NOR", 927, 0),
        ...     AthleteStrength("2", "Valnes", "NOR", 828, 0),
        ...     AthleteStrength("3", "Anger", "SWE", 784, 0),
        ... ]
        >>> predictions = model.predict(athletes)
        >>> print(predictions[0].gold_prob)  # Klæbo's gold probability
    """
    
    def __init__(self, strength_power: float = 2.0):
        self.strength_power = strength_power
    
    def calculate_strengths(self, athletes: List[AthleteStrength]) -> List[AthleteStrength]:
        """
        Calculate strength from scores using power transformation.
        
        strength = (score / max_score) ^ power
        
        This normalizes scores to [0,1] and amplifies differences.
        """
        if not athletes:
            return []
        
        max_score = max(a.score for a in athletes)
        
        for a in athletes:
            relative_score = a.score / max_score
            a.strength = relative_score ** self.strength_power
        
        return athletes
    
    def predict(self, athletes: List[AthleteStrength]) -> List[AthletePrediction]:
        """
        Calculate exact gold/silver/bronze probabilities for all athletes.
        
        Uses Plackett-Luce closed-form expressions.
        """
        if len(athletes) < 3:
            return []
        
        # Ensure strengths are calculated
        athletes = self.calculate_strengths(athletes)
        
        n = len(athletes)
        strengths = [a.strength for a in athletes]
        total_strength = sum(strengths)
        
        predictions = []
        
        for i, athlete in enumerate(athletes):
            gold_prob = self._gold_probability(strengths, i)
            silver_prob = self._silver_probability(strengths, i)
            bronze_prob = self._bronze_probability(strengths, i)
            
            predictions.append(AthletePrediction(
                athlete_id=athlete.athlete_id,
                name=athlete.name,
                country=athlete.country,
                score=athlete.score,
                strength=athlete.strength,
                gold_prob=gold_prob,
                silver_prob=silver_prob,
                bronze_prob=bronze_prob
            ))
        
        return predictions
    
    def _gold_probability(self, strengths: List[float], athlete_idx: int) -> float:
        """
        P(athlete i wins) = strength_i / sum(strengths)
        """
        total = sum(strengths)
        return strengths[athlete_idx] / total
    
    def _silver_probability(self, strengths: List[float], athlete_idx: int) -> float:
        """
        P(athlete i gets silver) = sum over all k != i of:
            P(k wins) * P(i wins among remaining | k won)
        
        = sum_{k != i} [ s_k / S ] * [ s_i / (S - s_k) ]
        
        where S = sum of all strengths
        """
        n = len(strengths)
        s_i = strengths[athlete_idx]
        S = sum(strengths)
        
        silver_prob = 0.0
        for k in range(n):
            if k == athlete_idx:
                continue
            
            # P(k wins)
            p_k_wins = strengths[k] / S
            
            # P(i wins among remaining after k removed)
            remaining_strength = S - strengths[k]
            p_i_second_given_k = s_i / remaining_strength
            
            silver_prob += p_k_wins * p_i_second_given_k
        
        return silver_prob
    
    def _bronze_probability(self, strengths: List[float], athlete_idx: int) -> float:
        """
        P(athlete i gets bronze) = sum over all pairs (k,j) where k,j != i of:
            P(k wins) * P(j second | k won) * P(i third | k,j took 1st,2nd)
        
        This is more complex but still closed-form.
        """
        n = len(strengths)
        s_i = strengths[athlete_idx]
        S = sum(strengths)
        
        bronze_prob = 0.0
        
        for k in range(n):
            if k == athlete_idx:
                continue
            
            s_k = strengths[k]
            p_k_wins = s_k / S
            
            for j in range(n):
                if j == athlete_idx or j == k:
                    continue
                
                s_j = strengths[j]
                
                # P(j second | k won)
                remaining_after_k = S - s_k
                p_j_second_given_k = s_j / remaining_after_k
                
                # P(i third | k won, j second)
                remaining_after_kj = S - s_k - s_j
                p_i_third_given_kj = s_i / remaining_after_kj
                
                bronze_prob += p_k_wins * p_j_second_given_k * p_i_third_given_kj
        
        return bronze_prob
    
    def validate_predictions(self, predictions: List[AthletePrediction]) -> Dict[str, float]:
        """
        Validate that predictions are consistent.
        
        Checks:
        - All probabilities >= 0
        - Gold probabilities sum to 1.0
        - Silver probabilities sum to 1.0
        - Bronze probabilities sum to 1.0
        """
        gold_sum = sum(p.gold_prob for p in predictions)
        silver_sum = sum(p.silver_prob for p in predictions)
        bronze_sum = sum(p.bronze_prob for p in predictions)
        
        return {
            "gold_sum": gold_sum,
            "silver_sum": silver_sum,
            "bronze_sum": bronze_sum,
            "gold_valid": abs(gold_sum - 1.0) < 0.001,
            "silver_valid": abs(silver_sum - 1.0) < 0.001,
            "bronze_valid": abs(bronze_sum - 1.0) < 0.001,
            "all_valid": (abs(gold_sum - 1.0) < 0.001 and 
                         abs(silver_sum - 1.0) < 0.001 and 
                         abs(bronze_sum - 1.0) < 0.001)
        }


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def create_athletes_from_scores(data: List[Dict]) -> List[AthleteStrength]:
    """
    Create AthleteStrength list from simple dict data.
    
    Args:
        data: List of {"id": str, "name": str, "country": str, "score": float}
    
    Returns:
        List of AthleteStrength objects
    """
    return [
        AthleteStrength(
            athlete_id=d["id"],
            name=d["name"],
            country=d["country"],
            score=d["score"],
            strength=0  # Will be calculated by model
        )
        for d in data
    ]


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":
    # Demo: Men's Sprint cross-country
    print("=" * 70)
    print("PLACKETT-LUCE MODEL - DEMO")
    print("=" * 70)
    
    # Sample data
    athletes_data = [
        {"id": "1", "name": "Johannes Klæbo", "country": "NOR", "score": 927},
        {"id": "2", "name": "Erik Valnes", "country": "NOR", "score": 828},
        {"id": "3", "name": "Edvin Anger", "country": "SWE", "score": 784},
        {"id": "4", "name": "Lucas Chanavat", "country": "FRA", "score": 731},
        {"id": "5", "name": "Even Northug", "country": "NOR", "score": 699},
        {"id": "6", "name": "Federico Pellegrino", "country": "ITA", "score": 694},
        {"id": "7", "name": "Ben Ogden", "country": "USA", "score": 544},
        {"id": "8", "name": "Lauri Vuorinen", "country": "FIN", "score": 525},
    ]
    
    athletes = create_athletes_from_scores(athletes_data)
    
    # Test with different power values
    for power in [1.0, 2.0, 3.0]:
        print(f"\n{'=' * 70}")
        print(f"STRENGTH_POWER = {power}")
        print(f"{'=' * 70}")
        
        model = PlackettLuceModel(strength_power=power)
        predictions = model.predict(athletes)
        
        # Validate
        validation = model.validate_predictions(predictions)
        print(f"\nValidation: Gold sum={validation['gold_sum']:.4f}, "
              f"Silver sum={validation['silver_sum']:.4f}, "
              f"Bronze sum={validation['bronze_sum']:.4f}")
        print(f"All valid: {validation['all_valid']}")
        
        # Show results
        print(f"\n{'Athlete':<25}{'Score':>8}{'Strength':>10}{'P(G)':>10}{'P(S)':>10}{'P(B)':>10}{'P(Medal)':>10}")
        print("-" * 85)
        
        for p in sorted(predictions, key=lambda x: -x.gold_prob):
            print(f"{p.name:<25}{p.score:>8.0f}{p.strength:>10.3f}"
                  f"{p.gold_prob*100:>9.1f}%{p.silver_prob*100:>9.1f}%"
                  f"{p.bronze_prob*100:>9.1f}%{p.medal_prob*100:>9.1f}%")
        
        # Country aggregation
        print(f"\nBy country:")
        country_medals = {}
        for p in predictions:
            if p.country not in country_medals:
                country_medals[p.country] = {"gold": 0, "silver": 0, "bronze": 0}
            country_medals[p.country]["gold"] += p.gold_prob
            country_medals[p.country]["silver"] += p.silver_prob
            country_medals[p.country]["bronze"] += p.bronze_prob
        
        for country, medals in sorted(country_medals.items(), key=lambda x: -x[1]["gold"]):
            total = medals["gold"] + medals["silver"] + medals["bronze"]
            print(f"  {country}: G={medals['gold']:.2f} S={medals['silver']:.2f} "
                  f"B={medals['bronze']:.2f} Total={total:.2f}")
