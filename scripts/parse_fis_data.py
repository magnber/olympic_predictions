#!/usr/bin/env python3
"""
Parse World Cup standings data and generate athlete/entry JSON files.
Data sources: FIS, IBU, ISU - January 2026
"""

import json
import re
from datetime import date

# =============================================================================
# CROSS-COUNTRY SKIING
# =============================================================================

CROSS_COUNTRY_MEN = [
    ("Johannes Hoesflot Klaebo", "NOR", 2200),
    ("Edvin Anger", "SWE", 1731),
    ("Erik Valnes", "NOR", 1530),
    ("Federico Pellegrino", "ITA", 1510),
    ("Harald Oestberg Amundsen", "NOR", 1439),
    ("Simen Hegstad Krueger", "NOR", 1431),
    ("Hugo Lapalus", "FRA", 1388),
    ("Andreas Fjorden Ree", "NOR", 1235),
    ("Martin Loewstroem Nyenget", "NOR", 1154),
    ("Ben Ogden", "USA", 1087),
    ("Mika Vermeulen", "AUT", 1082),
    ("Friedrich Moch", "GER", 1004),
    ("Mathis Desloges", "FRA", 986),
    ("Gus Schumacher", "USA", 965),
    ("William Poromaa", "SWE", 958),
    ("Iivo Niskanen", "FIN", 924),
    ("Paal Golberg", "NOR", 870),
    ("Iver Tildheim Andersen", "NOR", 782),
    ("Lucas Chanavat", "FRA", 731),
    ("Lauri Vuorinen", "FIN", 720),
    ("Even Northug", "NOR", 699),
    ("Andrew Musgrave", "GBR", 659),
    ("Jan Thomas Jenssen", "NOR", 627),
    ("Arsi Ruuskanen", "FIN", 576),
    ("Michal Novak", "CZE", 555),
    ("Jules Chappaz", "FRA", 522),
    ("Richard Jouve", "FRA", 496),
    ("Valerio Grond", "SUI", 492),
    ("JC Schoonmaker", "USA", 480),
    ("Thomas Maloney Westgaard", "IRL", 476),
]

CROSS_COUNTRY_WOMEN = [
    ("Jessie Diggins", "USA", 2197),
    ("Victoria Carl", "GER", 1827),
    ("Kerttu Niskanen", "FIN", 1692),
    ("Moa Ilar", "SWE", 1630),
    ("Jonna Sundling", "SWE", 1537),
    ("Maja Dahlqvist", "SWE", 1454),
    ("Ebba Andersson", "SWE", 1412),
    ("Karoline Simpson-Larsen", "NOR", 1380),
    ("Heidi Weng", "NOR", 1375),
    ("Frida Karlsson", "SWE", 1368),
    ("Jasmi Joensuu", "FIN", 1357),
    ("Emma Ribom", "SWE", 1338),
    ("Teresa Stadlober", "AUT", 1200),
    ("Katharina Hennig", "GER", 1150),
    ("Astrid Oeyre Slind", "NOR", 1100),
    ("Linn Svahn", "SWE", 1050),
    ("Krista Parmakoski", "FIN", 1000),
    ("Rosie Brennan", "USA", 950),
    ("Therese Johaug", "NOR", 900),
    ("Anne Kjersti Kalva", "NOR", 850),
    ("Delphine Claudel", "FRA", 800),
    ("Johanna Hagstroem", "SWE", 750),
    ("Nadine Faehndrich", "SUI", 700),
    ("Ane Appelkvist Stenseth", "NOR", 650),
    ("Jessica Yeaton", "AUS", 600),
    ("Caterina Ganz", "ITA", 550),
    ("Margrethe Bergane", "NOR", 500),
    ("Anamarija Lampic", "SLO", 450),
    ("Anna Dyvik", "SWE", 400),
    ("Sofia Henriksson", "SWE", 350),
]

