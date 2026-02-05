"""
Excluded athletes for Olympic predictions.

Athletes who should not be included in predictions due to:
- Injury
- Retirement
- Not competing at 2026 Olympics
"""

# Format: (name, country, reason)
EXCLUDED_ATHLETES = [
    # Ski Jumping - retirees/injured
    ("Daniela Iraschko-Stolz", "AUT", "retired"),
    ("Maren Lundby", "NOR", "not competing"),
    
    # Cross Country
    ("Therese Johaug", "NOR", "retired"),
    
    # Alpine
    ("Aleksander Aamodt Kilde", "NOR", "injury - out for season"),
    
    # Speed Skating
    ("Ireen Wüst", "NED", "retired"),
]


def get_excluded_set():
    """Return set of (name, country) tuples for quick lookup."""
    return {(name, country) for name, country, _ in EXCLUDED_ATHLETES}


def get_excluded_with_reasons():
    """Return list of (name, country, reason) tuples."""
    return EXCLUDED_ATHLETES
