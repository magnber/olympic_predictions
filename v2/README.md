# V2 Data Pipeline

Forbedret prediksjonssystem med SQLite database og API-integrasjon.

## Datakilder

| Kilde | Sport | Type |
|-------|-------|------|
| **ISU API** | Skøyter | Event-spesifikke WC-resultater |
| **Legacy JSON** | Alt annet | Overall WC-standings |

### ISU Speed Skating
Aggregerer World Cup-resultater per distanse (500m, 1000m, 1500m, etc.) fra `api.isuresults.eu`. Løser problemet med at sprintere ble plassert i distanseøvelser.

### Legacy Data
Importerer eksisterende data fra `data/*.json` (overall WC-standings).

---

## Datamodell

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  athletes   │────▶│   entries    │◀────│ competitions│
├─────────────┤     ├──────────────┤     ├─────────────┤
│ id          │     │ athlete_id   │     │ id          │
│ name        │     │ competition_id│    │ sport_id    │
│ country_code│     │ score        │     │ name        │
└─────────────┘     │ source       │     │ gender      │
                    └──────────────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │excluded_     │
                    │athletes      │
                    ├──────────────┤
                    │ athlete_id   │
                    │ reason       │
                    └──────────────┘
```

**Score** = WC-poeng (akkumulert over sesongen)
- ISU: Poeng per distanse (1.plass=100, 2.plass=80, ...)
- Legacy: Overall WC-poeng

---

## Beregning

### Plackett-Luce Monte Carlo

For hver av 10,000 simuleringer:

```
For hver konkurranse:
  1. Hent alle entries (utøver + score)
  2. Beregn styrke: log(score)
  3. Legg til støy: styrke + Gumbel(0, σ·T)
  4. Ranger etter støy-justert styrke
  5. Tildel gull/sølv/bronse til topp 3
  
Summer medaljer per land
```

**Parametre:**
- `TEMPERATURE = 0.3` - Skalerer støy (lavere = mer deterministisk)
- `NUM_SIMULATIONS = 10,000`

---

## Kjøring

```bash
# Full pipeline (legacy + ISU API)
python v2/run_pipeline.py

# Kun prediksjon (krever at DB finnes)
python v2/predict.py

# Vis ekskluderte utøvere
python v2/excluded_athletes.py
```

---

## Output

```
v2/output/
├── v2_predictions.csv              # Medaljer per land
└── v2_competition_predictions.csv  # Sannsynlighet per utøver/konkurranse
```

---

## Forbedringer vs V1

| Problem | V1 | V2 |
|---------|----|----|
| Stolz i 10000m | ✗ Feil | ✓ Riktig (kun 500m, 1000m, 1500m) |
| USA medaljer | 43 (overestimert) | 34 (realistisk) |
| Datakilde | Kun manual | API + manual |
