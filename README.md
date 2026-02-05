# 2026 Winter Olympics - Medal Predictions

Monte Carlo simulation to predict medal outcomes at the 2026 Milano-Cortina Winter Olympics using a Plackett-Luce model with temperature scaling.

## Quick Start

```bash
# 1. Install dependencies
pip install streamlit pandas requests beautifulsoup4 lxml

# 2. Run data pipeline (fetches fresh data from APIs)
python run_pipeline.py

# 3. Run predictions
python predict.py

# 4. View results in Streamlit
streamlit run app.py
```

## Project Structure

```
olympic_predictions/
├── app.py                  # Streamlit visualization
├── predict.py              # Monte Carlo prediction engine
├── run_pipeline.py         # Data pipeline orchestrator
├── database.py             # SQLite database setup
├── excluded_athletes.py    # Athletes to exclude (injured/retired)
├── pipelines/
│   ├── import_legacy.py    # Import baseline JSON data
│   ├── isu_speed_skating.py # ISU API for speed skating
│   └── fis_alpine.py       # FIS scraping for alpine
├── data/                   # Baseline athlete data (JSON)
├── db/
│   └── olympics.db         # SQLite database
├── output/
│   ├── predictions.csv     # Country medal totals
│   └── competition_predictions.csv  # Per-event predictions
└── scripts/
    └── parse_fis_data.py   # Legacy data generation
```

## Data Pipeline

The pipeline aggregates data from multiple sources:

| Source | Sports | Method |
|--------|--------|--------|
| **ISU API** | Speed Skating | Official API - event-specific standings |
| **FIS Scraping** | Alpine Skiing | Web scraping - discipline-specific standings |
| **Legacy JSON** | All others | World Cup overall standings |

### Key Improvements
- **Event specialization**: Athletes only compete in their actual events
- **Jordan Stolz fix**: Speed skaters now correctly appear only in their specialized distances
- **Mikaela Shiffrin fix**: Alpine skiers now have discipline-specific scores (SL/GS vs DH/SG)

## Prediction Model

Uses **Plackett-Luce** model with Monte Carlo simulation:

1. **Strength**: Convert WC points to log-strength
2. **Noise**: Add temperature-scaled Gumbel noise (temp=0.3)
3. **Simulate**: Run 10,000 simulations per competition
4. **Aggregate**: Count medals per country

### Sample Results

| Country | Gold | Silver | Bronze | Total |
|---------|------|--------|--------|-------|
| NOR     | 12   | 11     | 10     | 33    |
| SWE     | 6    | 6      | 6      | 18    |
| USA     | 5    | 6      | 6      | 17    |
| GER     | 5    | 5      | 5      | 15    |

## Running

### Full Pipeline
```bash
python run_pipeline.py      # Fetch all data sources
python predict.py           # Run predictions
streamlit run app.py        # View results
```

### Individual Steps
```bash
python run_pipeline.py legacy   # Only import JSON baseline
python run_pipeline.py isu      # Only ISU speed skating
python run_pipeline.py fis      # Only FIS alpine
```

## Streamlit App

The app has three sections:

1. **Datagrunnlag** - Database statistics, entries by source/sport
2. **Prediksjoner** - Medal predictions per country, Nordic focus
3. **Konkurransedetaljer** - Per-competition medal probabilities

## Excluding Athletes

Edit `excluded_athletes.py` to exclude injured/retired athletes:

```python
EXCLUDED_ATHLETES = [
    ("Aleksander Aamodt Kilde", "NOR", "injury"),
    ("Therese Johaug", "NOR", "retired"),
]
```

## Requirements

- Python 3.8+
- streamlit
- pandas
- requests
- beautifulsoup4, lxml

```bash
pip install streamlit pandas requests beautifulsoup4 lxml
```

---

*Predictions for Milano-Cortina 2026 Winter Olympics*
