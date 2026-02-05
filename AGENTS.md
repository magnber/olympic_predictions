# Olympic Medal Prediction

## Goal

Predict Nordic medal counts (DEN, NOR, SWE, FIN) for 2026 Winter Olympics.

---

## Approach

```
DEFINE → GATHER → PREDICT → FILTER
```

1. **Define** - Competition (event), Athlete (competitor), Entry (performance data)
2. **Gather** - Top 30 athletes per competition globally (not just Nordic)
3. **Predict** - Monte Carlo simulation based on World Cup points
4. **Filter** - Extract Nordic countries from results

---

## Data Model

| Entity | Key Fields |
|--------|------------|
| **Competition** | id, name, sport, gender, type |
| **Athlete** | id, name, country |
| **Entry** | competition_id, athlete_id, wc_points, world_ranking |

---

## Prediction Method

```
P(gold) = athlete_wc_points / total_wc_points
```

Run 10,000 simulations → aggregate → filter to Nordic.

---

## Documents

| File | Purpose |
|------|---------|
| [STRATEGY.md](./STRATEGY.md) | High-level approach |
| [TECHNICAL.md](./TECHNICAL.md) | Data model & code |
| [WORKING_NOTES.md](./WORKING_NOTES.md) | Task tracking |
