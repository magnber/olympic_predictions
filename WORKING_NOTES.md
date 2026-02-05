# Working Notes

## Tasks

### 1. Data Model Setup
- [x] Create `data/sports.json` (16 sports with scoring_type + data sources)
- [x] Create `data/competitions.json` (116 events)
- [x] Create `data/athletes.json` (300 athletes, 110 Nordic)
- [x] Create `data/entries.json` (1200 entries with scores)

### 2. Data Gathering
- [x] List all 116 competitions (verified from Wikipedia + IOC ODF)
- [x] Cross-country skiing - Men + Women (30 each, FIS data)
- [x] Biathlon - Men + Women (30 each, IBU data)
- [x] Alpine skiing - Men + Women (30 each, FIS data)
- [x] Ski jumping - Men + Women (30 each, FIS data)
- [x] Speed skating - Men + Women (30 each, ISU data)
- [ ] Freestyle skiing - pending
- [ ] Snowboard - pending
- [ ] Other sports (hockey, curling, luge, bobsled, etc.) - pending

### 3. Prediction
- [x] Implement probability calculation (normalize scores → probabilities)
- [x] Implement Monte Carlo simulation (10,000 runs)
- [x] Generate results dataset → prediction/v1/output.csv

### 4. Output
- [x] Filter to Nordic countries
- [x] Format final prediction with 95% confidence intervals

## V1 Results (40/116 competitions covered)

| Country | Gold | Silver | Bronze | Total |
|---------|------|--------|--------|-------|
| Norway  | 8    | 8      | 8      | 24    |
| Sweden  | 3    | 3      | 3      | 9     |
| Finland | 1    | 1      | 1      | 4     |
| Denmark | 0    | 0      | 0      | 0     |

**Note:** Only 40 of 116 competitions have athlete data. More data needed for accuracy.

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
