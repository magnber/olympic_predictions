"""
Data models for Olympic Predictions.

Defines the output structure from the prediction model and simulation.
Uses dataclasses for clear, typed data structures.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import csv
from pathlib import Path


# ============================================================
# ATHLETE & COMPETITION MODELS
# ============================================================

@dataclass
class AthleteEntry:
    """An athlete's entry in a competition with calculated strength."""
    athlete_id: str
    athlete_name: str
    country: str
    score: float
    relative_score: float  # score / max_score in competition (0-1)
    strength: float        # relative_score ** POWER
    base_win_prob: float   # strength / total_strength (before simulation)


@dataclass
class AthleteCompetitionResult:
    """Result of simulation for one athlete in one competition."""
    athlete_id: str
    athlete_name: str
    country: str
    score: float
    relative_score: float
    strength: float
    gold_prob: float       # P(gold) from simulations
    silver_prob: float     # P(silver) from simulations
    bronze_prob: float     # P(bronze) from simulations
    
    @property
    def medal_prob(self) -> float:
        """Probability of any medal."""
        return self.gold_prob + self.silver_prob + self.bronze_prob
    
    def to_dict(self) -> dict:
        return {
            "athlete_id": self.athlete_id,
            "athlete_name": self.athlete_name,
            "country": self.country,
            "score": self.score,
            "relative_score": round(self.relative_score, 3),
            "strength": round(self.strength, 4),
            "gold_prob": round(self.gold_prob, 4),
            "silver_prob": round(self.silver_prob, 4),
            "bronze_prob": round(self.bronze_prob, 4),
            "medal_prob": round(self.medal_prob, 4)
        }


@dataclass
class CompetitionResult:
    """Full results for one competition after simulation."""
    competition_id: str
    competition_name: str
    sport: str
    gender: str
    athlete_results: List[AthleteCompetitionResult] = field(default_factory=list)
    
    def get_top_athletes(self, n: int = 5) -> List[AthleteCompetitionResult]:
        """Get top N athletes by gold probability."""
        return sorted(self.athlete_results, key=lambda x: -x.gold_prob)[:n]
    
    def get_country_breakdown(self) -> Dict[str, dict]:
        """Aggregate results by country for this competition."""
        country_medals = {}
        
        for result in self.athlete_results:
            country = result.country
            if country not in country_medals:
                country_medals[country] = {
                    "expected_gold": 0,
                    "expected_silver": 0,
                    "expected_bronze": 0,
                    "athletes": []
                }
            
            country_medals[country]["expected_gold"] += result.gold_prob
            country_medals[country]["expected_silver"] += result.silver_prob
            country_medals[country]["expected_bronze"] += result.bronze_prob
            country_medals[country]["athletes"].append({
                "name": result.athlete_name,
                "gold_prob": result.gold_prob
            })
        
        return country_medals


# ============================================================
# COUNTRY-LEVEL MODELS
# ============================================================

@dataclass
class CountryCompetitionBreakdown:
    """How a country performs in a specific competition."""
    country: str
    sport: str
    competition: str
    competition_id: str
    expected_gold: float
    expected_silver: float
    expected_bronze: float
    top_athlete: str
    top_athlete_gold_prob: float
    
    @property
    def expected_total(self) -> float:
        return self.expected_gold + self.expected_silver + self.expected_bronze
    
    def to_dict(self) -> dict:
        return {
            "country": self.country,
            "sport": self.sport,
            "competition": self.competition,
            "competition_id": self.competition_id,
            "expected_gold": round(self.expected_gold, 3),
            "expected_silver": round(self.expected_silver, 3),
            "expected_bronze": round(self.expected_bronze, 3),
            "expected_total": round(self.expected_total, 3),
            "top_athlete": self.top_athlete,
            "top_athlete_gold_prob": round(self.top_athlete_gold_prob, 3)
        }


@dataclass
class CountrySummary:
    """Total medal expectations for a country."""
    country: str
    gold: float
    silver: float
    bronze: float
    competition_breakdown: List[CountryCompetitionBreakdown] = field(default_factory=list)
    
    @property
    def total(self) -> float:
        return self.gold + self.silver + self.bronze
    
    def to_dict(self) -> dict:
        return {
            "country": self.country,
            "gold": round(self.gold, 2),
            "silver": round(self.silver, 2),
            "bronze": round(self.bronze, 2),
            "total": round(self.total, 2)
        }
    
    def get_top_competitions(self, n: int = 10) -> List[CountryCompetitionBreakdown]:
        """Get top N competitions by expected medals."""
        return sorted(self.competition_breakdown, key=lambda x: -x.expected_total)[:n]


# ============================================================
# SIMULATION OUTPUT
# ============================================================

