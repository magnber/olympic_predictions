# Data Pipeline: Hvordan vi lager predikasjoner

## Oversikt

Dette dokumentet beskriver hvordan vi bygger datagrunnlaget for OL-prediksjonene, og hvilke begrensninger dette medfører.

---

## 1. Datainnsamling

### Kilde
Vi henter data fra **World Cup (WC) totalstillinger** for sesongen 2025-26.

### Prosess
For hver sport (langrenn, alpint, skiskyting, etc.):
1. Hent overall WC-standing for menn og kvinner
2. Velg **topp ~30 utøvere** basert på totale WC-poeng
3. Tildel hver utøver en **styrke-score** = deres WC-poeng

### Eksempel: Langrenn menn
```
1. Johannes Høsflot Klæbo (NOR): 2200 poeng
2. Edvin Anger (SWE): 1731 poeng
3. Erik Valnes (NOR): 1530 poeng
...
30. [Utøver]: 287 poeng
```

---

## 2. Mapping til OL-konkurranser

### Nåværende tilnærming
Hver utøver mappes til **ALLE konkurranser** i sin sport/kategori med **samme score**.

```
Klæbo (2200 poeng) → Sprint, Skiathlon, 15km, 50km, Team Sprint
Stolz (871 poeng)  → 500m, 1000m, 1500m, 5000m, 10000m, Mass Start
Shiffrin (1033 poeng) → Slalom, Storslalom, Super-G, Utfor
```

### Resultat
- **entries.json**: ~1,800 oppføringer (utøver × konkurranse)
- Hver oppføring har: `athlete_id`, `competition_id`, `score`

---

## 3. Monte Carlo Simulering

### For hver av 100,000 simuleringer:
1. For hver konkurranse:
   - Hent alle utøvere som er påmeldt
   - Beregn `performance = log(score) + støy`
   - Ranger utøvere etter performance
   - Tildel gull/sølv/bronse til topp 3
2. Summer medaljer per land
3. Beregn gjennomsnitt og konfidensintervaller

---

## 4. Problemet: Ingen event-spesialisering

### Symptom
USA predikeres til **43 medaljer** - høyere enn deres historiske rekord (37 i 2010).

### Årsak
Utøvere som er spesialister i én disiplin får samme styrke i ALLE disipliner:

| Utøver | Spesialisering | Faktiske OL-events | Våre data |
|--------|----------------|---------------------|-----------|
| **Jordan Stolz** | Sprint (500m, 1000m) | 500m, 1000m, 1500m, Mass Start | Alle 6 distanser |
| **Mikaela Shiffrin** | Teknisk (SL, GS) | Slalom, Storslalom | Alle 4 alpine |
| **Jessie Diggins** | Distanse | 10km, Skiathlon, 50km | Alle 4 øvelser |

### Konsekvens
```
Jordan Stolz:
  - 10000m gull: 58% sannsynlighet  ← Han deltar IKKE i 10000m!
  - 5000m gull:  58% sannsynlighet  ← Han deltar IKKE i 5000m!
  
Mikaela Shiffrin:
  - Utfor gull:  35% sannsynlighet  ← Hun er ikke utfor-spesialist
  - Super-G gull: 35% sannsynlighet  ← Sjelden på pallen her
```

### Hvorfor dette skjer
WC overall standings belønner allroundere og de som stiller i mange renn. En sprintspesialist som vinner alle 500m/1000m-renn får høy totalsum, som deretter brukes for ALLE distanser.

---

## 5. Påvirkning på prediksjonene

### Hvem overestimeres?
- **USA**: Har mange spesialister (Stolz, Shiffrin)
- **Nederland**: Skøyte-spesialister
- **Østerrike**: Alpine spesialister

### Hvem påvirkes mindre?
- **Norge**: Har dybde og allroundere i mange idretter
- **Sverige**: Lignende situasjon

### Eksempel på feil
| Land | Vår prediksjon | Realistisk? |
|------|----------------|-------------|
| USA | 43 medaljer | Historisk maks: 37 |
| SWE | 21 medaljer | Offisielt mål: 15 |

---

## 6. Mulige løsninger

### A) Event-spesifikke standings (Anbefalt, men arbeidskrevende)
Bruk distanse-spesifikke WC-standings i stedet for overall:
- Langrenn: Sprint-cup, Distance-cup
- Skøyter: 500m/1000m standings, 5000m/10000m standings
- Alpint: Slalom-cup, Speed-cup

**Fordel**: Mye mer nøyaktig
**Ulempe**: Krever manuell datainnsamling for hver disiplin

### B) Begrense utøvere til faktiske events
Manuelt definere hvilke events hver utøver faktisk deltar i:
```python
ATHLETE_EVENTS = {
    "Jordan Stolz": ["500m", "1000m", "1500m", "mass-start"],
    "Mikaela Shiffrin": ["slalom", "giant-slalom"],
}
```

**Fordel**: Direkte fix
**Ulempe**: Må vedlikeholdes manuelt for 600+ utøvere

### C) Disiplin-kategorier (Kompromiss)
Dele sports-kategorier i underkategorier:
- `speed-skating-sprint` (500m, 1000m)
- `speed-skating-distance` (5000m, 10000m)
- `alpine-technical` (SL, GS)
- `alpine-speed` (DH, SG)

**Fordel**: Reduserer problemet betydelig
**Ulempe**: Fortsatt noe unøyaktighet

### D) Akseptere begrensningen
Dokumentere at modellen fungerer best for land med allroundere og dybde, og er mindre nøyaktig for land med mange spesialister.

---

## 7. Nåværende status

