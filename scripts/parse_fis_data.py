#!/usr/bin/env python3
"""
Parse World Cup standings data and generate athlete/entry JSON files.
Data sources: FIS, IBU, ISU - January 2026
"""

import json
import re
from datetime import date
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"

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
# FREESTYLE SKIING
# =============================================================================

FREESTYLE_MOGULS_MEN = [
    ("Mikael Kingsbury", "CAN", 1100),
    ("Matt Graham", "AUS", 950),
    ("Nick Page", "USA", 850),
    ("Ikuma Horishima", "JPN", 800),
    ("Walter Wallberg", "SWE", 750),
    ("Benjamin Cavet", "FRA", 700),
    ("Ludvig Fjallstrom", "SWE", 650),
    ("Daichi Hara", "JPN", 600),
    ("Cole McDonald", "USA", 550),
    ("Dylan Walczyk", "USA", 500),
    ("Rasmus Stegfeldt", "SWE", 450),
    ("Filip Gravenfors", "SWE", 400),
    ("Albin Holmgren", "SWE", 350),
    ("Felix Elofsson", "SWE", 300),
    ("Birk Ruud", "NOR", 250),
]

FREESTYLE_MOGULS_WOMEN = [
    ("Jaelin Kauf", "USA", 1336),
    ("Perrine Laffont", "FRA", 1090),
    ("Tess Johnson", "USA", 683),
    ("Maia Schwinghammer", "CAN", 681),
    ("Olivia Giaccio", "USA", 573),
    ("Jakara Anthony", "AUS", 550),
    ("Anri Kawamura", "JPN", 500),
    ("Hannah Soar", "USA", 450),
    ("Anastassiya Gorodko", "KAZ", 400),
    ("Justine Dufour-Lapointe", "CAN", 350),
    ("Chloe Dufour-Lapointe", "CAN", 300),
    ("Hedda Berntsen", "NOR", 250),
    ("Moa Backlund", "SWE", 200),
    ("Tilde Hansson", "SWE", 150),
]

FREESTYLE_AERIALS_MEN = [
    ("Qi Guangpu", "CHN", 400),
    ("Noe Roth", "SUI", 400),
    ("Wang Xindi", "CHN", 304),
    ("Sun Jiaxu", "CHN", 298),
    ("Christopher Lillis", "USA", 274),
    ("Eric Loughran", "USA", 250),
    ("Maxim Burov", "RUS", 220),
    ("Mykola Puzderko", "UKR", 200),
    ("Lloyd Wallace", "GBR", 180),
    ("Pirmin Werner", "SUI", 160),
]

FREESTYLE_AERIALS_WOMEN = [
    ("Xu Mengtao", "CHN", 400),
    ("Laura Peel", "AUS", 380),
    ("Winter Vinecki", "USA", 320),
    ("Megan Nick", "USA", 300),
    ("Kong Fanyu", "CHN", 280),
    ("Xu Sicun", "CHN", 260),
    ("Marion Thenault", "CAN", 240),
    ("Mengtao Xu", "CHN", 220),
    ("Liubov Nikitina", "RUS", 200),
    ("Olga Polyuk", "UKR", 180),
]

FREESTYLE_SKI_CROSS_MEN = [
    ("Reece Howden", "CAN", 1038),
    ("Simone Deromedis", "ITA", 965),
    ("Florian Wilmsmann", "GER", 902),
    ("Youri Duplessis Kergomard", "FRA", 715),
    ("Alex Fiva", "SUI", 638),
    ("David Mobaerg", "SWE", 544),
    ("Kevin Drury", "CAN", 518),
    ("Ryan Regez", "SUI", 495),
    ("Tobias Baur", "SUI", 413),
    ("Adam Kappacher", "AUT", 392),
    ("Erik Mobaerg", "SWE", 350),
    ("Victor Oehling Norberg", "SWE", 300),
    ("Kristoffer Haugen", "NOR", 250),
    ("Terence Tchiknavorian", "FRA", 200),
]

FREESTYLE_SKI_CROSS_WOMEN = [
    ("Marielle Thompson", "CAN", 900),
    ("Sandra Naeslund", "SWE", 850),
    ("Fanny Smith", "SUI", 800),
    ("Brittany Phelan", "CAN", 700),
    ("Talina Gantenbein", "SUI", 650),
    ("Daniela Maier", "GER", 600),
    ("India Sherret", "CAN", 550),
    ("Lisa Andersson", "SWE", 500),
    ("Alexandra Edebo", "SWE", 450),
    ("Courtney Hoffos", "CAN", 400),
    ("Andrea Limbacher", "AUT", 350),
    ("Alizee Baron", "FRA", 300),
]

FREESTYLE_HALFPIPE_MEN = [
    ("Nico Porteous", "NZL", 600),
    ("Birk Ruud", "NOR", 550),
    ("Alex Ferreira", "USA", 500),
    ("David Wise", "USA", 450),
    ("Aaron Blunck", "USA", 400),
    ("Noah Bowman", "CAN", 350),
    ("Brendan Mackay", "CAN", 300),
    ("Simon D Artois", "CAN", 250),
    ("Kevin Rolland", "FRA", 200),
    ("Ben Harrington", "NZL", 150),
]

FREESTYLE_HALFPIPE_WOMEN = [
    ("Eileen Gu", "CHN", 700),
    ("Rachael Karker", "CAN", 600),
    ("Zoe Atkin", "GBR", 500),
    ("Hanna Faulhaber", "USA", 450),
    ("Amy Fraser", "CAN", 400),
    ("Valeriya Demidova", "RUS", 350),
    ("Sabrina Cakmakli", "GER", 300),
    ("Cassie Sharpe", "CAN", 250),
]

