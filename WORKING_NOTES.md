# Working Notes - Data Foundation

**Focus:** Gather and structure data according to the schema defined in TECHNICAL.md

**Deadline:** February 6, 2026

---

## Task Overview

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  1. Create   │──▶│  2. Populate │──▶│  3. Populate │──▶│  4. Populate │──▶│  5. Create   │
│  Static Data │   │  Competitions│   │  Athletes    │   │  Rankings    │   │  Entries     │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
     countries         116 events       Nordic athletes   WC points/rank     Link + probs
     sports                             + teams
```

---

## Task 1: Create Static Data Files

These are fixed datasets that don't require external data gathering.

### 1.1 Create `data/countries.json`
- [ ] Create file with 4 Nordic countries
- [ ] Fields: `id`, `code`, `name`
- [ ] Values: NOR, SWE, FIN, DEN

### 1.2 Create `data/sports.json`
- [ ] Create file with 16 sports
- [ ] Fields: `id`, `name`, `federation`, `data_source`, `nordic_relevance`
- [ ] Include data source URLs for each federation

**Sports to include:**
| id | federation | data_source |
|----|------------|-------------|
| `alpine` | FIS | fis-ski.com |
| `biathlon` | IBU | biathlonworld.com |
| `bobsled` | IBSF | ibsf.org |
| `cross-country` | FIS | fis-ski.com |
| `curling` | WCF | worldcurling.org |
| `figure-skating` | ISU | isu.org |
| `freestyle` | FIS | fis-ski.com |
| `hockey` | IIHF | iihf.com |
| `luge` | FIL | fil-luge.org |
| `nordic-combined` | FIS | fis-ski.com |
| `short-track` | ISU | isu.org |
| `skeleton` | IBSF | ibsf.org |
| `ski-jumping` | FIS | fis-ski.com |
| `ski-mountaineering` | ISMF | ismf-ski.org |
| `snowboard` | FIS | fis-ski.com |
| `speed-skating` | ISU | isu.org |

---

## Task 2: Populate Competitions (116 events)

List every medal event with correct metadata. No filtering or prioritization - collect all events.

### 2.1 Competition Data Required

For each event, record:
- `id`: unique identifier
- `name`: official event name
- `sport_id`: link to sport
- `gender`: M/F/X
- `type`: individual/team

### 2.2 Events by Sport

#### Alpine Skiing (11 events)
- [ ] Men's Downhill
- [ ] Men's Super-G
- [ ] Men's Giant Slalom
- [ ] Men's Slalom
- [ ] Men's Combined
- [ ] Women's Downhill
- [ ] Women's Super-G
- [ ] Women's Giant Slalom
- [ ] Women's Slalom
- [ ] Women's Combined
- [ ] Team Combined (new)

#### Biathlon (11 events)
- [ ] Men's 10km Sprint
- [ ] Men's 20km Individual
- [ ] Men's 12.5km Pursuit
- [ ] Men's 15km Mass Start
- [ ] Men's 4x7.5km Relay
- [ ] Women's 7.5km Sprint
- [ ] Women's 15km Individual
- [ ] Women's 10km Pursuit
- [ ] Women's 12.5km Mass Start
- [ ] Women's 4x6km Relay
- [ ] Mixed Relay

#### Bobsleigh (4 events)
- [ ] Two-Man
- [ ] Four-Man
- [ ] Two-Woman
- [ ] Women's Monobob

#### Cross-Country Skiing (12 events)
- [ ] Men's Sprint
- [ ] Men's Team Sprint
- [ ] Men's 10km (Skiathlon)
- [ ] Men's 15km
- [ ] Men's 50km Mass Start
- [ ] Men's 4x10km Relay
- [ ] Women's Sprint
- [ ] Women's Team Sprint
- [ ] Women's 7.5km (Skiathlon)
- [ ] Women's 10km
- [ ] Women's 30km Mass Start
- [ ] Women's 4x5km Relay

#### Curling (3 events)
- [ ] Men's
- [ ] Women's
- [ ] Mixed Doubles

#### Figure Skating (5 events)
- [ ] Men's Singles
- [ ] Women's Singles
- [ ] Pairs
- [ ] Ice Dance
- [ ] Team Event

#### Freestyle Skiing (13 events)
- [ ] Men's Moguls
- [ ] Men's Dual Moguls (new)
- [ ] Men's Aerials
- [ ] Men's Ski Cross
- [ ] Men's Halfpipe
- [ ] Men's Slopestyle
- [ ] Men's Big Air
- [ ] Women's Moguls
- [ ] Women's Dual Moguls (new)
- [ ] Women's Aerials
- [ ] Women's Ski Cross
- [ ] Women's Halfpipe
- [ ] Women's Slopestyle
- [ ] Mixed Aerials (verify)

#### Ice Hockey (2 events)
- [ ] Men's Tournament
- [ ] Women's Tournament

#### Luge (5 events)
- [ ] Men's Singles
- [ ] Women's Singles
- [ ] Men's Doubles
- [ ] Women's Doubles (new)
- [ ] Team Relay

#### Nordic Combined (3 events)
- [ ] Individual Normal Hill
- [ ] Individual Large Hill
- [ ] Team Sprint

#### Short Track Speed Skating (9 events)
- [ ] Men's 500m
- [ ] Men's 1000m
- [ ] Men's 1500m
- [ ] Men's 5000m Relay
- [ ] Women's 500m
- [ ] Women's 1000m
- [ ] Women's 1500m
- [ ] Women's 3000m Relay
- [ ] Mixed Team Relay

#### Skeleton (3 events)
- [ ] Men's
- [ ] Women's
- [ ] Mixed Team (new)

#### Ski Jumping (5 events)
- [ ] Men's Normal Hill
- [ ] Men's Large Hill
- [ ] Men's Team
- [ ] Women's Normal Hill
- [ ] Women's Large Hill (new)

#### Ski Mountaineering (3 events)
- [ ] Men's Sprint
- [ ] Women's Sprint
- [ ] Mixed Relay

#### Snowboard (11 events)
- [ ] Men's Parallel Giant Slalom
- [ ] Men's Snowboard Cross
- [ ] Men's Halfpipe
- [ ] Men's Slopestyle
- [ ] Men's Big Air
- [ ] Women's Parallel Giant Slalom
- [ ] Women's Snowboard Cross
- [ ] Women's Halfpipe
- [ ] Women's Slopestyle
- [ ] Women's Big Air
- [ ] Mixed Team Snowboard Cross

#### Speed Skating (14 events)
- [ ] Men's 500m
- [ ] Men's 1000m
- [ ] Men's 1500m
- [ ] Men's 5000m
- [ ] Men's 10000m
- [ ] Men's Mass Start
- [ ] Men's Team Pursuit
- [ ] Women's 500m
- [ ] Women's 1000m
- [ ] Women's 1500m
- [ ] Women's 3000m
- [ ] Women's 5000m
- [ ] Women's Mass Start
- [ ] Women's Team Pursuit

---

## Task 3: Populate Athletes

Gather all Nordic athletes (NOR, SWE, FIN, DEN) from current World Cup standings.

### 3.1 Data Collection Approach

For each sport:
1. Get full World Cup standings
2. Extract all athletes from NOR, SWE, FIN, DEN
3. Record: name, country, ranking, points

No pre-filtering - let the data show who competes.

### 3.2 Individual Sports - By Federation

#### FIS Sports (fis-ski.com)
- [ ] Alpine Skiing: All Nordic athletes in overall + discipline standings
- [ ] Cross-Country Skiing: All Nordic athletes in distance + sprint standings
- [ ] Freestyle Skiing: All Nordic athletes by discipline (moguls, aerials, ski cross, halfpipe, slopestyle, big air)
- [ ] Nordic Combined: All Nordic athletes in standings
- [ ] Ski Jumping: All Nordic athletes in standings
- [ ] Snowboard: All Nordic athletes by discipline (PGS, cross, halfpipe, slopestyle, big air)

#### IBU (biathlonworld.com)
- [ ] Biathlon: All Nordic athletes in overall + discipline standings

#### ISU (isu.org)
- [ ] Speed Skating: All Nordic athletes in distance standings
- [ ] Short Track: All Nordic athletes in standings (if any)
- [ ] Figure Skating: All Nordic athletes in standings (if any)

#### Other Federations
- [ ] IBSF (Bobsleigh/Skeleton): All Nordic athletes in standings (if any)
- [ ] FIL (Luge): All Nordic athletes in standings (if any)
- [ ] ISMF (Ski Mountaineering): All Nordic athletes in standings (if any)

### 3.3 Team Sports - Check Qualification Status

#### Ice Hockey (IIHF)
- [ ] Men's: Which Nordic countries qualified?
- [ ] Women's: Which Nordic countries qualified?

#### Curling (WCF)
- [ ] Men's: Which Nordic countries qualified?
- [ ] Women's: Which Nordic countries qualified?
- [ ] Mixed Doubles: Which Nordic countries qualified?

### 3.4 Relay/Team Event Entries

For relay and team events, create team entries for each qualified Nordic country:
- [ ] Cross-country relay teams
- [ ] Biathlon relay teams
- [ ] Speed skating team pursuit
- [ ] Short track relay teams (if qualified)

---

## Task 4: Gather Ranking/Points Data

For each athlete, collect current World Cup points and world ranking.

### 4.1 FIS Sports

| Sport | Data Needed | Source URL |
|-------|-------------|------------|
| Cross-country | Overall WC standings | fis-ski.com/DB/cross-country/cup-standings.html |
| Ski Jumping | Overall WC standings | fis-ski.com/DB/ski-jumping/cup-standings.html |
| Nordic Combined | Overall WC standings | fis-ski.com/DB/nordic-combined/cup-standings.html |
| Alpine | Discipline WC standings | fis-ski.com/DB/alpine-skiing/cup-standings.html |
| Freestyle | Discipline WC standings | fis-ski.com/DB/freestyle-skiing/cup-standings.html |
| Snowboard | Discipline WC standings | fis-ski.com/DB/snowboard/cup-standings.html |

- [ ] Scrape/record Cross-country standings
- [ ] Scrape/record Ski Jumping standings
- [ ] Scrape/record Nordic Combined standings
- [ ] Scrape/record Alpine standings (by discipline)
- [ ] Scrape/record Freestyle standings (by discipline)
- [ ] Scrape/record Snowboard standings (by discipline)

### 4.2 IBU Biathlon

- [ ] Scrape/record Biathlon WC standings from biathlonworld.com

### 4.3 ISU Speed Skating

- [ ] Scrape/record Speed Skating WC standings from isu.org

### 4.4 Team Rankings

- [ ] IIHF Men's world ranking
- [ ] IIHF Women's world ranking
- [ ] WCF Men's world ranking
- [ ] WCF Women's world ranking
- [ ] WCF Mixed Doubles ranking

---

## Task 5: Create Competition Entries

Link athletes to competitions with ranking data. Probabilities calculated later.

### 5.1 Structure

For each competition:
1. Identify all Nordic athletes who will compete
2. Create entry with `competition_id`, `athlete_id`, `world_ranking`, `wc_points`
3. Leave `p_gold`, `p_silver`, `p_bronze` as null (calculated in next phase)

### 5.2 Entry Creation (All Sports)

For each of the 116 competitions:
- [ ] Alpine Skiing (11 events)
- [ ] Biathlon (11 events)
- [ ] Bobsleigh (4 events)
- [ ] Cross-Country Skiing (12 events)
- [ ] Curling (3 events)
- [ ] Figure Skating (5 events)
- [ ] Freestyle Skiing (13 events)
- [ ] Ice Hockey (2 events)
- [ ] Luge (5 events)
- [ ] Nordic Combined (3 events)
- [ ] Short Track (9 events)
- [ ] Skeleton (3 events)
- [ ] Ski Jumping (5 events)
- [ ] Ski Mountaineering (3 events)
- [ ] Snowboard (11 events)
- [ ] Speed Skating (14 events)

### 5.3 "Field" Entries

For each competition, create one "field" entry representing all non-Nordic competitors combined.
- [ ] Add field entry for each competition

---

## Data Validation Checklist

Before proceeding to probability calculations:

- [ ] `countries.json` has 4 entries
- [ ] `sports.json` has 16 entries
- [ ] `competitions.json` has 116 entries
- [ ] All competition IDs follow format: `{sport}-{gender}-{event}`
- [ ] All athletes have valid `country_id` (NOR/SWE/FIN/DEN)
- [ ] All entries have valid `competition_id` and `athlete_id`
- [ ] Each competition has at least one Nordic entry OR is marked as "no Nordic contenders"
- [ ] Each competition has exactly one "field" entry

---

## File Outputs

| File | Records | Status |
|------|---------|--------|
| `data/countries.json` | 4 | [ ] |
| `data/sports.json` | 16 | [ ] |
| `data/competitions.json` | 116 | [ ] |
| `data/athletes.json` | ~100-150 | [ ] |
| `data/entries.json` | ~300-500 | [ ] |
