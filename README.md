# 2026 Winter Olympics - Nordic Medal Predictions

Monte Carlo simulation models to predict medal outcomes for Nordic countries (Norway, Sweden, Finland, Denmark) at the 2026 Milano-Cortina Winter Olympics.

## Quick Start

```bash
# 1. Clone and setup
cd olympic_predictions
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit pandas

# 2. Generate athlete data
python3 scripts/parse_fis_data.py

# 3. Run predictions (V3 recommended)
python3 prediction/v3/predict.py

# 4. View results in Streamlit
streamlit run app.py
```

## Project Structure

```
olympic_predictions/
├── data/                    # Athlete and competition data (JSON)
│   ├── athletes.json        # Individual athletes + team entries
│   ├── competitions.json    # All 116 Olympic events
│   ├── entries.json         # Athlete scores per competition
│   └── sports.json          # Sport metadata
├── prediction/
│   ├── v1/predict.py        # Plackett-Luce model
│   ├── v2/predict.py        # Bradley-Terry model
│   └── v3/predict.py        # Plackett-Luce + Variance Propagation (recommended)
├── output/                  # Prediction results (CSV)
├── scripts/
│   └── parse_fis_data.py    # Data generation from WC standings
├── app.py                   # Streamlit visualization
├── DATA_FOUNDATION_REPORT.md
└── README.md
```

## Prediction Models

### Model Comparison

| Model | Methodology | Norway | Sweden | Finland | Denmark |
|-------|-------------|--------|--------|---------|---------|
| **V1** | Plackett-Luce + Gumbel noise | 33 | 15 | 6 | 0 |
| **V2** | Bradley-Terry + position weights | 31 | 18 | 6 | 0 |
| **V3** | Plackett-Luce + Variance Propagation | **39** | **21** | **9** | 0 |

### Recommended: V3 Model

V3 is recommended because it:
- Models strength uncertainty (15% CV)
- Creates realistic correlated errors across events
- Based on academic literature (FiveThirtyEight methodology)

### V3 Detailed Predictions

| Country | Gold | Silver | Bronze | Total | 95% CI |
|---------|------|--------|--------|-------|--------|
| **Norway** | 13 | 13 | 13 | **39** | 28-47 |
| **Sweden** | 7 | 7 | 7 | **21** | 13-27 |
| **Finland** | 3 | 3 | 3 | **9** | 4-14 |
| **Denmark** | 0 | 0 | 0 | **0** | 0-1 |

## Data Foundation

### Coverage
- **99/116 events** (85%) have athlete data
- **1,775 entries** across 623 individual athletes + 20 team entries
- Data sourced from 2025-26 World Cup standings

### Selection Criteria
- Top ~30 athletes per sport/gender from World Cup overall standings
- Same athletes mapped to all events in their category
- Team events use aggregated nation-level strength

### Excluded Athletes
Athletes can be excluded in `scripts/parse_fis_data.py`:
```python
EXCLUDED_ATHLETES = {
    ("Aleksander Aamodt Kilde", "NOR"),  # Injury
}
```

## Running Predictions

### Generate Data
```bash
python3 scripts/parse_fis_data.py
```
Output: Updates `data/athletes.json` and `data/entries.json`

### Run V3 Model (Recommended)
```bash
python3 prediction/v3/predict.py
```
Output: 
- `output/v3_predictions.csv` - Country medal totals
- `output/v3_competition_predictions.csv` - Per-event predictions

### Run All Models
```bash
python3 prediction/v1/predict.py
python3 prediction/v2/predict.py
python3 prediction/v3/predict.py
```

### View in Streamlit
```bash
streamlit run app.py
```
Opens browser at `http://localhost:8501`

## Model Details

### V1: Plackett-Luce
- Converts WC points to strength
- Adds Gumbel noise for randomness
- Simulates 100,000 competitions

### V2: Bradley-Terry
- Position-weighted probabilities
- Gold favors top athletes more (power=1.5)
- Bronze is more "random" (power=1.0)

### V3: Variance Propagation
- Samples athlete strength uncertainty per simulation
- Same multiplier affects athlete across all their events
- Models correlated prediction errors (realistic)

## Known Limitations

1. **No event specialization** - Sprinters appear in distance events
2. **Same score all events** - Uses overall WC points, not event-specific
3. **Top 30 cutoff** - May miss surprise medalists ranked 31+
4. **17 events missing** - Ski Mountaineering, Figure Skating pairs, etc.

## Files

| File | Description |
|------|-------------|
| `DATA_FOUNDATION_REPORT.md` | Detailed analysis of data quality |
| `montecarlo_v3.md` | V3 model methodology documentation |
| `STRATEGY.md` | Project strategy notes |

## Requirements

- Python 3.8+
- streamlit
- pandas

```bash
pip install streamlit pandas
```

---

*Predictions generated February 2026 for Milano-Cortina 2026 Winter Olympics*