FREESTYLE_SLOPESTYLE_MEN = [
    ("Birk Ruud", "NOR", 700),
    ("Oliwer Magnusson", "SWE", 650),
    ("Alex Hall", "USA", 600),
    ("Mac Forehand", "USA", 550),
    ("Colby Stevenson", "USA", 500),
    ("Andri Ragettli", "SUI", 450),
    ("Ferdinand Dahl", "NOR", 400),
    ("Kim Gubser", "SUI", 350),
    ("Jesper Tjader", "SWE", 300),
    ("Henrik Harlaut", "SWE", 250),
]

FREESTYLE_SLOPESTYLE_WOMEN = [
    ("Eileen Gu", "CHN", 700),
    ("Kelly Sildaru", "EST", 650),
    ("Megan Oldham", "CAN", 600),
    ("Mathilde Gremaud", "SUI", 550),
    ("Olivia Asselin", "CAN", 500),
    ("Darian Stevens", "USA", 450),
    ("Tess Ledeux", "FRA", 400),
    ("Johanne Killi", "NOR", 350),
    ("Jennie-Lee Burmansson", "SWE", 300),
]

# =============================================================================
# SNOWBOARD
# =============================================================================

SNOWBOARD_HALFPIPE_MEN = [
    ("Yuto Totsuka", "JPN", 600),
    ("Valentino Guseli", "AUS", 550),
    ("Ryusei Yamada", "JPN", 500),
    ("Ruka Hirano", "JPN", 450),
    ("Jan Scherrer", "SUI", 400),
    ("Scotty James", "AUS", 350),
    ("Chase Josey", "USA", 300),
    ("Taylor Gold", "USA", 280),
    ("Ayumu Hirano", "JPN", 260),
    ("Andre Hoeflich", "GER", 240),
]

SNOWBOARD_HALFPIPE_WOMEN = [
    ("Chloe Kim", "USA", 700),
    ("Sena Tomita", "JPN", 600),
    ("Queralt Castellet", "ESP", 500),
    ("Xuetong Cai", "CHN", 450),
    ("Maddie Mastro", "USA", 400),
    ("Mitsuki Ono", "JPN", 350),
    ("Elizabeth Hosking", "CAN", 300),
    ("Kurumi Imai", "JPN", 250),
]

SNOWBOARD_SLOPESTYLE_MEN = [
    ("Su Yiming", "CHN", 600),
    ("Kira Kimura", "JPN", 550),
    ("Marcus Kleveland", "NOR", 500),
    ("Mark McMorris", "CAN", 450),
    ("Max Parrot", "CAN", 400),
    ("Mons Roisland", "NOR", 350),
    ("Staale Sandbech", "NOR", 300),
    ("Chris Corning", "USA", 280),
    ("Sebastien Toutant", "CAN", 260),
    ("Red Gerard", "USA", 240),
]

SNOWBOARD_SLOPESTYLE_WOMEN = [
    ("Zoi Sadowski-Synnott", "NZL", 700),
    ("Anna Gasser", "AUT", 650),
    ("Kokomo Murase", "JPN", 600),
    ("Tess Coady", "AUS", 550),
    ("Julia Marino", "USA", 500),
    ("Laurie Blouin", "CAN", 450),
    ("Jamie Anderson", "USA", 400),
    ("Mia Brookes", "GBR", 350),
]

SNOWBOARD_CROSS_MEN = [
    ("Eliot Grondin", "CAN", 827),
    ("Loan Bozzolo", "FRA", 541),
    ("Aidan Chollet", "FRA", 503),
    ("Jakob Dusek", "AUT", 491),
    ("Adam Lambert", "AUS", 394),
    ("Julien Tomas", "FRA", 372),
    ("Cameron Bolton", "AUS", 354),
    ("Leon Ulbricht", "GER", 350),
    ("Alessandro Haemmerle", "AUT", 342),
    ("Merlin Surget", "FRA", 313),
]

SNOWBOARD_CROSS_WOMEN = [
    ("Lindsey Jacobellis", "USA", 700),
    ("Charlotte Bankes", "GBR", 650),
    ("Belle Brockhoff", "AUS", 600),
    ("Caterina Carpano", "ITA", 550),
    ("Michela Moioli", "ITA", 500),
    ("Eva Samkova", "CZE", 450),
    ("Hanna Ihedioha", "GER", 400),
    ("Lara Casanova", "SUI", 350),
]

SNOWBOARD_PGS_MEN = [
    ("Benjamin Karl", "AUT", 600),
    ("Dmitry Loginov", "RUS", 550),
    ("Roland Fischnaller", "ITA", 500),
    ("Tim Mastnak", "SLO", 450),
    ("Sangho Lee", "KOR", 400),
    ("Edwin Coratti", "ITA", 350),
    ("Arvid Auner", "AUT", 300),
    ("Victor Wild", "RUS", 250),
]

SNOWBOARD_PGS_WOMEN = [
    ("Ramona Theresia Hofmeister", "GER", 600),
    ("Ester Ledecka", "CZE", 550),
    ("Daniela Ulbing", "AUT", 500),
    ("Julie Zogg", "SUI", 450),
    ("Sofia Nadyrshina", "RUS", 400),
    ("Selina Joerg", "GER", 350),
    ("Sabine Schoeffmann", "AUT", 300),
    ("Cheyenne Loch", "GER", 250),
]

# =============================================================================
# SHORT TRACK SPEED SKATING
# =============================================================================

