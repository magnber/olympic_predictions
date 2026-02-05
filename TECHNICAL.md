# Technical Implementation

## Data Model

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Competition   │       │      Entry      │       │     Athlete     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id              │◄──────│ competition_id  │       │ id              │
│ name            │       │ athlete_id      │──────▶│ name            │
│ sport           │       │ wc_points       │       │ country         │
│ gender          │       │ world_ranking   │       └─────────────────┘
│ type            │       └─────────────────┘
└─────────────────┘
```

---

## Entity Definitions

### Competition

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID: `{sport}-{gender}-{event}` |
| `name` | string | Official event name |
| `sport` | string | Sport category |
| `gender` | string | M / F / X (mixed) |
| `type` | string | individual / team |

### Athlete

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID |
| `name` | string | Full name |
| `country` | string | IOC country code (e.g., NOR, USA, GER) |

### Entry

| Field | Type | Description |
|-------|------|-------------|
| `competition_id` | string | FK to Competition |
| `athlete_id` | string | FK to Athlete |
| `wc_points` | int | World Cup points this season |
| `world_ranking` | int | Current world ranking |

---

## File Structure

```
data/
├── competitions.json   # 116 medal events
├── athletes.json       # All top athletes globally
└── entries.json        # Performance data per athlete per competition

src/
├── probability.py      # Convert wc_points to P(medal)
├── simulator.py        # Monte Carlo simulation
└── output.py           # Filter & format results

output/
└── predictions.json    # Full results, filterable
```

---

## Calculation

### Probability from WC Points

```python
def calculate_probabilities(entries):
    total = sum(e.wc_points for e in entries)
    for e in entries:
        e.p_gold = e.wc_points / total if total > 0 else 1/len(entries)
```

### Monte Carlo Simulation

```python
def simulate(competitions, entries, n=10000):
    results = []
    for _ in range(n):
        medals = {}
        for comp in competitions:
            comp_entries = get_entries(comp.id)
            gold = weighted_choice(comp_entries, 'p_gold')
            silver = weighted_choice(comp_entries, 'p_silver')
            bronze = weighted_choice(comp_entries, 'p_bronze')
            
            for athlete, medal in [(gold, 'gold'), (silver, 'silver'), (bronze, 'bronze')]:
                medals[athlete.country] = medals.get(athlete.country, {})
                medals[athlete.country][medal] = medals[athlete.country].get(medal, 0) + 1
        results.append(medals)
    return aggregate(results)
```

### Filter to Nordic

```python
def get_nordic_prediction(results):
    nordic = ['NOR', 'SWE', 'FIN', 'DEN']
    return {c: results[c] for c in nordic if c in results}
```
