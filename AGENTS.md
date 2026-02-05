# Olympic Medal Prediction - Agent Guide

## Goal

Predict medal counts (Gold, Silver, Bronze) for **Denmark, Norway, Sweden, Finland** in the 2026 Winter Olympics.

**Deadline:** February 6, 2026

---

## Workflow

```
COLLECT FACTS → CALCULATE PROBABILITIES → AGGREGATE → OUTPUT
```

1. **Collect** - All 116 events, Nordic athletes, World Cup rankings/points
2. **Calculate** - Convert WC points to medal probabilities
3. **Aggregate** - Sum probabilities by country
4. **Output** - Generate prediction in required format

---

## Key Principle

**Data first, conclusions second.**

- Collect data for ALL sports and ALL Nordic countries
- Do NOT pre-filter based on assumed strengths
- Let the World Cup standings reveal medal chances

---

## Data Model (5 Entities)

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| **Country** | Nordic nations | id, name |
| **Sport** | 16 Olympic sports | id, federation, data_source |
| **Competition** | 116 medal events | id, name, sport_id, gender, type |
| **Athlete** | Nordic athletes + teams | id, name, country_id, sports |
| **CompetitionEntry** | Links athlete↔competition | athlete_id, competition_id, wc_points, world_ranking, p_gold* |

*Probabilities are **calculated** from wc_points, not manually assigned.

---

## Data Files

```
data/
├── countries.json    # 4 records
├── sports.json       # 16 records
├── competitions.json # 116 records
├── athletes.json     # ~100-150 records
└── entries.json      # ~300-500 records
```

---

## Output Format

```
Denmark:
🥇 Gold – X
🥈 Silver – Y
🥉 Bronze – Z

Norway:
🥇 Gold – X
🥈 Silver – Y
🥉 Bronze – Z

Sweden:
🥇 Gold – X
🥈 Silver – Y
🥉 Bronze – Z

Finland:
🥇 Gold – X
🥈 Silver – Y
🥉 Bronze – Z
```

---

## Reference Documents

| Document | Purpose |
|----------|---------|
| [STRATEGY.md](./STRATEGY.md) | Approach, phases, calculation methods |
| [TECHNICAL.md](./TECHNICAL.md) | Data model, entity definitions, code logic |
| [WORKING_NOTES.md](./WORKING_NOTES.md) | Task checklist, progress tracking |

---

## Current Phase

See `WORKING_NOTES.md` for current progress and next tasks.