SHORT_TRACK_MEN = [
    ("William Dandjinou", "CAN", 800),
    ("Pietro Sighel", "ITA", 750),
    ("Park Ji-won", "KOR", 700),
    ("Hwang Dae-heon", "KOR", 650),
    ("Sebastien Lepape", "FRA", 600),
    ("Liu Shaolin Sandor", "HUN", 550),
    ("Ren Ziwei", "CHN", 500),
    ("Liu Shaoang", "HUN", 450),
    ("Steven Dubois", "CAN", 400),
    ("Pascal Dion", "CAN", 350),
    ("Luca Spechenhauser", "ITA", 300),
    ("Oleh Handei", "UKR", 250),
]

SHORT_TRACK_WOMEN = [
    ("Courtney Sarault", "CAN", 800),
    ("Xandra Velzeboer", "NED", 750),
    ("Kim Gil-li", "KOR", 700),
    ("Choi Min-jeong", "KOR", 650),
    ("Suzanne Schulting", "NED", 600),
    ("Kim Boutin", "CAN", 550),
    ("Natalia Maliszewska", "POL", 500),
    ("Kristen Santos-Griswold", "USA", 450),
    ("Hanne Desmet", "BEL", 400),
    ("Florence Brunelle", "CAN", 350),
]

# =============================================================================
# NORDIC COMBINED
# =============================================================================

NORDIC_COMBINED_MEN = [
    ("Vinzenz Geiger", "GER", 1506),
    ("Johannes Lamparter", "AUT", 1317),
    ("Julian Schmid", "GER", 1100),
    ("Ryota Yamamoto", "JPN", 950),
    ("Stefan Rettenegger", "AUT", 850),
    ("Jens Luraas Oftebro", "NOR", 800),
    ("Manuel Faisst", "GER", 750),
    ("Ilkka Herola", "FIN", 700),
    ("Eero Hirvonen", "FIN", 650),
    ("Joergen Graabak", "NOR", 600),
    ("Espen Andersen", "NOR", 550),
    ("Lukas Greiderer", "AUT", 500),
    ("Espen Bjoernstad", "NOR", 450),
    ("Akito Watabe", "JPN", 400),
]

NORDIC_COMBINED_WOMEN = [
    ("Ida Marie Hagen", "NOR", 790),
    ("Alexa Brabec", "USA", 620),
    ("Minja Korhonen", "FIN", 589),
    ("Nathalie Armbruster", "GER", 510),
    ("Katharina Gruber", "AUT", 472),
    ("Yuna Kasai", "JPN", 459),
    ("Marte Leinan Lund", "NOR", 394),
    ("Lisa Hirner", "AUT", 383),
    ("Ingrid Laate", "NOR", 353),
    ("Jenny Nowak", "GER", 353),
]

# =============================================================================
# FIGURE SKATING
# =============================================================================

FIGURE_SKATING_MEN = [
    ("Ilia Malinin", "USA", 1500),
    ("Yuma Kagiyama", "JPN", 1390),
    ("Adam Siao Him Fa", "FRA", 1333),
    ("Shun Sato", "JPN", 1267),
    ("Daniel Grassl", "ITA", 1186),
    ("Nika Egadze", "GEO", 1156),
    ("Mikhail Shaidorov", "KAZ", 1132),
    ("Lukas Britschgi", "SUI", 1129),
    ("Kazuki Tomono", "JPN", 1105),
    ("Jason Brown", "USA", 1067),
    ("Kevin Aymoz", "FRA", 1000),
    ("Keegan Messing", "CAN", 950),
]

FIGURE_SKATING_WOMEN = [
    ("Kaori Sakamoto", "JPN", 1500),
    ("Isabeau Levito", "USA", 1400),
    ("Loena Hendrickx", "BEL", 1350),
    ("Mai Mihara", "JPN", 1300),
    ("Bradie Tennell", "USA", 1250),
    ("Kim Ye-lim", "KOR", 1200),
    ("Amber Glenn", "USA", 1150),
    ("Mana Kawabe", "JPN", 1100),
    ("Haein Lee", "KOR", 1050),
    ("Young You", "KOR", 1000),
]

# =============================================================================
# LUGE
# =============================================================================

LUGE_MEN = [
    ("Felix Loch", "GER", 246),
    ("Jonas Mueller", "AUT", 245),
    ("Max Langenhan", "GER", 240),
    ("Wolfgang Kindl", "AUT", 159),
    ("Nico Gleirscher", "AUT", 152),
    ("Kristers Aparjods", "LAT", 140),
    ("Dominik Fischnaller", "ITA", 130),
    ("Sebastian Bley", "GER", 120),
    ("Chris Mazdzer", "USA", 100),
    ("Tucker West", "USA", 90),
]

LUGE_WOMEN = [
    ("Julia Taubitz", "GER", 250),
    ("Lisa Schulte", "AUT", 220),
    ("Madeleine Egle", "AUT", 200),
    ("Dajana Eitberger", "GER", 180),
    ("Natalie Geisenberger", "GER", 160),
    ("Tatjana Huefner", "GER", 140),
    ("Summer Britcher", "USA", 120),
    ("Emily Sweeney", "USA", 100),
    ("Eliza Tiruma", "LAT", 90),
]

# =============================================================================
# BOBSLED
# =============================================================================

BOBSLED_MEN = [
    ("Francesco Friedrich", "GER", 800),
    ("Johannes Lochner", "GER", 750),
    ("Adam Edelman", "GER", 700),
    ("Benjamin Maier", "AUT", 650),
    ("Brad Hall", "GBR", 600),
    ("Christoph Hafer", "GER", 550),
    ("Hunter Church", "USA", 500),
    ("Frank Delduca", "USA", 450),
    ("Justin Kripps", "CAN", 400),
    ("Oskars Kibermanis", "LAT", 350),
]

