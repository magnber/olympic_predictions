# Technical Implementation

## Data Model

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   Country   │       │   Competition   │       │    Sport    │
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ id          │       │ id              │       │ id          │
│ code        │       │ name            │       │ name        │
│ name        │       │ sport_id ───────┼──────▶│ federation  │
└─────────────┘       │ gender          │       │ data_source │
       ▲              │ type            │       └─────────────┘
       │              └─────────────────┘
       │                      ▲
       │                      │
       │              ┌───────┴───────┐
       │              │               │
┌──────┴──────┐    ┌──┴───────────────┴──┐
│   Athlete   │    │  CompetitionEntry   │
├─────────────┤    ├─────────────────────┤
│ id          │    │ id                  │
│ name        │    │ competition_id      │
│ country_id ─┼───▶│ athlete_id          │
│ gender      │    │ world_ranking       │
│ sports      │    │ wc_points           │
└─────────────┘    │ p_gold (derived)    │
                   │ p_silver (derived)  │
                   │ p_bronze (derived)  │
                   └─────────────────────┘
```

**Note:** `p_gold`, `p_silver`, `p_bronze` are calculated from `world_ranking` and `wc_points` - they are outputs of the model, not inputs.

---

## Entity Definitions

### Country

Represents a nation. We track only the four Nordic countries.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier, same as IOC code |
| `code` | string | 3-letter IOC country code |
| `name` | string | Full country name for display |

```json
{
    "id": "NOR",
    "code": "NOR",
    "name": "Norway"
}
```

**Target countries:** `NOR`, `SWE`, `FIN`, `DEN`

---

### Sport

Represents an Olympic sport discipline. Used to group competitions and identify data sources.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier, kebab-case |
| `name` | string | Official sport name |
| `federation` | string | Governing body (FIS, IBU, ISU, IIHF, WCF, IBSF, FIL, ISMF) |
| `data_source` | string | URL for fetching rankings/results |

```json
{
    "id": "cross-country",
    "name": "Cross-Country Skiing",
    "federation": "FIS",
    "data_source": "fis-ski.com"
}
```

---

### Competition

Represents a single medal event. Each awards one set of medals (gold, silver, bronze).

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier: `{sport}-{gender}-{event}` |
| `name` | string | Official event name |
| `sport_id` | string | Foreign key to Sport |
| `gender` | enum | `"M"` (men), `"F"` (women), `"X"` (mixed) |
| `type` | enum | `"individual"` or `"team"` |

```json
{
    "id": "cc-m-50km-mass",
    "name": "Men's 50km Mass Start",
    "sport_id": "cross-country",
    "gender": "M",
    "type": "individual"
}
```

---

### Athlete

Represents an individual athlete or a team (for hockey/curling).

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier: `{lastname}-{firstname}` or `{country}-{sport}-team` |
| `name` | string | Full name or team name |
| `country_id` | string | Foreign key to Country (IOC code) |
| `gender` | enum | `"M"`, `"F"`, `"X"` (mixed team) |
| `sports` | array | List of sport IDs the athlete competes in |

```json
{
    "id": "klaebo-johannes",
    "name": "Johannes Høsflot Klæbo",
    "country_id": "NOR",
    "gender": "M",
    "sports": ["cross-country"]
}
```

---

### CompetitionEntry

Links athletes to competitions. Contains both collected facts and derived probabilities.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `id` | string | generated | Format: `{competition_id}-{athlete_id}` |
| `competition_id` | string | input | Foreign key to Competition |
| `athlete_id` | string | input | Foreign key to Athlete |
| `world_ranking` | int | **collected** | Current ranking from federation |
| `wc_points` | int | **collected** | World Cup points this season |
| `p_gold` | float | **calculated** | Probability of gold (0.0-1.0) |
| `p_silver` | float | **calculated** | Probability of silver (0.0-1.0) |
| `p_bronze` | float | **calculated** | Probability of bronze (0.0-1.0) |

```json
{
    "id": "cc-m-50km-mass-klaebo-johannes",
    "competition_id": "cc-m-50km-mass",
    "athlete_id": "klaebo-johannes",
    "world_ranking": 1,
    "wc_points": 1250,
    "p_gold": null,
    "p_silver": null,
    "p_bronze": null
}
```

**Note:** Probabilities start as `null` and are calculated after all data is collected.

---

## File Structure

```
olympic_predictions/
├── STRATEGY.md
├── TECHNICAL.md
├── WORKING_NOTES.md
│
├── data/
│   ├── countries.json    # 4 Nordic countries
│   ├── sports.json       # 16 sports with federation info
│   ├── competitions.json # 116 medal events
│   ├── athletes.json     # Nordic athletes + field entries
│   └── entries.json      # Competition entries with rankings/points
│
├── src/
│   ├── models.py         # Data classes
│   ├── loader.py         # Load JSON data
│   ├── probability.py    # Calculate probabilities from points/rankings
│   ├── calculator.py     # Expected value calculations
│   ├── simulator.py      # Monte Carlo simulation
│   └── output.py         # Format final predictions
│
└── output/
    └── predictions.md