@dataclass
class SimulationOutput:
    """
    Complete output from a prediction simulation.
    
    This is the main container for all results.
    """
    # Configuration used
    num_simulations: int
    strength_power: float
    noise_scale: float
    
    # Results
    country_summaries: List[CountrySummary] = field(default_factory=list)
    competition_results: List[CompetitionResult] = field(default_factory=list)
    
    def get_country(self, country_code: str) -> Optional[CountrySummary]:
        """Get summary for a specific country."""
        for c in self.country_summaries:
            if c.country == country_code:
                return c
        return None
    
    def get_competition(self, competition_id: str) -> Optional[CompetitionResult]:
        """Get results for a specific competition."""
        for c in self.competition_results:
            if c.competition_id == competition_id:
                return c
        return None
    
    def get_top_countries(self, n: int = 10) -> List[CountrySummary]:
        """Get top N countries by total medals."""
        return sorted(self.country_summaries, key=lambda x: -x.total)[:n]
    
    # --------------------------------------------------------
    # EXPORT METHODS
    # --------------------------------------------------------
    
    def save_all(self, output_dir: Path):
        """Save all output files."""
        output_dir.mkdir(exist_ok=True)
        
        self.save_country_summary(output_dir / "predictions.csv")
        self.save_country_competition_breakdown(output_dir / "country_competition_breakdown.csv")
        self.save_competition_details(output_dir / "competition_details.csv")
        self.save_competition_predictions(output_dir / "competition_predictions.csv")
    
    def save_country_summary(self, filepath: Path):
        """Save country summary to CSV."""
        sorted_countries = sorted(self.country_summaries, key=lambda x: -x.total)
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["country", "gold", "silver", "bronze", "total"])
            writer.writeheader()
            for country in sorted_countries:
                writer.writerow(country.to_dict())
        
        print(f"Saved: {filepath}")
    
    def save_country_competition_breakdown(self, filepath: Path):
        """Save country-competition breakdown to CSV."""
        all_breakdown = []
        
        for country in self.country_summaries:
            for comp in country.competition_breakdown:
                if comp.expected_total >= 0.01:  # Skip negligible
                    all_breakdown.append(comp.to_dict())
        
        # Sort by expected total descending
        all_breakdown.sort(key=lambda x: (-x["expected_total"], x["country"]))
        
        fieldnames = ["country", "sport", "competition", "expected_gold", 
                     "expected_silver", "expected_bronze", "expected_total",
                     "top_athlete", "top_athlete_gold_prob"]
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_breakdown)
        
        print(f"Saved: {filepath}")
    
    def save_competition_details(self, filepath: Path):
        """Save full competition details to CSV."""
        all_details = []
        
        for comp in self.competition_results:
            for athlete in comp.athlete_results:
                row = athlete.to_dict()
                row["competition"] = comp.competition_name
                row["competition_id"] = comp.competition_id
                row["sport"] = comp.sport
                all_details.append(row)
        
        # Sort by competition, then gold_prob descending
        all_details.sort(key=lambda x: (x["competition"], -x["gold_prob"]))
        
        fieldnames = ["competition", "sport", "athlete_name", "country", "score",
                     "relative_score", "strength", "gold_prob", "silver_prob",
                     "bronze_prob", "medal_prob"]
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_details)
        
        print(f"Saved: {filepath}")
    
    def save_competition_predictions(self, filepath: Path):
        """Save competition predictions (legacy format for Streamlit compatibility)."""
        all_predictions = []
        
        for comp in self.competition_results:
            for athlete in comp.athlete_results:
                all_predictions.append({
                    "competition": comp.competition_name,
                    "athlete_id": athlete.athlete_id,
                    "athlete_name": athlete.athlete_name,
                    "country": athlete.country,
                    "gold_prob": round(athlete.gold_prob, 4),
                    "silver_prob": round(athlete.silver_prob, 4),
                    "bronze_prob": round(athlete.bronze_prob, 4),
                    "medal_prob": round(athlete.medal_prob, 4)
                })
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "competition", "athlete_id", "athlete_name", "country",
                "gold_prob", "silver_prob", "bronze_prob", "medal_prob"
            ])
            writer.writeheader()
            writer.writerows(all_predictions)
        
        print(f"Saved: {filepath}")
    
    # --------------------------------------------------------
    # DISPLAY METHODS
    # --------------------------------------------------------
    
    def print_summary(self):
        """Print summary to console."""
        print("\n" + "=" * 70)
        print("MEDAL PREDICTIONS - Winter Olympics 2026")
        print(f"Model: Power={self.strength_power}, Noise={self.noise_scale}, "
              f"Sims={self.num_simulations:,}")
        print("=" * 70)
        
        # Top 10 countries
        print(f"\n{'Rank':<6}{'Country':<10}{'Gold':>8}{'Silver':>8}{'Bronze':>8}{'Total':>8}")
        print("-" * 50)
        
        for i, c in enumerate(self.get_top_countries(10), 1):
            print(f"{i:<6}{c.country:<10}{c.gold:>8.1f}{c.silver:>8.1f}"
                  f"{c.bronze:>8.1f}{c.total:>8.1f}")
        
        # Top country breakdown
        if self.country_summaries:
            top_country = self.get_top_countries(1)[0]
            print(f"\n{'=' * 70}")
            print(f"BREAKDOWN: {top_country.country}")
            print(f"{'=' * 70}")
            
            top_comps = top_country.get_top_competitions(10)
            print(f"\n{'Competition':<30}{'E[G]':>8}{'E[S]':>8}{'E[B]':>8}{'Total':>8}")
            print("-" * 60)
            
            for comp in top_comps:
                print(f"{comp.competition[:29]:<30}{comp.expected_gold:>8.2f}"
                      f"{comp.expected_silver:>8.2f}{comp.expected_bronze:>8.2f}"
                      f"{comp.expected_total:>8.2f}")
        
        # Nordic countries
        print(f"\n{'=' * 70}")
        print("NORDIC COUNTRIES")
        print("=" * 70)
        
        for code in ["NOR", "SWE", "FIN", "DEN"]:
            country = self.get_country(code)
            if country:
                print(f"{code}: {country.total:.1f} medals "
                      f"(G:{country.gold:.1f} S:{country.silver:.1f} B:{country.bronze:.1f})")