BOBSLED_WOMEN = [
    ("Laura Nolte", "GER", 700),
    ("Lisa Buckwitz", "GER", 650),
    ("Kaillie Humphries", "USA", 600),
    ("Elana Meyers Taylor", "USA", 550),
    ("Mariama Jamanka", "GER", 500),
    ("Christine de Bruin", "CAN", 450),
    ("Kim Kalicki", "GER", 400),
    ("Melanie Hasler", "SUI", 350),
]

# =============================================================================
# SKELETON
# =============================================================================

SKELETON_MEN = [
    ("Matt Weston", "GBR", 600),
    ("Martins Dukurs", "LAT", 550),
    ("Marcus Wyatt", "GBR", 500),
    ("Christopher Grotheer", "GER", 450),
    ("Axel Jungk", "GER", 400),
    ("Austin Florian", "USA", 350),
    ("Vladyslav Heraskevych", "UKR", 300),
    ("Seunggi Jung", "KOR", 280),
]

SKELETON_WOMEN = [
    ("Janine Flock", "AUT", 600),
    ("Kim Meylemans", "BEL", 550),
    ("Tina Hermann", "GER", 500),
    ("Jaclyn Narracott", "AUS", 450),
    ("Kimberley Bos", "NED", 400),
    ("Hannah Neise", "GER", 350),
    ("Amelia Coltman", "GBR", 300),
    ("Katie Uhlaender", "USA", 250),
]

# =============================================================================
# CURLING (Team-based - using team skip/leaders)
# =============================================================================

CURLING_MEN = [
    ("Bruce Mouat", "SCO", 84328),   # Scotland (GBR)
    ("Brad Gushue", "CAN", 77015),
    ("Niklas Edin", "SWE", 67254),
    ("Yannick Schwaller", "SUI", 53716),
    ("Joel Retornaz", "ITA", 41000),
    ("Korey Dropkin", "USA", 38000),
    ("Magnus Ramsfjell", "NOR", 35000),
    ("Steffen Walstad", "NOR", 32000),
]

CURLING_WOMEN = [
    ("Silvana Tirinzoni", "SUI", 89851),
    ("Rachel Homan", "CAN", 83284),
    ("Kim Eun-jung", "KOR", 55925),
    ("Anna Hasselborg", "SWE", 46567),
    ("Satsuki Fujisawa", "JPN", 36836),
    ("Tabitha Peterson", "USA", 33000),
    ("Marianne Roervik", "NOR", 30000),
    ("Kristin Skaslien", "NOR", 28000),
]

# =============================================================================
# ICE HOCKEY (Team-based - using IIHF rankings)
# =============================================================================

HOCKEY_MEN = [
    ("Team Canada", "CAN", 4100),
    ("Team Finland", "FIN", 3955),
    ("Team Czechia", "CZE", 3945),
    ("Team Switzerland", "SUI", 3945),
    ("Team USA", "USA", 3900),
    ("Team Sweden", "SWE", 3850),
    ("Team Germany", "GER", 3600),
    ("Team Slovakia", "SVK", 3500),
]

HOCKEY_WOMEN = [
    ("Team USA", "USA", 4150),
    ("Team Canada", "CAN", 4140),
    ("Team Finland", "FIN", 3930),
    ("Team Czechia", "CZE", 3920),
    ("Team Switzerland", "SUI", 3855),
    ("Team Sweden", "SWE", 3800),
    ("Team Japan", "JPN", 3600),
    ("Team Germany", "GER", 3400),
]

# =============================================================================
# TEAM/RELAY EVENTS (Nation-level entries)
# =============================================================================

# Cross-Country Relay - Men's 4x10km (FIS Nations Cup standings)
CROSS_COUNTRY_RELAY_MEN = [
    ("Team Norway", "NOR", 8096),
    ("Team Sweden", "SWE", 6812),
    ("Team Germany", "GER", 5731),
    ("Team Finland", "FIN", 5420),
    ("Team France", "FRA", 4800),
    ("Team Italy", "ITA", 3500),
    ("Team Switzerland", "SUI", 3200),
    ("Team USA", "USA", 2800),
]

# Cross-Country Relay - Women's 4x5km (FIS Nations Cup standings)
CROSS_COUNTRY_RELAY_WOMEN = [
    ("Team Sweden", "SWE", 7500),
    ("Team Norway", "NOR", 7200),
    ("Team Finland", "FIN", 5800),
    ("Team Germany", "GER", 5400),
    ("Team USA", "USA", 4200),
    ("Team Switzerland", "SUI", 3000),
    ("Team Italy", "ITA", 2500),
    ("Team Austria", "AUT", 2000),
]

# Cross-Country Team Sprint - Men (Top 2 athletes per nation aggregated)
CROSS_COUNTRY_TEAM_SPRINT_MEN = [
    ("Team Norway", "NOR", 3730),   # Klaebo + Valnes
    ("Team Sweden", "SWE", 2689),   # Anger + Poromaa
    ("Team France", "FRA", 2119),   # Lapalus + Desloges
    ("Team Finland", "FIN", 1644),  # Niskanen + Vuorinen
    ("Team USA", "USA", 2052),      # Ogden + Schumacher
    ("Team Germany", "GER", 1004),
    ("Team Italy", "ITA", 1510),    # Pellegrino
    ("Team Switzerland", "SUI", 492),
]