```

---

## Sports Reference (2026 Milan-Cortina)

| ID | Sport | Federation | Events |
|----|-------|------------|--------|
| `alpine` | Alpine Skiing | FIS | 11 |
| `biathlon` | Biathlon | IBU | 11 |
| `bobsled` | Bobsleigh | IBSF | 4 |
| `cross-country` | Cross-Country Skiing | FIS | 12 |
| `curling` | Curling | WCF | 3 |
| `figure-skating` | Figure Skating | ISU | 5 |
| `freestyle` | Freestyle Skiing | FIS | 13 |
| `hockey` | Ice Hockey | IIHF | 2 |
| `luge` | Luge | FIL | 5 |
| `nordic-combined` | Nordic Combined | FIS | 3 |
| `short-track` | Short Track Speed Skating | ISU | 9 |
| `skeleton` | Skeleton | IBSF | 3 |
| `ski-jumping` | Ski Jumping | FIS | 5 |
| `ski-mountaineering` | Ski Mountaineering | ISMF | 3 |
| `snowboard` | Snowboard | FIS | 11 |
| `speed-skating` | Speed Skating | ISU | 14 |

**Total: 116 medal events**

---

## Calculation Logic

### Step 1: Calculate Probabilities

After collecting all entries with `wc_points`:

```python
def calculate_probabilities(entries_for_competition):
    total_points = sum(e.wc_points for e in entries_for_competition)
    
    for entry in entries_for_competition:
        if total_points > 0:
            entry.p_gold = entry.wc_points / total_points
        else:
            # Equal probability if no points data
            entry.p_gold = 1 / len(entries_for_competition)
        
        # Silver/bronze slightly lower correlation with ranking
        entry.p_silver = entry.p_gold * 0.9  # simplified
        entry.p_bronze = entry.p_gold * 0.8  # simplified
    
    # Normalize so probabilities sum to 1
    normalize(entries_for_competition)
```

### Step 2: Expected Medals Per Country

```python
def calculate_expected_medals(country_id, entries):
    expected = {"gold": 0, "silver": 0, "bronze": 0}
    
    for entry in entries:
        if get_athlete_country(entry.athlete_id) == country_id:
            expected["gold"] += entry.p_gold
            expected["silver"] += entry.p_silver
            expected["bronze"] += entry.p_bronze
    
    return expected
```

### Step 3: Monte Carlo Simulation

```python
def simulate_olympics(entries, competitions, n_simulations=10000):
    results = []
    
    for _ in range(n_simulations):
        medals = {c: {"gold": 0, "silver": 0, "bronze": 0} 
                  for c in ["NOR", "SWE", "FIN", "DEN"]}
        
        for comp in competitions:
            comp_entries = get_entries_for_competition(comp.id, entries)
            
            gold_winner = weighted_random_choice(comp_entries, "p_gold")
            silver_winner = weighted_random_choice(comp_entries, "p_silver")
            bronze_winner = weighted_random_choice(comp_entries, "p_bronze")
            
            for winner, medal in [(gold_winner, "gold"), 
                                   (silver_winner, "silver"), 
                                   (bronze_winner, "bronze")]:
                country = get_athlete_country(winner.athlete_id)
                if country in medals:
                    medals[country][medal] += 1
        
        results.append(medals)
    
    return calculate_percentiles(results)
```

---

## Output Format

```python
def format_prediction(expected_medals):
    output = ""
    for country in ["Denmark", "Norway", "Sweden", "Finland"]:
        code = {"Denmark": "DEN", "Norway": "NOR", 
                "Sweden": "SWE", "Finland": "FIN"}[country]
        m = expected_medals[code]
        output += f"{country}:\n"
        output += f"🥇 Gold – {round(m['gold'])}\n"
        output += f"🥈 Silver – {round(m['silver'])}\n"
        output += f"🥉 Bronze – {round(m['bronze'])}\n\n"
    return output
```