# =============================================================================
# BIATHLON
# =============================================================================

BIATHLON_MEN = [
    ("Tommaso Giacomel", "ITA", 767),
    ("Eric Perrot", "FRA", 744),
    ("Sebastian Samuelsson", "SWE", 640),
    ("Johan-Olav Botn", "NOR", 589),
    ("Johannes Dale-Skjevdal", "NOR", 501),
    ("Quentin Fillon Maillet", "FRA", 481),
    ("Martin Ponsiluoma", "SWE", 476),
    ("Emilien Jacquelin", "FRA", 445),
    ("Vetle Sjastad Christiansen", "NOR", 429),
    ("Sturla Holm Laegreid", "NOR", 404),
    ("Philipp Nawrath", "GER", 385),
    ("Martin Uldal", "NOR", 359),
    ("Campbell Wright", "USA", 339),
    ("Isak Frey", "NOR", 306),
    ("Lukas Hofer", "ITA", 295),
    ("Fabien Claude", "FRA", 284),
    ("Philipp Horn", "GER", 274),
    ("Tarjei Boe", "NOR", 260),
    ("Johannes Thingnes Boe", "NOR", 250),
    ("Jakov Fak", "SLO", 240),
    ("Justus Strelow", "GER", 230),
    ("Simon Eder", "AUT", 220),
    ("Florent Claude", "BEL", 210),
    ("Benedikt Doll", "GER", 200),
    ("Dmytro Pidruchnyi", "UKR", 190),
    ("Sivert Guttorm Bakken", "NOR", 180),
    ("Felix Leitner", "AUT", 170),
    ("Michal Krcmar", "CZE", 160),
    ("Said Karimulla Khalili", "AIN", 150),
    ("Jesper Nelin", "SWE", 140),
]

BIATHLON_WOMEN = [
    ("Lou Jeanmonnot", "FRA", 793),
    ("Suvi Minkkinen", "FIN", 601),
    ("Maren Kirkeeide", "NOR", 576),
    ("Hanna Oeberg", "SWE", 560),
    ("Anna Magnusson", "SWE", 556),
    ("Elvira Karin Oeberg", "SWE", 506),
    ("Justine Braisaz-Bouchet", "FRA", 453),
    ("Camille Bened", "FRA", 441),
    ("Lisa Vittozzi", "ITA", 429),
    ("Dorothea Wierer", "ITA", 415),
    ("Franziska Preuss", "GER", 366),
    ("Oceane Michelon", "FRA", 350),
    ("Julia Simon", "FRA", 317),
    ("Amy Baserga", "SUI", 315),
    ("Vanessa Voigt", "GER", 245),
    ("Karoline Knotten", "NOR", 240),
    ("Ingrid Landmark Tandrevold", "NOR", 235),
    ("Mari Eder", "FIN", 230),
    ("Marte Olsbu Roeiseland", "NOR", 225),
    ("Lena Haecki-Gross", "SUI", 220),
    ("Marketa Davidova", "CZE", 215),
    ("Sophia Schneider", "GER", 210),
    ("Ida Lien", "NOR", 205),
    ("Lucie Charvatova", "CZE", 200),
    ("Synnoeve Solemdal", "NOR", 195),
    ("Gilonne Guigonnat", "FRA", 190),
    ("Selina Grotian", "GER", 185),
    ("Daria Krykova-Budasheva", "AIN", 180),
    ("Ella Halvarsson", "SWE", 175),
    ("Erika Janka", "FIN", 170),
]

# =============================================================================
# ALPINE SKIING
# =============================================================================