# Cross-Country Team Sprint - Women (Top 2 athletes per nation aggregated)
CROSS_COUNTRY_TEAM_SPRINT_WOMEN = [
    ("Team Sweden", "SWE", 3167),   # Ilar + Sundling
    ("Team Norway", "NOR", 2755),   # Simpson-Larsen + Weng
    ("Team Finland", "FIN", 3049),  # Niskanen + Joensuu
    ("Team Germany", "GER", 2977),  # Carl + Hennig
    ("Team USA", "USA", 3147),      # Diggins + Brennan
    ("Team Switzerland", "SUI", 700),
    ("Team Italy", "ITA", 550),
    ("Team Austria", "AUT", 1200),
]

# Biathlon Relay - Men's 4x7.5km (IBU Nations Cup relay standings)
BIATHLON_RELAY_MEN = [
    ("Team France", "FRA", 90),
    ("Team Norway", "NOR", 75),
    ("Team Sweden", "SWE", 60),
    ("Team Germany", "GER", 50),
    ("Team Finland", "FIN", 45),
    ("Team USA", "USA", 40),
    ("Team Ukraine", "UKR", 36),
    ("Team Switzerland", "SUI", 34),
    ("Team Austria", "AUT", 32),
    ("Team Italy", "ITA", 31),
]

# Biathlon Relay - Women's 4x6km (IBU Nations Cup relay standings)
BIATHLON_RELAY_WOMEN = [
    ("Team France", "FRA", 85),
    ("Team Sweden", "SWE", 70),
    ("Team Germany", "GER", 65),
    ("Team Norway", "NOR", 60),
    ("Team Finland", "FIN", 50),
    ("Team Italy", "ITA", 45),
    ("Team Switzerland", "SUI", 40),
    ("Team USA", "USA", 35),
    ("Team Austria", "AUT", 30),
    ("Team Czechia", "CZE", 25),
]

# Biathlon Mixed Relay (IBU Nations Cup)
BIATHLON_MIXED_RELAY = [
    ("Team France", "FRA", 95),
    ("Team Norway", "NOR", 80),
    ("Team Sweden", "SWE", 75),
    ("Team Germany", "GER", 65),
    ("Team Italy", "ITA", 55),
    ("Team Finland", "FIN", 50),
    ("Team Switzerland", "SUI", 45),
    ("Team USA", "USA", 40),
    ("Team Austria", "AUT", 35),
    ("Team Czechia", "CZE", 30),
]

# Ski Jumping Team - Men's Large Hill (Top 4 jumpers per nation aggregated)
SKI_JUMPING_TEAM_MEN = [
    ("Team Austria", "AUT", 3280),   # Kraft + Hoerl + Tschofenig + Hayboeck
    ("Team Germany", "GER", 1310),   # Paschke + Geiger + Wellinger + Eisenbichler
    ("Team Slovenia", "SLO", 1720),  # Lanisek + D.Prevc + P.Prevc + Kos
    ("Team Norway", "NOR", 2050),    # Forfang + Lindvik + Granerud + Johansson
    ("Team Japan", "JPN", 1060),     # Kobayashi + Nikaido
    ("Team Poland", "POL", 800),     # Kubacki + Zyla + Stoch
    ("Team Switzerland", "SUI", 750),
    ("Team Finland", "FIN", 120),
]

# Ski Jumping Mixed Team (Top 2 men + top 2 women per nation)
SKI_JUMPING_MIXED_TEAM = [
    ("Team Austria", "AUT", 3179),   # Kraft + Hoerl + Eder + Pinkelnig
    ("Team Slovenia", "SLO", 2906),  # Lanisek + D.Prevc + N.Prevc + Vodan
    ("Team Germany", "GER", 2247),   # Paschke + Geiger + Freitag + Schmid
    ("Team Norway", "NOR", 1907),    # Forfang + Lindvik + Stroem + Opseth
    ("Team Japan", "JPN", 2066),     # Kobayashi + Nikaido + Maruyama + Takanashi
    ("Team Canada", "CAN", 904),     # Strate + Loutitt
    ("Team France", "FRA", 320),
    ("Team Switzerland", "SUI", 750),
]

# Nordic Combined Team Sprint - Men (Top 2 per nation)
NORDIC_COMBINED_TEAM_MEN = [
    ("Team Germany", "GER", 2606),   # Geiger + Schmid
    ("Team Austria", "AUT", 2167),   # Lamparter + Rettenegger
    ("Team Japan", "JPN", 1350),     # Yamamoto + Watabe
    ("Team Norway", "NOR", 1400),    # Oftebro + Graabak
    ("Team Finland", "FIN", 1350),   # Herola + Hirvonen
    ("Team France", "FRA", 500),
    ("Team USA", "USA", 400),
    ("Team Italy", "ITA", 300),
]

# Speed Skating Team Pursuit - Men (Nations based on individual depth)
SPEED_SKATING_TEAM_PURSUIT_MEN = [
    ("Team Netherlands", "NED", 1577),  # De Boo + Nuis + Roest + Bergsma
    ("Team Norway", "NOR", 770),        # Eitrem + Lorentzen + Kongshaug + Johansson
    ("Team USA", "USA", 941),           # Stolz + Mantia
    ("Team Italy", "ITA", 285),
    ("Team Canada", "CAN", 70),
    ("Team China", "CHN", 393),
    ("Team South Korea", "KOR", 30),
    ("Team Poland", "POL", 501),
]

# Speed Skating Team Pursuit - Women (Nations based on individual depth)
SPEED_SKATING_TEAM_PURSUIT_WOMEN = [
    ("Team Netherlands", "NED", 1662),  # Kok + Rijpma-de Jong + Beune + Fledderus
    ("Team Japan", "JPN", 1019),        # Takagi + Yoshida + Takagi + Sato
    ("Team Canada", "CAN", 565),        # Weidemann + Maltais + Blondin
    ("Team USA", "USA", 762),           # Jackson + Bowe + Manganello
    ("Team Norway", "NOR", 370),        # Wiklund + Njatun + Haugen
    ("Team Italy", "ITA", 80),
    ("Team Czechia", "CZE", 160),
    ("Team South Korea", "KOR", 10),
]

