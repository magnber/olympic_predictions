# Olympic Medal Prediction Strategy

## Goal

Predict medal counts for Denmark, Norway, Sweden, and Finland in the 2026 Winter Olympics.

---

## Approach

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. DEFINE  │───▶│  2. GATHER  │───▶│  3. PREDICT │───▶│  4. FILTER  │
│  Data Model │    │  All Data   │    │  All Medals │    │  Nordic     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**Key insight:** To predict Nordic medals accurately, we need performance data on ALL top athletes globally, not just Nordic ones. Then filter results.

---

## Phase 1: Define Data Model

### Core Entities

**Competition** - An event where medals are awarded
- id, name, sport, gender, type

**Athlete** - Someone who can win a medal
- id, name, country

**Entry** - An athlete's participation in a competition with performance data
- competition_id, athlete_id, wc_points, world_ranking

---

## Phase 2: Gather Data

For each competition:
1. Get World Cup standings (top 30 athletes globally)
2. Record each athlete's points and ranking
3. This gives us the full competitive field

**Data sources:** FIS, IBU, ISU, IIHF, WCF (federation websites)

---

## Phase 3: Predict Medals

Convert performance data to probabilities:

```
P(gold) = athlete_wc_points / sum(all_wc_points)
```

Run Monte Carlo simulation:
1. For each competition, randomly select winners based on probabilities
2. Repeat 10,000 times
3. Output: medal distribution across all athletes

---

## Phase 4: Filter to Nordic

From the full prediction results, filter to:
- `country IN ('NOR', 'SWE', 'FIN', 'DEN')`

Sum expected medals by country.

---

## Output

```
Denmark:
🥇 Gold – X    🥈 Silver – Y    🥉 Bronze – Z

Norway:
🥇 Gold – X    🥈 Silver – Y    🥉 Bronze – Z

Sweden:
🥇 Gold – X    🥈 Silver – Y    🥉 Bronze – Z

Finland:
🥇 Gold – X    🥈 Silver – Y    🥉 Bronze – Z
```