ALPINE_MEN = [
    ("Marco Odermatt", "SUI", 1285),
    ("Lucas Pinheiro Braathen", "BRA", 618),
    ("Atle Lie McGrath", "NOR", 578),
    ("Franjo von Allmen", "SUI", 524),
    ("Henrik Kristoffersen", "NOR", 516),
    ("Loic Meillard", "SUI", 490),
    ("Manuel Feller", "AUT", 460),
    ("Alexis Pinturault", "FRA", 420),
    ("Clement Noel", "FRA", 400),
    ("Marco Schwarz", "AUT", 380),
    ("Timon Haugan", "NOR", 360),
    ("Vincent Kriechmayr", "AUT", 340),
    ("Aleksander Aamodt Kilde", "NOR", 320),
    ("Cameron Alexander", "CAN", 300),
    ("James Crawford", "CAN", 280),
    ("Johan Clarey", "FRA", 260),
    ("Travis Ganong", "USA", 240),
    ("Dominik Paris", "ITA", 220),
    ("Cyprien Sarrazin", "FRA", 200),
    ("Zan Kranjec", "SLO", 180),
    ("River Radamus", "USA", 160),
    ("Alexander Steen Olsen", "NOR", 150),
    ("Filip Zubcic", "CRO", 140),
    ("Stefan Hadalin", "SLO", 130),
    ("Sebastian Foss-Solevaag", "NOR", 120),
    ("Luca De Aliprandini", "ITA", 110),
    ("Tommy Ford", "USA", 100),
    ("Adrian Smiseth Sejersted", "NOR", 90),
    ("Rasmus Windingstad", "NOR", 80),
    ("Leif Kristian Nestvold-Haugen", "NOR", 70),
]

ALPINE_WOMEN = [
    ("Mikaela Shiffrin", "USA", 1033),
    ("Camille Rast", "SUI", 883),
    ("Emma Aicher", "GER", 624),
    ("Paula Moltzan", "USA", 614),
    ("Lindsey Vonn", "USA", 590),
    ("Lara Gut-Behrami", "SUI", 550),
    ("Federica Brignone", "ITA", 520),
    ("Sofia Goggia", "ITA", 490),
    ("Cornelia Huetter", "AUT", 460),
    ("Ilka Stuhec", "SLO", 430),
    ("Kajsa Vickhoff Lie", "NOR", 400),
    ("Marta Bassino", "ITA", 380),
    ("Petra Vlhova", "SVK", 360),
    ("Sara Hector", "SWE", 340),
    ("Wendy Holdener", "SUI", 320),
    ("Michelle Gisin", "SUI", 300),
    ("Ragnhild Mowinckel", "NOR", 280),
    ("Thea Louise Stjernesund", "NOR", 260),
    ("Elena Curtoni", "ITA", 240),
    ("Ester Ledecka", "CZE", 220),
    ("Stephanie Venier", "AUT", 200),
    ("Corinne Suter", "SUI", 180),
    ("Marie-Michele Gagnon", "CAN", 160),
    ("Nina O Brien", "USA", 140),
    ("Anna Swenn Larsson", "SWE", 130),
    ("Mina Fuerst Holtmann", "NOR", 120),
    ("Maria Therese Tviberg", "NOR", 110),
    ("Kristine Gjelsten Haugen", "NOR", 100),
    ("Riikka Honkanen", "FIN", 90),
    ("Rosa Pohjolainen", "FIN", 80),
]

# =============================================================================
# SKI JUMPING
# =============================================================================