# Curling Mixed Doubles (WCF Team Rankings - using ranking points)
CURLING_MIXED_DOUBLES = [
    ("Team Scotland", "GBR", 60254),    # Scotland competes as GBR at Olympics
    ("Team Italy", "ITA", 58603),
    ("Team Norway", "NOR", 53254),
    ("Team Sweden", "SWE", 50857),
    ("Team Switzerland", "SUI", 48000),
    ("Team Canada", "CAN", 45000),
    ("Team USA", "USA", 42000),
    ("Team South Korea", "KOR", 38000),
    ("Team Japan", "JPN", 35000),
    ("Team Hungary", "HUN", 32000),
]

# =============================================================================
# CONFIGURATION
# =============================================================================

NORDIC_COUNTRIES = {"NOR", "SWE", "FIN", "DEN"}

# Athletes excluded from predictions (injury, retirement, etc.)
EXCLUDED_ATHLETES = {
    ("Aleksander Aamodt Kilde", "NOR"),  # Injury - shoulder injury and sepsis, uncertain return
    ("Alexander Steen Olsen", "NOR"),    # Knee surgery Dec 2025 - out for 2025/26 season including Olympics
    ("Lara Gut-Behrami", "SUI"),         # ACL tear Nov 2024 - confirmed out for 2026 Olympics
    # ("Therese Johaug", "NOR"),         # Retired May 2025 - not in current WC standings anyway
}

