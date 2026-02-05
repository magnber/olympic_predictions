# Working Notes

## Tasks

### 1. Data Model Setup
- [ ] Create `data/competitions.json` (116 events)
- [ ] Create `data/athletes.json` (all top athletes)
- [ ] Create `data/entries.json` (performance data)

### 2. Data Gathering
- [ ] List all 116 competitions
- [ ] For each competition, get top 30 athletes from World Cup standings
- [ ] Record wc_points and world_ranking for each

### 3. Prediction
- [ ] Implement probability calculation
- [ ] Implement Monte Carlo simulation
- [ ] Generate full results dataset

### 4. Output
- [ ] Filter to Nordic countries
- [ ] Format final prediction

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
