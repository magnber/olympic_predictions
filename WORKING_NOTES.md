# Working Notes

## Tasks

### 1. Data Model Setup
- [x] Create `data/sports.json` (16 sports with scoring_type + data sources)
- [x] Create `data/competitions.json` (116 events)
- [x] Create `data/athletes.json` (625 athletes, 155 Nordic)
- [x] Create `data/entries.json` (1669 entries with scores)

### 2. Data Gathering
- [x] List all 116 competitions (verified from Wikipedia + IOC ODF)
- [x] Cross-country skiing - Men + Women (30 each, FIS data)
- [x] Biathlon - Men + Women (30 each, IBU data)
- [x] Alpine skiing - Men + Women (30 each, FIS data)
- [x] Ski jumping - Men + Women (30 each, FIS data)
- [x] Speed skating - Men + Women (30 each, ISU data)
- [x] Freestyle skiing - Moguls, Aerials, Ski Cross, Halfpipe, Slopestyle (FIS data)
- [x] Snowboard - Halfpipe, Slopestyle, Cross, PGS (FIS data)
- [x] Short track speed skating - Men + Women (ISU data)
- [x] Nordic combined - Men + Women (FIS data)
- [x] Figure skating - Men + Women (ISU data)
- [x] Luge - Men + Women (FIL data)
- [x] Bobsled - Men + Women (IBSF data)
- [x] Skeleton - Men + Women (IBSF data)
- [x] Curling - Men + Women (WCF data)
- [x] Ice Hockey - Men + Women (IIHF data)

### 3. Prediction
- [x] Implement probability calculation (normalize scores → probabilities)
- [x] Implement Monte Carlo simulation (10,000 runs)
- [x] Generate results dataset → prediction/v1/output.csv

### 4. Output
- [x] Filter to Nordic countries
- [x] Format final prediction with 95% confidence intervals

## V1 Results (86/116 competitions covered)

| Country | Gold | Silver | Bronze | Total |
|---------|------|--------|--------|-------|
| Norway  | 11   | 11     | 11     | 33    |
| Sweden  | 5    | 5      | 5      | 16    |
| Finland | 2    | 2      | 2      | 5     |
| Denmark | 0    | 0      | 0      | 0     |

**Data:** 625 athletes, 1669 entries across 86 events (74% coverage).

---

## Data Sources

| Sport | Federation | URL |
|-------|------------|-----|
| Alpine, XC, Freestyle, Jumping, Snowboard | FIS | fis-ski.com |
| Biathlon | IBU | biathlonworld.com |
| Speed Skating, Short Track, Figure Skating | ISU | isu.org |
| Ice Hockey | IIHF | iihf.com |
| Curling | WCF | worldcurling.org |
| Bobsled, Skeleton | IBSF | ibsf.org |
| Luge | FIL | fil-luge.org |
