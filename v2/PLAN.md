# V2 Data Pipeline Plan

## Mål
Forbedre datagrunnlaget med event-spesifikke scores fra APIer, kombinert med eksisterende data.

## Status (oppdatert)

| Sport | Datakilde | Event-spesialisering | Status |
|-------|-----------|----------------------|--------|
| Skøyter | ISU API | ✅ Ja | **LØST** |
| Skiskyting | Manual | ❌ Nei | IBU API begrenset |
| Alpint | Manual | ❌ Nei | Trenger FIS/manuell fix |
| Langrenn | Manual | ⚠️ Delvis | Allroundere OK |
| Hopping | Manual | ⚠️ Delvis | OK |
| Resten | Manual | ❌ Nei | Lav prioritet |

**Resultater:**
- USA: 43 → 34 medaljer (forbedring -9)
- Nederland: 19 → 14 medaljer (forbedring -5)
- Stolz-problemet: ✅ Løst (8 → 3 events)
- Shiffrin-problemet: ❌ Gjenstår (4 alpine events)

---

## 1. Database Schema

```sql
-- Kjernentiteter
CREATE TABLE countries (
    code TEXT PRIMARY KEY,  -- 'NOR', 'SWE', etc.
    name TEXT
);

CREATE TABLE sports (
    id TEXT PRIMARY KEY,    -- 'cross-country', 'speed-skating'
    name TEXT
);

CREATE TABLE competitions (
    id TEXT PRIMARY KEY,    -- 'speed-skating-m-1000m'
    sport_id TEXT,
    name TEXT,
    gender TEXT,            -- 'M', 'W'
    FOREIGN KEY (sport_id) REFERENCES sports(id)
);

CREATE TABLE athletes (
    id TEXT PRIMARY KEY,    -- 'jordan-stolz-usa'
    name TEXT,
    country_code TEXT,
    FOREIGN KEY (country_code) REFERENCES countries(code)
);

-- Resultat/styrke per event
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id TEXT,
    competition_id TEXT,
    score REAL,             -- Styrke-score
    source TEXT,            -- 'isu_api', 'ibu_api', 'manual'
    updated_at TEXT,
    FOREIGN KEY (athlete_id) REFERENCES athletes(id),
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    UNIQUE(athlete_id, competition_id)
);

-- Ekskluderte utøvere
CREATE TABLE excluded_athletes (
    athlete_id TEXT PRIMARY KEY,
    reason TEXT,            -- 'injury', 'retired', etc.
    FOREIGN KEY (athlete_id) REFERENCES athletes(id)
);
```

---

## 2. Filstruktur

```
v2/
├── PLAN.md                 # Denne filen
├── db/
│   └── olympics.db         # SQLite database
├── models.py               # SQLAlchemy/dataclass modeller
├── database.py             # Database setup og queries
├── pipelines/
│   ├── __init__.py
│   ├── isu_speed_skating.py    # ISU API → DB
│   ├── ibu_biathlon.py         # IBU API → DB
│   └── import_legacy.py        # Eksisterende JSON → DB
├── predict.py              # V2 prediksjon (leser fra DB)
└── run_pipeline.py         # Hovedscript for å kjøre alt
```

---

## 3. Implementeringsplan

### Fase 1: Grunnstruktur ✅
- [x] Opprette v2/ mappe
- [x] database.py - SQLite setup med schema
- [x] import_legacy.py - Importer eksisterende JSON-data

### Fase 2: API-integrasjon (pågående)
- [x] isu_speed_skating.py - API tilgjengelig, standings-import TODO
- [ ] ibu_biathlon.py - Hent cup-standings

### Fase 3: Prediksjon ✅
- [x] predict.py - Tilpasset V3-logikk som leser fra DB
- [x] run_pipeline.py - Orchestrering

---

## 4. Prioriterte API-integrasjoner

| Prioritet | Sport | API | Løser problem |
|-----------|-------|-----|---------------|
| 1 | Skøyter | ISU | Stolz i feil events |
| 2 | Skiskyting | IBU | Event-spesialisering |
| 3 | Resten | Legacy | Beholder dekning |

---

## 5. Enkel første versjon

Start med:
1. SQLite database med schema
2. Import av eksisterende data
3. ISU API for skøyter
4. Prediksjon som leser fra DB

Ikke overtenk - få noe som fungerer først.