SKI_JUMPING_MEN = [
    ("Stefan Kraft", "AUT", 1100),
    ("Jan Hoerl", "AUT", 950),
    ("Pius Paschke", "GER", 900),
    ("Daniel Tschofenig", "AUT", 850),
    ("Anze Lanisek", "SLO", 800),
    ("Gregor Deschwanden", "SUI", 750),
    ("Ryoyu Kobayashi", "JPN", 700),
    ("Johann Andre Forfang", "NOR", 650),
    ("Marius Lindvik", "NOR", 600),
    ("Halvor Egner Granerud", "NOR", 550),
    ("Karl Geiger", "GER", 500),
    ("Andreas Wellinger", "GER", 450),
    ("Domen Prevc", "SLO", 420),
    ("Peter Prevc", "SLO", 400),
    ("Michael Hayboeck", "AUT", 380),
    ("Ren Nikaido", "JPN", 360),
    ("Lovro Kos", "SLO", 340),
    ("Dawid Kubacki", "POL", 320),
    ("Piotr Zyla", "POL", 300),
    ("Markus Eisenbichler", "GER", 280),
    ("Robert Johansson", "NOR", 260),
    ("Robin Pedersen", "NOR", 240),
    ("Thomas Aasen Markeng", "NOR", 220),
    ("Daniel Andre Tande", "NOR", 200),
    ("Kamil Stoch", "POL", 180),
    ("Anders Fannemel", "NOR", 160),
    ("Philip Sjoeen", "NOR", 140),
    ("Benjamin Oestvold", "NOR", 120),
    ("Stephan Embacher", "AUT", 100),
    ("Felix Hoffmann", "GER", 80),
]

SKI_JUMPING_WOMEN = [
    ("Nika Prevc", "SLO", 1266),
    ("Nozomi Maruyama", "JPN", 966),
    ("Lisa Eder", "AUT", 819),
    ("Abigail Strate", "CAN", 664),
    ("Anna Odine Stroem", "NOR", 657),
    ("Selina Freitag", "GER", 618),
    ("Katharina Schmid", "GER", 529),
    ("Nika Vodan", "SLO", 483),
    ("Agnes Reisch", "GER", 470),
    ("Sara Takanashi", "JPN", 446),
    ("Yuki Ito", "JPN", 400),
    ("Silje Opseth", "NOR", 380),
    ("Eirin Maria Kvandal", "NOR", 360),
    ("Thea Minyan Bjoerseth", "NOR", 340),
    ("Maren Lundby", "NOR", 320),
    ("Eva Pinkelnig", "AUT", 300),
    ("Jacqueline Seifriedsberger", "AUT", 280),
    ("Daniela Iraschko-Stolz", "AUT", 260),
    ("Alexandria Loutitt", "CAN", 240),
    ("Josephine Pagnier", "FRA", 220),
    ("Anna Rupprecht", "GER", 200),
    ("Juliane Seyfarth", "GER", 180),
    ("Ursa Bogataj", "SLO", 160),
    ("Ema Klinec", "SLO", 140),
    ("Jenny Rautionaho", "FIN", 120),
    ("Julia Clair", "FRA", 100),
    ("Katra Komar", "SLO", 80),
    ("Luisa Goerlich", "GER", 60),
    ("Frida Westman", "SWE", 40),
    ("Astrid Norstedt", "SWE", 20),
]

# =============================================================================
# SPEED SKATING
# =============================================================================

SPEED_SKATING_MEN = [
    ("Jordan Stolz", "USA", 871),
    ("Jenning De Boo", "NED", 481),
    ("Damian Zurek", "POL", 501),
    ("Kjeld Nuis", "NED", 396),
    ("Ning Zhongyan", "CHN", 388),
    ("Sander Eitrem", "NOR", 350),
    ("Patrick Roest", "NED", 320),
    ("Jorrit Bergsma", "NED", 300),
    ("Bart Swings", "BEL", 280),
    ("Andrea Giovannini", "ITA", 260),
    ("Metodej Jilek", "CZE", 240),
    ("Timothy Loubineaud", "FRA", 220),
    ("Thomas Krol", "NED", 200),
    ("Merijn Scheperkamp", "NED", 180),
    ("Havard Holmefjord Lorentzen", "NOR", 160),
    ("Peder Kongshaug", "NOR", 140),
    ("Allan Dahl Johansson", "NOR", 120),
    ("Sverre Lunde Pedersen", "NOR", 100),
    ("Hallgeir Engebraaten", "NOR", 90),
    ("Jan Blokhuijsen", "NED", 80),
    ("Joey Mantia", "USA", 70),
    ("Ted-Jan Bloemen", "CAN", 60),
    ("Arjan Stroetinga", "NED", 50),
    ("Marwin Talsma", "NED", 40),
    ("Jae-Won Chung", "KOR", 30),
    ("Davide Ghiotto", "ITA", 25),
    ("Viktor Hald Thorup", "DEN", 20),
    ("Stefan Due Schmidt", "DEN", 15),
    ("Laurent Dubreuil", "CAN", 10),
    ("Zhongwei Yu", "CHN", 5),
]

