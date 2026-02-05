# Nordic Olympic Medal Prediction Strategy

## Challenge

Predict medal counts (Gold, Silver, Bronze) for Denmark, Norway, Sweden, and Finland in the 2026 Winter Olympics (Milan-Cortina).

---

## Approach Overview

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. Collect  │───▶│  2. Calculate│───▶│  3. Aggregate│───▶│  4. Generate │
│  Facts       │    │  Probability │    │  by Country  │    │  Prediction  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
   DATA FOUNDATION       MODELING           ANALYSIS           OUTPUT
```

---

## Phase 1: Data Foundation (Facts)

Collect objective data - no filtering or assumptions about medal chances.

### 1.1 Competitions
- List all 116 medal events
- Record: name, sport, gender, type (individual/team)

### 1.2 Athletes
- Gather all Nordic athletes (NOR, SWE, FIN, DEN) from World Cup standings
- Record: name, country, sport(s)
- Include team entries for hockey, curling, relays

### 1.3 Rankings & Points
- Collect current World Cup points for each athlete
- Collect current world rankings
- Source from federation websites (FIS, IBU, ISU, IIHF, WCF, etc.)

### Data Sources

| Federation | Sports | Source |
|------------|--------|--------|
| FIS | Alpine, Cross-country, Freestyle, Nordic Combined, Ski Jumping, Snowboard | fis-ski.com |
| IBU | Biathlon | biathlonworld.com |
| ISU | Figure Skating, Short Track, Speed Skating | isu.org |
| IIHF | Ice Hockey | iihf.com |
| WCF | Curling | worldcurling.org |
| IBSF | Bobsleigh, Skeleton | ibsf.org |
| FIL | Luge | fil-luge.org |
| ISMF | Ski Mountaineering | ismf-ski.org |

---

## Phase 2: Probability Modeling (Derived)

Calculate medal probabilities from the collected data.

### Individual Events

Convert World Cup performance to probability:
```
P(medal) = f(athlete_wc_points, field_wc_points)
```

Primary method:
```
P(gold) ≈ athlete_points / sum(top_30_points)
```

### Team Events

For relays, hockey, curling:
- Use team-level world rankings
- Convert ranking to probability based on historical medal distribution by rank

### Field Entry

For each competition, create a "field" entry representing all non-Nordic competitors:
```
P(field_gold) = 1 - Σ P(nordic_athlete_gold)
```

---

## Phase 3: Aggregation (Analysis)

### Per-Event Expected Medals

For each country, sum probabilities across their athletes:
```
E[gold|country|event] = Σ P(gold) for all country's athletes in event
```

### Country Totals

Sum across all 116 events:
```
E[gold|country] = Σ E[gold|country|event]
```

### Confidence Intervals

Monte Carlo simulation (10,000 runs) to understand variance:
- Simulate each event outcome based on probabilities
- Count medals per country per simulation
- Calculate percentiles (10th, 50th, 90th)

---

## Phase 4: Output

Generate final predictions:
```
Country:
🥇 Gold – X
🥈 Silver – Y
🥉 Bronze – Z
```

Round expected values to integers for submission.

---

## Key Principle

**Data first, conclusions second.**

- Do NOT pre-filter events based on assumed Nordic strength
- Do NOT assign "relevance" labels before seeing the data
- Let World Cup standings reveal where Nordic countries have chances
- The model output tells us which sports matter, not our assumptions
