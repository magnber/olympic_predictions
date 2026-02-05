"""
Excluded Athletes for V2 Pipeline

Athletes who should be excluded from predictions due to:
- Injury
- Retirement
- Not participating in 2026 Olympics

Format: (name, country_code, reason)
"""

EXCLUDED_ATHLETES = [
    # Alpine
    ("Aleksander Aamodt Kilde", "NOR", "Shoulder injury and sepsis - uncertain return"),
    ("Alexander Steen Olsen", "NOR", "Knee surgery Dec 2025 - out for 2025/26 season"),
    ("Lara Gut-Behrami", "SUI", "ACL tear Nov 2024 - confirmed out for 2026 Olympics"),
    
    # Add more as needed:
    # ("Athlete Name", "COUNTRY", "Reason"),
]


def get_excluded_set():
    """Return set of (name, country) tuples for quick lookup."""
    return {(name, country) for name, country, _ in EXCLUDED_ATHLETES}


def get_excluded_with_reasons():
    """Return full list with reasons."""
    return EXCLUDED_ATHLETES


if __name__ == "__main__":
    print("Excluded Athletes for 2026 Olympics:")
    print("-" * 60)
    for name, country, reason in EXCLUDED_ATHLETES:
        print(f"  {name} ({country})")
        print(f"    Reason: {reason}")