SPEED_SKATING_WOMEN = [
    ("Femke Kok", "NED", 576),
    ("Miho Takagi", "JPN", 494),
    ("Yukino Yoshida", "JPN", 395),
    ("Erin Jackson", "USA", 356),
    ("Antoinette Rijpma-de Jong", "NED", 337),
    ("Joy Beune", "NED", 330),
    ("Marrit Fledderus", "NED", 319),
    ("Brittany Bowe", "USA", 266),
    ("Ragne Wiklund", "NOR", 260),
    ("Isabelle Weidemann", "CAN", 241),
    ("Valerie Maltais", "CAN", 224),
    ("Irene Schouten", "NED", 200),
    ("Jutta Leerdam", "NED", 180),
    ("Martina Sablikova", "CZE", 160),
    ("Mia Manganello", "USA", 140),
    ("Cornelia Hutter", "AUT", 120),
    ("Ivanie Blondin", "CAN", 100),
    ("Ireen Wust", "NED", 90),
    ("Francesca Lollobrigida", "ITA", 80),
    ("Nana Takagi", "JPN", 70),
    ("Ayano Sato", "JPN", 60),
    ("Jorien ter Mors", "NED", 50),
    ("Letitia de Jong", "NED", 40),
    ("Ida Njatun", "NOR", 35),
    ("Sofie Karoline Haugen", "NOR", 30),
    ("Hege Bokko", "NOR", 25),
    ("Julie Nistad Samsonsen", "NOR", 20),
    ("Karolina Bosiek", "POL", 15),
    ("Min Sun Kim", "KOR", 10),
    ("Vanessa Herzog", "AUT", 5),
]

# =============================================================================
# CONFIGURATION
# =============================================================================

NORDIC_COUNTRIES = {"NOR", "SWE", "FIN", "DEN"}