| Aspekt | Status |
|--------|--------|
| Datainnsamling | ✓ Fungerer |
| Overall standings | ✓ Implementert |
| Event-spesialisering | ✗ Mangler |
| Monte Carlo | ✓ Fungerer |
| Temperatur-justering | ✓ Implementert |

**Konklusjon**: Modellen gir rimelige resultater for allround-nasjoner, men overestimerer land med mange spesialister.

---

## 8. Tilgjengelige APIer og datakilder

For å forbedre datagrunnlaget kan vi bruke programmatiske grensesnitt (APIer) fra de internasjonale forbundene.

### 8.1 ISU Speed Skating API ⭐ (Beste alternativ)

**URL**: `https://api.isuresults.eu/`

**Dokumentasjon**: https://api.isuresults.eu/docs/

**Tilgjengelige endpoints**:
```
GET /events/?season=2025           # Alle events i en sesong
GET /events/{eventId}/competitions # Distanser/konkurranser
GET /events/{eventId}/competitors  # Utøvere i et event
GET /events/{eventId}/results      # Resultater
```

**Fordeler**:
- ✅ Offisiell API med dokumentasjon
- ✅ Event-spesifikke resultater (500m, 1000m, 5000m separat)
- ✅ JSON-format
- ✅ Gratis tilgang

**Eksempel**:
```python
import requests
response = requests.get("https://api.isuresults.eu/events/?season=2025")
events = response.json()
```

---

### 8.2 IBU Biathlon API

**URL**: `https://api.biathlonresults.com/`

**Tilgjengelige endpoints**:
```
/modules/sportapi/api/Events?SeasonId=2526   # Events per sesong
/modules/sportapi/api/CupResults             # Cup-stillinger
/modules/sportapi/api/Results                # Rennresultater
```

**Fordeler**:
- ✅ Offisiell IBU-data
- ✅ Distanse-spesifikke resultater (sprint, jaktstart, fellesstart)
- ✅ JSON-format

**Ulemper**:
- ⚠️ Begrenset dokumentasjon
- ⚠️ API kan endre seg uten varsel

**Python-pakke**: `pip install biathlonresults` (uoffisiell wrapper)

---

### 8.3 FIS Ski Data (Langrenn, Alpint, Hopping, etc.)

**URL**: https://www.fis-ski.com/DB/

**Programmatisk tilgang**:
- Ingen offisiell API
- XML-format dokumentert for timing/resultater
- Community-prosjekter tilgjengelig

**Alternativer**:

| Ressurs | Type | URL |
|---------|------|-----|
| fisdata (R) | R-pakke | github.com/stibu81/fisdata |
| ski-reference-backend | REST API | api.ski-reference.com |
| FIS XML specs | Dokumentasjon | fis-ski.com/inside-fis/timing-data |

**Eksempel med ski-reference API**:
```python
import requests
response = requests.get("https://api.ski-reference.com/athletes/12345")
```

---

### 8.4 Olympics / Gracenote Data

**Gracenote Virtual Medal Table**:
- Brukes av NBC, BBC og andre store mediehus
- Kommersiell lisens påkrevd
- Metodikk: Analyserer resultater fra store mesterskap

**SportsData.io Olympics API**:
- URL: https://sportsdata.io/olympics-api
- Historisk data fra 1896
- JSON/XML format
- Kommersiell (betalt)

**IOC Olympic Data Feed (ODF)**:
- Offisiell IOC-standard
- Brukes av akkrediterte medier
- Krever lisensavtale

---

### 8.5 Anbefalt strategi for forbedring

**Fase 1: Implementer ISU API (Enkel gevinst)**
```python
# Hent event-spesifikke standings for skøyter
# Erstatter overall WC med distanse-spesifikk data
def get_speed_skating_standings(distance="1000m"):
    url = f"https://api.isuresults.eu/standings/{distance}"
    return requests.get(url).json()
```

**Fase 2: Implementer IBU API**
```python
# Hent sprint-cup og distanse-cup separat
sprint_standings = get_biathlon_cup("sprint")
distance_standings = get_biathlon_cup("individual")
```

**Fase 3: FIS-data via scraping eller community-API**
```python
# Bruk ski-reference API for alpine/langrenn
# Eller implementer FIS XML parsing
```

---

### 8.6 Sammenligning av datakilder

| Sport | Nåværende kilde | Bedre alternativ | Vanskelighetsgrad |
|-------|-----------------|------------------|-------------------|
| Skøyter | Manuell | ISU API ⭐ | Enkel |
| Skiskyting | Manuell | IBU API | Medium |
| Langrenn | Manuell | FIS/ski-reference | Medium |
| Alpint | Manuell | FIS/ski-reference | Medium |
| Hopping | Manuell | FIS XML | Vanskelig |
| Freestyle | Manuell | FIS XML | Vanskelig |
| Snowboard | Manuell | FIS XML | Vanskelig |

**Prioritert rekkefølge**:
1. 🥇 ISU Speed Skating API - Løser Stolz-problemet direkte
2. 🥈 IBU Biathlon API - Viktig for nordiske land
3. 🥉 FIS community tools - Dekker resten

---

### 8.7 Eksempel: Hvordan ISU API løser Stolz-problemet

**Nåværende data** (feil):
```json
{"athlete": "Jordan Stolz", "events": ["500m","1000m","1500m","5000m","10000m","mass-start"], "score": 871}
```

**Med ISU API** (riktig):
```json
{"athlete": "Jordan Stolz", "events": {
  "500m": {"rank": 1, "points": 450},
  "1000m": {"rank": 1, "points": 500},
  "1500m": {"rank": 2, "points": 380},
  "5000m": null,  // Deltar ikke
  "10000m": null  // Deltar ikke
}}
```

Dette gir event-spesifikke scores og fjerner utøvere fra events de ikke deltar i.
