# Technical Implementation

## Data Model

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      Sport      │       │   Competition   │       │     Athlete     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │◄──────│ sport_id        │       │ id              │
│ name            │       │ id              │       │ name            │
│ scoring_type    │       │ name            │       │ country         │
│ data_source_url │       │ gender          │       └─────────────────┘
└─────────────────┘       │ type            │               ▲
                          └─────────────────┘               │
                                  ▲                         │
                                  │                         │
                          ┌───────┴─────────────────────────┴───┐
                          │              Entry                   │
                          ├─────────────────────────────────────┤
                          │ competition_id                      │
                          │ athlete_id                          │
                          │ score           (raw from source)   │
                          │ source_url      (traceability)      │
                          │ source_date     (when collected)    │
                          └─────────────────────────────────────┘
```

---

## Entity Definitions

### Sport

Defines the scoring system and data source for a category of competitions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID |
| `name` | string | Display name |
| `scoring_type` | enum | How to interpret scores (see below) |
| `data_source_url` | string | Where to get standings |

**Scoring types:**

| Type | Description | Sports |
|------|-------------|--------|
| `wc_points` | World Cup points (higher = better) | Alpine, XC, Biathlon, Freestyle, Jumping, Snowboard |
| `world_ranking` | Rank position (lower = better) | Hockey, Curling |
| `season_best` | Best score this season (higher = better) | Figure Skating |
| `isu_points` | ISU ranking points | Speed Skating, Short Track |

---

### Competition

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID: `{sport}-{gender}-{event}` |
| `sport_id` | string | FK to Sport |
| `name` | string | Official event name |
| `gender` | string | M / F / X |
| `type` | string | individual / team |

---

### Athlete

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID |
| `name` | string | Full name (or team name for team sports) |
| `country` | string | IOC code |

---

### Entry

Links athlete to competition with traceable performance data.

| Field | Type | Description |
|-------|------|-------------|
| `competition_id` | string | FK to Competition |
| `athlete_id` | string | FK to Athlete |
| `score` | number | Raw score from source (interpreted by sport.scoring_type) |
| `source_url` | string | URL where data was collected |
| `source_date` | date | When data was collected |

---

## Score Normalization

Different scoring types are normalized to **relative strength** (0 to 1) for probability calculation.

```python
def normalize_scores(entries, scoring_type):
    """Convert raw scores to relative strength based on scoring type."""
    
    if scoring_type == "wc_points":
        # Higher is better - direct proportion
        total = sum(e.score for e in entries)
        for e in entries:
            e.strength = e.score / total if total > 0 else 1/len(entries)
    
    elif scoring_type == "world_ranking":
        # Lower is better - invert
        for e in entries:
            e.strength = 1 / e.score  # rank 1 → 1.0, rank 10 → 0.1
        total = sum(e.strength for e in entries)
        for e in entries:
            e.strength /= total  # normalize to sum=1
    
    elif scoring_type == "season_best":
        # Higher is better - direct proportion
        total = sum(e.score for e in entries)
        for e in entries:
            e.strength = e.score / total
    
    elif scoring_type == "isu_points":
        # Higher is better - direct proportion
        total = sum(e.score for e in entries)
        for e in entries:
            e.strength = e.score / total
```

---

## Probability Calculation

After normalization, strength becomes probability:

```python
def calculate_probabilities(entries):
    """Strength already normalized to sum=1, so it IS the probability."""
    for e in entries:
        e.p_gold = e.strength
        e.p_silver = e.strength * 0.95  # slight reduction for lower medals
        e.p_bronze = e.strength * 0.90
    
    # Re-normalize silver/bronze
    normalize(entries, 'p_silver')
    normalize(entries, 'p_bronze')
```

---

## File Structure

```
data/
├── sports.json         # Sport definitions with scoring_type
├── competitions.json   # 116 medal events
├── athletes.json       # All top athletes globally
└── entries.json        # Performance data with source tracking

src/
├── normalize.py        # Score → strength by scoring_type
├── probability.py      # Strength → probability
├── simulator.py        # Monte Carlo simulation
└── output.py           # Filter & format

output/
└── predictions.json
```

---

## Sports Reference

| ID | Sport | Scoring Type | Data Source |
|----|-------|--------------|-------------|
| `alpine` | Alpine Skiing | wc_points | fis-ski.com |
| `biathlon` | Biathlon | wc_points | biathlonworld.com |
| `bobsled` | Bobsleigh | world_ranking | ibsf.org |
| `cross-country` | Cross-Country | wc_points | fis-ski.com |
| `curling` | Curling | world_ranking | worldcurling.org |
| `figure-skating` | Figure Skating | season_best | isu.org |
| `freestyle` | Freestyle Skiing | wc_points | fis-ski.com |
| `hockey` | Ice Hockey | world_ranking | iihf.com |
| `luge` | Luge | world_ranking | fil-luge.org |
| `nordic-combined` | Nordic Combined | wc_points | fis-ski.com |
| `short-track` | Short Track | isu_points | isu.org |
| `skeleton` | Skeleton | world_ranking | ibsf.org |
| `ski-jumping` | Ski Jumping | wc_points | fis-ski.com |
| `ski-mountaineering` | Ski Mountaineering | world_ranking | ismf-ski.org |
| `snowboard` | Snowboard | wc_points | fis-ski.com |
| `speed-skating` | Speed Skating | isu_points | isu.org |