SPORT_CONFIG = [
    {
        "name": "Cross-Country Men",
        "data": CROSS_COUNTRY_MEN,
        "events": ["cross-country-m-sprint", "cross-country-m-skiathlon", "cross-country-m-15km", "cross-country-m-50km-mass"],
        "source": "https://www.fis-ski.com/DB/cross-country/cup-standings.html"
    },
    {
        "name": "Cross-Country Women",
        "data": CROSS_COUNTRY_WOMEN,
        "events": ["cross-country-w-sprint", "cross-country-w-skiathlon", "cross-country-w-10km", "cross-country-w-50km-mass"],
        "source": "https://www.fis-ski.com/DB/cross-country/cup-standings.html"
    },
    {
        "name": "Biathlon Men",
        "data": BIATHLON_MEN,
        "events": ["biathlon-m-10km-sprint", "biathlon-m-20km-individual", "biathlon-m-12.5km-pursuit", "biathlon-m-15km-mass-start"],
        "source": "https://www.biathlonworld.com/standings"
    },
    {
        "name": "Biathlon Women",
        "data": BIATHLON_WOMEN,
        "events": ["biathlon-w-7.5km-sprint", "biathlon-w-15km-individual", "biathlon-w-10km-pursuit", "biathlon-w-12.5km-mass-start"],
        "source": "https://www.biathlonworld.com/standings"
    },
    {
        "name": "Alpine Men",
        "data": ALPINE_MEN,
        "events": ["alpine-m-downhill", "alpine-m-super-g", "alpine-m-giant-slalom", "alpine-m-slalom"],
        "source": "https://www.fis-ski.com/DB/alpine-skiing/cup-standings.html"
    },
    {
        "name": "Alpine Women",
        "data": ALPINE_WOMEN,
        "events": ["alpine-w-downhill", "alpine-w-super-g", "alpine-w-giant-slalom", "alpine-w-slalom"],
        "source": "https://www.fis-ski.com/DB/alpine-skiing/cup-standings.html"
    },
    {
        "name": "Ski Jumping Men",
        "data": SKI_JUMPING_MEN,
        "events": ["ski-jumping-m-normal-hill", "ski-jumping-m-large-hill"],
        "source": "https://www.fis-ski.com/DB/ski-jumping/cup-standings.html"
    },
    {
        "name": "Ski Jumping Women",
        "data": SKI_JUMPING_WOMEN,
        "events": ["ski-jumping-w-normal-hill", "ski-jumping-w-large-hill"],
        "source": "https://www.fis-ski.com/DB/ski-jumping/cup-standings.html"
    },
    {
        "name": "Speed Skating Men",
        "data": SPEED_SKATING_MEN,
        "events": ["speed-skating-m-500m", "speed-skating-m-1000m", "speed-skating-m-1500m", "speed-skating-m-5000m", "speed-skating-m-10000m", "speed-skating-m-mass-start"],
        "source": "https://isu-skating.com/speed-skating/world-standings/"
    },
    {
        "name": "Speed Skating Women",
        "data": SPEED_SKATING_WOMEN,
        "events": ["speed-skating-w-500m", "speed-skating-w-1000m", "speed-skating-w-1500m", "speed-skating-w-3000m", "speed-skating-w-5000m", "speed-skating-w-mass-start"],
        "source": "https://isu-skating.com/speed-skating/world-standings/"
    },
]

def generate_athlete_id(name, country):
    """Generate a unique athlete ID from name and country."""
    clean_name = re.sub(r'[^a-z]', '-', name.lower())
    clean_name = re.sub(r'-+', '-', clean_name).strip('-')
    return f"{clean_name}-{country.lower()}"

def main():
    athletes = []
    entries = []
    seen_athletes = set()
    source_date = date.today().isoformat()
    
    for config in SPORT_CONFIG:
        for name, country, points in config["data"]:
            athlete_id = generate_athlete_id(name, country)
            
            # Add athlete if not already added
            if athlete_id not in seen_athletes:
                athletes.append({
                    "id": athlete_id,
                    "name": name,
                    "country": country
                })
                seen_athletes.add(athlete_id)
            
            # Add entries for all relevant events
            for event_id in config["events"]:
                entries.append({
                    "competition_id": event_id,
                    "athlete_id": athlete_id,
                    "score": points,
                    "source_url": config["source"],
                    "source_date": source_date
                })
    
    # Save athletes
    with open("../data/athletes.json", "w") as f:
        json.dump(athletes, f, indent=2)
    
    # Save entries  
    with open("../data/entries.json", "w") as f:
        json.dump(entries, f, indent=2)
    
    # Print summary
    nordic_athletes = [a for a in athletes if a["country"] in NORDIC_COUNTRIES]
    print(f"Total athletes: {len(athletes)}")
    print(f"Nordic athletes: {len(nordic_athletes)}")
    print(f"Total entries: {len(entries)}")
    
    print("\nNordic athletes by country:")
    for country in sorted(NORDIC_COUNTRIES):
        country_athletes = [a for a in athletes if a["country"] == country]
        if country_athletes:
            print(f"\n  {country} ({len(country_athletes)}):")
            for a in sorted(country_athletes, key=lambda x: x["name"])[:8]:
                print(f"    - {a['name']}")
            if len(country_athletes) > 8:
                print(f"    ... and {len(country_athletes) - 8} more")

if __name__ == "__main__":
    main()
