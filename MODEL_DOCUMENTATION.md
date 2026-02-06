# Modell-dokumentasjon: Olympic Medal Prediction

## 1. Teoretisk grunnlag

### Hvorfor Plackett-Luce?

Plackett-Luce er **industristandard** for sportsprediksjoner:

- Brukt i Formel 1-prediksjoner (Henderson & Sherwin, 2017)
- Brukt i friidrett og skisport
- Forskningsartikler bekrefter at Gumbel-støy + log(strength) er korrekt implementasjon

**Referanser:**
- [Plackett–Luce modeling with trajectory models](https://www.degruyter.com/document/doi/10.1515/jqas-2021-0034/html)
- [Time-Weighted Plackett-Luce for F1](https://projecteuclid.org/journals/bayesian-analysis/volume-13/issue-2/)

### Plackett-Luce modellen

**Grunnleggende idé:**
- Hver utøver har en "styrke" (strength) basert på deres prestasjoner
- Sannsynlighet for å vinne er proporsjonal med styrke
- For 2. og 3. plass: Fjern vinneren og gjenta

**Matematisk (eksakte formler):**
```
P(gull for i)  = s_i / Σ(s_j)
P(sølv for i)  = Σ_{k≠i} [P(k vinner) × s_i / (Σ(s_j) - s_k)]
P(bronse for i) = Σ_{k≠i} Σ_{j≠i,k} [P(k vinner) × P(j sølv|k) × s_i / (Σ(s_j) - s_k - s_j)]
```

### Gumbel-noise for Monte Carlo

For å sample fra Plackett-Luce bruker vi **Gumbel-fordelt støy**:

```python
noisy_value = log(strength) + Gumbel(0, 1)
```

**Matematisk garanti:** Dette gir eksakt Plackett-Luce-fordeling:
```
P(argmax{noisy_value} = i) = strength_i / Σ(strength_j)
```

### Ekstra støy for variasjon

Utover standard Plackett-Luce kan vi legge til ekstra støy:

```python
noisy_value = log(strength) + Gumbel(0,1) + extra_noise
```

- **extra_noise = 0**: Ren Plackett-Luce (simulering konvergerer til eksakt modell)
- **extra_noise > 0**: Mer upsets, reflekterer race-day variasjon

### Forventet G/S/B-asymmetri

I en konkurranse med n utøvere med styrke s₁ > s₂ > ... > sₙ:
- Favoritten (s₁) har høyest P(gull), men også høy P(sølv/bronse)
- Når vi aggregerer over mange konkurranser, blir G/S/B-forholdet jevnere

**Viktig innsikt**: G/S/B-symmetri på landnivå er FORVENTET når:
1. Landet har mange "gode" utøvere (dybde) i stedet for få dominerende
2. Konkurransene har mange sterke deltakere fra ulike land

## 2. Datagrunnlag

### Kilder

| Kilde | Idretter | Skala | Kommentar |
|-------|----------|-------|-----------|
| ISU API | Skøyter | 0-905 | WC-poeng per distanse |
| FIS Scraping | Alpint | 0-665 | WC-poeng per disiplin |
| Manual JSON | Resten | Varierer | Ulike poengsystemer |

### Skala-forskjeller (OK!)

Forskjellige idretter har forskjellige skalaer, men dette er OK fordi:
- Vi simulerer INNEN hver konkurranse
- En curling-match sammenligner kun curling-lag
- En skøyte-distanse sammenligner kun skøyteløpere

### Problemer identifisert

| Problem | Konkurranse | Effekt |
|---------|-------------|--------|
| Lav ratio | Hockey (1.17) | Nesten tilfeldig |
| Lav ratio | Figure skating (1.5) | Nesten tilfeldig |
| Ingen data | Ski mountaineering | Mangler |

## 3. Disiplin-spesialisering

### Implementert korrekt ✓

**Alpint (FIS data):**
- Shiffrin: Kun i SL (486 pts) og GS (51 pts)
- Odermatt: I DH (605), GS (580), SG (536) - ikke SL
- Kristoffersen: SL (662), GS (454)

**Skøyter (ISU data):**
- Stolz: Kun i 500m, 1000m, 1500m
- Ikke i 5000m, 10000m (ikke hans distanser)

### Delvis implementert ⚠

**Cross-country (FIS data):**
- ✓ Sprint standings → sprint-konkurranser
- ✓ Distance standings → 15km, 50km, skiathlon, relay
- Klæbo: Sprint 927 pts, Distance 973 pts
- Krüger: Kun Distance 1317 pts (ingen sprint)

**Biathlon:**
- ✗ Bruker overall WC standings
- Samme score for ALLE distanser/formater

## 4. Beregningsflyt

```
1. Load entries from SQLite
   └── Filtrerer ut excluded_athletes

2. For hver konkurranse:
   └── Hent alle entries med score > 0
   └── Beregn log_strength = log(score)

3. Monte Carlo (10,000 simuleringer):
   For hver simulering:
     For hver konkurranse:
       └── noisy = log_strength + temp * Gumbel()
       └── Sorter etter noisy (synkende)
       └── Gull = #1, Sølv = #2, Bronse = #3
   
4. Aggreger resultater:
   └── Gjennomsnitt medaljer per land
   └── Konfidensintervaller
```

## 5. Kjente begrensninger

### Datakvalitet
1. **Uniform biathlon scores**: Alle distanser får samme poeng
2. **Hockey/curling har flat fordeling**: Lite differensiering
3. **Mangler noen idretter**: Ski mountaineering, etc.

### Modell-begrensninger
1. **Ingen korrelasjon mellom idretter**: Klæbo's form i sprint påvirker ikke skiathlon
2. **Statisk styrke**: Ingen dag-til-dag variasjon
3. **Ingen OL-spesifikk form**: Noen utøvere "peaker" for OL

## 6. Validering av datagrunnlag

### Status per idrett

| Idrett | Kilde | Disiplin-data | Kommentar |
|--------|-------|---------------|-----------|
| Alpint | FIS scraping | ✓ | SL/GS/SG/DH separat |
| Skøyter | ISU API | ✓ | Alle distanser separat |
| Langrenn | FIS scraping | ✓ | Sprint vs Distance separat |
| Skiskyting | Manual | ✗ | UNIFORM - samme score alle konkurranser |
| Hopp | Manual | ✗ | UNIFORM - normal/large hill samme |
| Hockey | Manual | ⚠ | Lav differensiering (ratio 1.17) |
| Curling | Manual | ⚠ | Lav differensiering (ratio 1.88) |

### Kritiske funn

1. **Langrenn** ✓ LØST: Nå med disiplin-spesifikke data
   - Klæbo: Sprint 927 pts, Distance 973 pts
   - Krüger: Kun Distance 1317 pts (ingen sprint-entries)
   - Distance-spesialister deltar ikke i sprint-simuleringer

2. **Skiskyting**: Alle utøvere har uniform score
   - Sprint-spesialister overkrediteres i distanse
   - Distanse-spesialister overkrediteres i sprint

## 7. Anbefalte forbedringer

### Høy prioritet

#### 1. ✓ Cross-country disiplin-data (IMPLEMENTERT)
Implementert i `pipelines/fis_cross_country.py`:
- Sprint standings → sprint, team-sprint
- Distance standings → 15km, 50km, skiathlon, relay

#### 2. Biathlon disiplin-data (IBU scraping)
**Kilde**: `biathlonworld.com/standings`

Tilgjengelige disipliner:
- Sprint (10km/7.5km)
- Pursuit (12.5km/10km)
- Individual (20km/15km)
- Mass Start (15km/12.5km)

**Implementering**: Lag `pipelines/ibu_biathlon.py`

#### 3. Bedre hockey/curling data
**Problem**: Lav differensiering i nåværende data
**Løsning**: Finn IIHF/WCF ranking eller historiske resultater

### Middels prioritet
1. **Normalisering**: Konverter alle scores til percentiler innen konkurranse
2. **Historisk kalibrering**: Juster temperatur basert på historiske OL-resultater

### Lav prioritet
1. **Form-faktor**: Vekt nylige resultater høyere
2. **OL-erfaring**: Bonus for tidligere OL-medaljer

## 8. Konklusjon

Modellen fungerer korrekt matematisk:

| Aspekt | Status | Påvirkning |
|--------|--------|------------|
| Plackett-Luce | ✓ | Fungerer som forventet |
| Alpint | ✓ | FIS scraping - SL/GS/SG/DH |
| Skøyter | ✓ | ISU API - alle distanser |
| Langrenn | ✓ | FIS scraping - Sprint vs Distance |
| Skiskyting | ✗ | Uniform score → jevn G/S/B |
| Hockey/Curling | ⚠ | Flat fordeling → tilfeldig |

**Neste steg**: Implementer IBU biathlon pipeline for disiplin-spesifikke data.