SPORT_CONFIG = [
    # Cross-Country Skiing
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
    # Biathlon
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
    # Alpine Skiing
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
    # Ski Jumping
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
    # Speed Skating
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
    # Freestyle Skiing - Moguls
    {
        "name": "Freestyle Moguls Men",
        "data": FREESTYLE_MOGULS_MEN,
        "events": ["freestyle-m-moguls", "freestyle-m-dual-moguls"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/moguls-aerials/cup-standings.html"
    },
    {
        "name": "Freestyle Moguls Women",
        "data": FREESTYLE_MOGULS_WOMEN,
        "events": ["freestyle-w-moguls", "freestyle-w-dual-moguls"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/moguls-aerials/cup-standings.html"
    },
    # Freestyle Skiing - Aerials
    {
        "name": "Freestyle Aerials Men",
        "data": FREESTYLE_AERIALS_MEN,
        "events": ["freestyle-m-aerials"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/moguls-aerials/cup-standings.html"
    },
    {
        "name": "Freestyle Aerials Women",
        "data": FREESTYLE_AERIALS_WOMEN,
        "events": ["freestyle-w-aerials"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/moguls-aerials/cup-standings.html"
    },
    # Freestyle Skiing - Ski Cross
    {
        "name": "Freestyle Ski Cross Men",
        "data": FREESTYLE_SKI_CROSS_MEN,
        "events": ["freestyle-m-ski-cross"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/ski-cross/cup-standings.html"
    },
    {
        "name": "Freestyle Ski Cross Women",
        "data": FREESTYLE_SKI_CROSS_WOMEN,
        "events": ["freestyle-w-ski-cross"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/ski-cross/cup-standings.html"
    },
    # Freestyle Skiing - Halfpipe
    {
        "name": "Freestyle Halfpipe Men",
        "data": FREESTYLE_HALFPIPE_MEN,
        "events": ["freestyle-m-halfpipe"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/freeski/cup-standings.html"
    },
    {
        "name": "Freestyle Halfpipe Women",
        "data": FREESTYLE_HALFPIPE_WOMEN,
        "events": ["freestyle-w-halfpipe"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/freeski/cup-standings.html"
    },
    # Freestyle Skiing - Slopestyle & Big Air
    {
        "name": "Freestyle Slopestyle Men",
        "data": FREESTYLE_SLOPESTYLE_MEN,
        "events": ["freestyle-m-slopestyle", "freestyle-m-big-air"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/freeski/cup-standings.html"
    },
    {
        "name": "Freestyle Slopestyle Women",
        "data": FREESTYLE_SLOPESTYLE_WOMEN,
        "events": ["freestyle-w-slopestyle", "freestyle-w-big-air"],
        "source": "https://www.fis-ski.com/DB/freestyle-freeski/freeski/cup-standings.html"
    },
    # Snowboard - Halfpipe
    {
        "name": "Snowboard Halfpipe Men",
        "data": SNOWBOARD_HALFPIPE_MEN,
        "events": ["snowboard-m-halfpipe"],
        "source": "https://www.fis-ski.com/DB/snowboard/snowboard-halfpipe/cup-standings.html"
    },
    {
        "name": "Snowboard Halfpipe Women",
        "data": SNOWBOARD_HALFPIPE_WOMEN,
        "events": ["snowboard-w-halfpipe"],
        "source": "https://www.fis-ski.com/DB/snowboard/snowboard-halfpipe/cup-standings.html"
    },
    # Snowboard - Slopestyle & Big Air
    {
        "name": "Snowboard Slopestyle Men",
        "data": SNOWBOARD_SLOPESTYLE_MEN,
        "events": ["snowboard-m-slopestyle", "snowboard-m-big-air"],
        "source": "https://www.fis-ski.com/DB/snowboard/snowboard-slopestyle/cup-standings.html"
    },
    {
        "name": "Snowboard Slopestyle Women",
        "data": SNOWBOARD_SLOPESTYLE_WOMEN,
        "events": ["snowboard-w-slopestyle", "snowboard-w-big-air"],
        "source": "https://www.fis-ski.com/DB/snowboard/snowboard-slopestyle/cup-standings.html"
    },
    # Snowboard - Cross
    {
        "name": "Snowboard Cross Men",
        "data": SNOWBOARD_CROSS_MEN,
        "events": ["snowboard-m-cross"],
        "source": "https://www.fis-ski.com/DB/snowboard/snowboard-cross/cup-standings.html"
    },
    {
        "name": "Snowboard Cross Women",
        "data": SNOWBOARD_CROSS_WOMEN,
        "events": ["snowboard-w-cross"],
        "source": "https://www.fis-ski.com/DB/snowboard/snowboard-cross/cup-standings.html"
    },
    # Snowboard - Parallel Giant Slalom
    {
        "name": "Snowboard PGS Men",
        "data": SNOWBOARD_PGS_MEN,
        "events": ["snowboard-m-pgs"],
        "source": "https://www.fis-ski.com/DB/snowboard/parallel/cup-standings.html"
    },
    {
        "name": "Snowboard PGS Women",
        "data": SNOWBOARD_PGS_WOMEN,
        "events": ["snowboard-w-pgs"],
        "source": "https://www.fis-ski.com/DB/snowboard/parallel/cup-standings.html"
    },
    # Short Track Speed Skating
    {
        "name": "Short Track Men",
        "data": SHORT_TRACK_MEN,
        "events": ["short-track-m-500m", "short-track-m-1000m", "short-track-m-1500m"],
        "source": "https://isu-skating.com/short-track/world-standings/"
    },
    {
        "name": "Short Track Women",
        "data": SHORT_TRACK_WOMEN,
        "events": ["short-track-w-500m", "short-track-w-1000m", "short-track-w-1500m"],
        "source": "https://isu-skating.com/short-track/world-standings/"
    },
    # Nordic Combined
    {
        "name": "Nordic Combined Men",
        "data": NORDIC_COMBINED_MEN,
        "events": ["nordic-combined-m-normal-hill", "nordic-combined-m-large-hill"],
        "source": "https://www.fis-ski.com/DB/nordic-combined/cup-standings.html"
    },
    {
        "name": "Nordic Combined Women",
        "data": NORDIC_COMBINED_WOMEN,
        "events": [],  # No women's individual events at 2026 Olympics yet
        "source": "https://www.fis-ski.com/DB/nordic-combined/cup-standings.html"
    },
    # Figure Skating
    {
        "name": "Figure Skating Men",
        "data": FIGURE_SKATING_MEN,
        "events": ["figure-skating-m"],
        "source": "https://isu-skating.com/figure-skating/world-standings/"
    },
    {
        "name": "Figure Skating Women",
        "data": FIGURE_SKATING_WOMEN,
        "events": ["figure-skating-w"],
        "source": "https://isu-skating.com/figure-skating/world-standings/"
    },
    # Luge
    {
        "name": "Luge Men",
        "data": LUGE_MEN,
        "events": ["luge-m-singles"],
        "source": "https://www.fil-luge.org/en/overall-scores"
    },
    {
        "name": "Luge Women",
        "data": LUGE_WOMEN,
        "events": ["luge-w-singles"],
        "source": "https://www.fil-luge.org/en/overall-scores"
    },
    # Bobsled
    {
        "name": "Bobsled Men",
        "data": BOBSLED_MEN,
        "events": ["bobsled-m-two-man", "bobsled-m-four-man"],
        "source": "https://www.ibsf.org/en/races-and-results"
    },
    {
        "name": "Bobsled Women",
        "data": BOBSLED_WOMEN,
        "events": ["bobsled-w-two-woman", "bobsled-w-monobob"],
        "source": "https://www.ibsf.org/en/races-and-results"
    },
    # Skeleton
    {
        "name": "Skeleton Men",
        "data": SKELETON_MEN,
        "events": ["skeleton-m"],
        "source": "https://www.ibsf.org/en/races-and-results"
    },
    {
        "name": "Skeleton Women",
        "data": SKELETON_WOMEN,
        "events": ["skeleton-w"],
        "source": "https://www.ibsf.org/en/races-and-results"
    },
    # Curling
    {
        "name": "Curling Men",
        "data": CURLING_MEN,
        "events": ["curling-m"],
        "source": "https://worldcurling.org/teamrankings/"
    },
    {
        "name": "Curling Women",
        "data": CURLING_WOMEN,
        "events": ["curling-w"],
        "source": "https://worldcurling.org/teamrankings/"
    },
    # Ice Hockey
    {
        "name": "Hockey Men",
        "data": HOCKEY_MEN,
        "events": ["hockey-m"],
        "source": "https://www.iihf.com/en/worldranking"
    },
    {
        "name": "Hockey Women",
        "data": HOCKEY_WOMEN,
        "events": ["hockey-w"],
        "source": "https://www.iihf.com/en/worldranking"
    },
    # =========================================================================
    # TEAM/RELAY EVENTS
    # =========================================================================
    # Cross-Country Relays
    {
        "name": "Cross-Country Relay Men",
        "data": CROSS_COUNTRY_RELAY_MEN,
        "events": ["cross-country-m-relay"],
        "source": "https://www.fis-ski.com/DB/cross-country/cup-standings.html",
        "type": "team"
    },
    {
        "name": "Cross-Country Relay Women",
        "data": CROSS_COUNTRY_RELAY_WOMEN,
        "events": ["cross-country-w-relay"],
        "source": "https://www.fis-ski.com/DB/cross-country/cup-standings.html",
        "type": "team"
    },
    {
        "name": "Cross-Country Team Sprint Men",
        "data": CROSS_COUNTRY_TEAM_SPRINT_MEN,
        "events": ["cross-country-m-team-sprint"],
        "source": "https://www.fis-ski.com/DB/cross-country/cup-standings.html",
        "type": "team"
    },
    {
        "name": "Cross-Country Team Sprint Women",
        "data": CROSS_COUNTRY_TEAM_SPRINT_WOMEN,
        "events": ["cross-country-w-team-sprint"],
        "source": "https://www.fis-ski.com/DB/cross-country/cup-standings.html",
        "type": "team"
    },
    # Biathlon Relays
    {
        "name": "Biathlon Relay Men",
        "data": BIATHLON_RELAY_MEN,
        "events": ["biathlon-m-relay"],
        "source": "https://www.biathlonworld.com/standings",
        "type": "team"
    },
    {
        "name": "Biathlon Relay Women",
        "data": BIATHLON_RELAY_WOMEN,
        "events": ["biathlon-w-relay"],
        "source": "https://www.biathlonworld.com/standings",
        "type": "team"
    },
    {
        "name": "Biathlon Mixed Relay",
        "data": BIATHLON_MIXED_RELAY,
        "events": ["biathlon-x-mixed-relay"],
        "source": "https://www.biathlonworld.com/standings",
        "type": "team"
    },
    # Ski Jumping Team Events
    {
        "name": "Ski Jumping Team Men",
        "data": SKI_JUMPING_TEAM_MEN,
        "events": ["ski-jumping-m-team"],
        "source": "https://www.fis-ski.com/DB/ski-jumping/cup-standings.html",
        "type": "team"
    },
    {
        "name": "Ski Jumping Mixed Team",
        "data": SKI_JUMPING_MIXED_TEAM,
        "events": ["ski-jumping-x-mixed-team"],
        "source": "https://www.fis-ski.com/DB/ski-jumping/cup-standings.html",
        "type": "team"
    },
    # Nordic Combined Team
    {
        "name": "Nordic Combined Team Men",
        "data": NORDIC_COMBINED_TEAM_MEN,
        "events": ["nordic-combined-m-team-sprint"],
        "source": "https://www.fis-ski.com/DB/nordic-combined/cup-standings.html",
        "type": "team"
    },
    # Speed Skating Team Pursuit
    {
        "name": "Speed Skating Team Pursuit Men",
        "data": SPEED_SKATING_TEAM_PURSUIT_MEN,
        "events": ["speed-skating-m-team-pursuit"],
        "source": "https://isu-skating.com/speed-skating/world-standings/",
        "type": "team"
    },
    {
        "name": "Speed Skating Team Pursuit Women",
        "data": SPEED_SKATING_TEAM_PURSUIT_WOMEN,
        "events": ["speed-skating-w-team-pursuit"],
        "source": "https://isu-skating.com/speed-skating/world-standings/",
        "type": "team"
    },
    # Curling Mixed Doubles
    {
        "name": "Curling Mixed Doubles",
        "data": CURLING_MIXED_DOUBLES,
        "events": ["curling-x-mixed-doubles"],
        "source": "https://worldcurling.org/teamrankings/mixed-doubles/",
        "type": "team"
    },
]

def generate_athlete_id(name, country):
    """Generate a unique athlete ID from name and country."""
    clean_name = re.sub(r'[^a-z]', '-', name.lower())
    clean_name = re.sub(r'-+', '-', clean_name).strip('-')
    return f"{clean_name}-{country.lower()}"

def generate_team_id(country):
    """Generate a unique team ID from country code."""
    return f"team-{country.lower()}"

def main():
    athletes = []
    entries = []
    seen_athletes = set()
    seen_teams = set()
    source_date = date.today().isoformat()
    
    for config in SPORT_CONFIG:
        is_team_event = config.get("type") == "team"
        
        for name, country, points in config["data"]:
            # Skip excluded athletes (injury, retirement, etc.)
            if (name, country) in EXCLUDED_ATHLETES:
                print(f"  Excluding: {name} ({country}) - not participating")
                continue
            
            if is_team_event:
                # Team event: use team ID instead of athlete ID
                team_id = generate_team_id(country)
                
                # Add team as an "athlete" if not already added
                if team_id not in seen_teams:
                    athletes.append({
                        "id": team_id,
                        "name": name,
                        "country": country,
                        "type": "team"
                    })
                    seen_teams.add(team_id)
                
                # Add entries for team events
                for event_id in config["events"]:
                    entries.append({
                        "competition_id": event_id,
                        "athlete_id": team_id,
                        "score": points,
                        "source_url": config["source"],
                        "source_date": source_date
                    })
            else:
                # Individual event: use athlete ID
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
    with open(DATA_DIR / "athletes.json", "w") as f:
        json.dump(athletes, f, indent=2)
    
    # Save entries  
    with open(DATA_DIR / "entries.json", "w") as f:
        json.dump(entries, f, indent=2)
    
    # Print summary
    individual_athletes = [a for a in athletes if a.get("type") != "team"]
    team_entries = [a for a in athletes if a.get("type") == "team"]
    nordic_athletes = [a for a in individual_athletes if a["country"] in NORDIC_COUNTRIES]
    nordic_teams = [t for t in team_entries if t["country"] in NORDIC_COUNTRIES]
    
    print(f"Total individual athletes: {len(individual_athletes)}")
    print(f"Total team entries: {len(team_entries)}")
    print(f"Nordic individual athletes: {len(nordic_athletes)}")
    print(f"Nordic team entries: {len(nordic_teams)}")
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
