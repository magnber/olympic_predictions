# V2 Sanity Check - Prediksjon vs Historiske resultater

Dato: 5. februar 2026

## Historisk benchmark (siste 3 vinter-OL)

| År | Sted | 🥇 Vinner | Medaljer | 🥈 2. plass | 🥉 3. plass |
|----|------|-----------|----------|-------------|-------------|
| 2022 | Beijing | **Norge** | 37 | ROC 32 | Tyskland 26 |
| 2018 | PyeongChang | **Norge** | 39 | Tyskland 31 | Canada 29 |
| 2014 | Sotsji | **Norge** | 26 | Canada 25 | USA 28 |

**Norge har aldri tatt mer enn 39 medaljer** i et vinter-OL.

---

## Sammenligning: V2 Prediksjon vs Historikk

| Rank | Land | V2 Pred | 2022 | 2018 | Historisk snitt | Vurdering |
|------|------|---------|------|------|-----------------|-----------|
| 1 | USA | **34** | 25 | 23 | ~25 | ⚠️ **Overestimert** |
| 2 | NOR | **32** | 37 | 39 | ~37 | ⚠️ Underestimert |
| 3 | GER | **28** | 27 | 31 | ~28 | ✓ OK |
| 4 | CAN | **22** | 26 | 29 | ~27 | ⚠️ Litt lav |
| 5 | SWE | **21** | 18 | 14 | ~16 | ⚠️ **Overestimert** |
| 6 | FRA | **19** | 14 | 15 | ~14 | ⚠️ Overestimert |
| 7 | AUT | **18** | 18 | 14 | ~15 | ✓ OK |
| 8 | SUI | **17** | 14 | 15 | ~14 | ⚠️ Litt høy |
| 9 | JPN | **15** | 18 | 13 | ~14 | ✓ OK |
| 10 | ITA | **15** | 17 | 10 | ~13 | ✓ OK (vert 2026) |
| 11 | NED | **14** | 17 | 20 | ~17 | ⚠️ Underestimert |
| 12 | CHN | **9** | 15 | 9 | ~11 | ⚠️ Underestimert |
| 13 | FIN | **7** | 8 | 6 | ~7 | ✓ OK |
| 14 | KOR | **7** | 9 | 17 | ~10 | ⚠️ Underestimert |
| 15 | SLO | **5** | 7 | 2 | ~4 | ✓ OK |

---

## Hovedfunn

### ⚠️ Overestimerte land

**1. USA (34 vs historisk ~25)**
- Vår prediksjon: 34 medaljer
- Historisk snitt: 23-28 medaljer
- **Årsak**: Trolig fortsatt noe event-spesialisering-problem (Shiffrin i alle alpine events)

**2. Sverige (21 vs historisk ~16)**
- Vår prediksjon: 21 medaljer
- Historisk: 14-18 medaljer
- Offisielt mål: 15 medaljer
- **Årsak**: Event-spesialisering-problem i alpine/langrenn

**3. Frankrike (19 vs historisk ~14)**
- Vår prediksjon: 19 medaljer
- Historisk: 14-15 medaljer
- **Årsak**: Samme problem

### ⚠️ Underestimerte land

**4. Norge (32 vs historisk 37-39)**
- Vår prediksjon: 32 medaljer
- Historisk: 37 (2022), 39 (2018)
- **Årsak**: Begrenset data i curling, bobsled. Norge har ekstremt dybde.

**5. Nederland (14 vs historisk 17-20)**
- Vår prediksjon: 14 medaljer
- Historisk: 17-20 medaljer
- **Årsak**: ISU-data er bedre, men NED dominerer skøyter mer enn modellen fanger

**6. Kina (9 vs historisk 15)**
- Vår prediksjon: 9 medaljer
- Historisk: 15 (2022, hjemmebane)
- **Årsak**: Begrenset short track data

### ✓ Rimelige prediksjoner

- Tyskland, Canada, Østerrike, Japan, Italia, Finland, Slovenia: Innenfor historisk rekkevidde

---

## Idrettsdekning i datagrunnlaget

| Idrett | Entries | Status | Kommentar |
|--------|---------|--------|-----------|
| Speed Skating | 314 | ✓ ISU API | Event-spesifikk, høy kvalitet |
| Biathlon | 270 | ⚠️ Manual | Overall standings, ikke event-spesifikk |
| Cross-Country | 268 | ⚠️ Manual | Overall standings |
| Alpine Skiing | 228 | ⚠️ Manual | Overall standings |
| Freestyle Skiing | 160 | ⚠️ Manual | - |
| Ski Jumping | 136 | ⚠️ Manual | - |
| Snowboard | 88 | ⚠️ Manual | - |
| **Short Track** | 66 | ⚠️ Begrenset | Viktig for CHN, KOR |
| Nordic Combined | 36 | ⚠️ Manual | - |
| Bobsleigh | 36 | ⚠️ Begrenset | Viktig for GER |
| Curling | 26 | ⚠️ Begrenset | Viktig for CAN, SWE |
| Figure Skating | 22 | ⚠️ Begrenset | Viktig for JPN, USA |
| Luge | 19 | ⚠️ Begrenset | - |
| **Ice Hockey** | 16 | ⚠️ Begrenset | Kun 2 medaljer, men høy profil |
| Skeleton | 16 | ⚠️ Begrenset | - |
| Ski Mountaineering | 0 | ❌ Mangler | Ny idrett 2026 |

**Problemet**: Begrenset data i flere idretter betyr færre utøvere → færre predikerte medaljer.

---

## Konklusjon

**Modellens styrker:**
- ✓ ISU-data løser Stolz-problemet (event-spesifikk)
- ✓ Rimelige prediksjoner for GER, CAN, AUT, JPN, ITA, FIN
- ✓ Riktig rangering av topp-nasjoner

**Modellens svakheter:**
- ⚠️ **Overestimerer** land med alpine-spesialister (USA, SWE, FRA) pga event-spesialisering
- ⚠️ **Underestimerer** Norge (mangler 5-7 medaljer vs historikk)
- ⚠️ Begrenset data i curling, bobsled, short track

**Anbefalt forbedring:**
1. Fikse alpine event-spesialisering (Shiffrin kun SL/GS)
2. Forbedre curling/bobsled-dekning
3. Vurdere "depth factor" for Norge (flere medaljer fra dybde)

---

## Nordiske land - detaljert sammenligning

| Land | V2 Pred | 2022 | 2018 | 2014 | Vurdering |
|------|---------|------|------|------|-----------|
| **Norge** | 32 | 37 | 39 | 26 | ⚠️ Under historisk toppnivå |
| **Sverige** | 21 | 18 | 14 | 15 | ⚠️ Over historisk snitt |
| **Finland** | 7 | 8 | 6 | 5 | ✓ Rimelig |
| **Danmark** | 0 | 0 | 0 | 0 | ✓ Korrekt |

---

## Kilder

- Historiske medaljetall: Olympics.com, Wikipedia
- Vinter-OL 2022: Norge 37, ROC 32, Tyskland 26
- Vinter-OL 2018: Norge 39, Tyskland 31, Canada 29
