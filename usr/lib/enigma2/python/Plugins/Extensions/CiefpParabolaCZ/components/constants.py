# -*- coding: utf-8 -*-
"""
Konstante i početni spiskovi (lako proširivo).
Naziv plugina: CiefpParabolaCZ
Tmp folder: /tmp/CiefpParabolaCZ  (cache fajlovi)
"""
from __future__ import absolute_import, print_function

BASE_URL = "https://www.parabola.cz"

TMP_DIR = "/tmp/CiefpParabolaCZ"

# Minimalni set za test (dodaj/uredi po potrebi).
# Linkovi su direktno ka "Přehledy → Digitální TV programy" po poziciji.# base URL za parabola.cz
BASE_URL = "https://www.parabola.cz"

SATELLITES = [
    ("90°E Jamal 401", BASE_URL + "/prehledy/televize-digital/90e/"),
    ("80,0°E Express 80", BASE_URL + "/prehledy/televize-digital/80e/"),
    ("74,7°E ABS 2, ABS 2A", BASE_URL + "/prehledy/televize-digital/75e/"),
    ("70,5°E Eutelsat 70B", BASE_URL + "/prehledy/televize-digital/70e5/"),
    ("68,5°E Intelsat 20", BASE_URL + "/prehledy/televize-digital/68e5/"),
    ("62°E Intelsat 39", BASE_URL + "/prehledy/televize-digital/62e/"),
    ("56°E Express AT1", BASE_URL + "/prehledy/televize-digital/56e/"),
    ("55°E Jamal 402", BASE_URL + "/prehledy/televize-digital/55e/"),
    ("53°E Express AM6", BASE_URL + "/prehledy/televize-digital/53e/"),
    ("52°E TurkmenÄlem/MonacoSat", BASE_URL + "/prehledy/televize-digital/52e/"),
    ("51,5°E Belintersat 1", BASE_URL + "/prehledy/televize-digital/51e5/"),
    ("50°E Türksat 4B", BASE_URL + "/prehledy/televize-digital/50e/"),
    ("46°E Azerspace 1 / Africasat-1A", BASE_URL + "/prehledy/televize-digital/46e/"),
    ("45°E Azerspace 2/Intelsat 38", BASE_URL + "/prehledy/televize-digital/45e/"),
    ("42°E Türksat 4A, Türksat 3A, Türksat 5B, Türksat 6A", BASE_URL + "/prehledy/televize-digital/42e/"),
    ("39°E Hellas Sat 3, Hellas Sat 4", BASE_URL + "/prehledy/televize-digital/39e/"),
    ("36°E Eutelsat 36D", BASE_URL + "/prehledy/televize-digital/36e/"),
    ("31,0°E Türksat 5A", BASE_URL + "/prehledy/televize-digital/31e/"),
    ("28,2°E Astra 2F, Astra 2E, Astra 2G", BASE_URL + "/prehledy/televize-digital/28e2/"),
    ("26°E Badr 7, Badr 8", BASE_URL + "/prehledy/televize-digital/26e/"),
    ("23,5°E Astra 3B, Astra 3C", BASE_URL + "/prehledy/televize-digital/23e5/"),
    ("21,6°E Eutelsat 21B", BASE_URL + "/prehledy/televize-digital/21e5/"),
    ("19,2°E Astra 1KR, Astra 1M, Astra 1N, Astra 1P", BASE_URL + "/prehledy/televize-digital/19e2/"),
    ("16°E Eutelsat 16A", BASE_URL + "/prehledy/televize-digital/16e/"),
    ("13°E Eutelsat Hot Bird 13F, 13G", BASE_URL + "/prehledy/televize-digital/13e/"),
    ("10°E Eutelsat 10A, 10B", BASE_URL + "/prehledy/televize-digital/10e/"),
    ("9°E Eutelsat 9B", BASE_URL + "/prehledy/televize-digital/09e/"),
    ("7°E Eutelsat 7C, 7B", BASE_URL + "/prehledy/televize-digital/07e/"),
    ("4,8°E Astra 4A, SES 5", BASE_URL + "/prehledy/televize-digital/05e/"),
    ("3°E Eutelsat 3B", BASE_URL + "/prehledy/televize-digital/03e/"),
    ("1,9°E BulgariaSat 1", BASE_URL + "/prehledy/televize-digital/01e9/"),
    ("1°W Intelsat 10-02 / Thor 5/6/7", BASE_URL + "/prehledy/televize-digital/01w/"),
    ("4°W Amos 3", BASE_URL + "/prehledy/televize-digital/04w/"),
    ("5°W Eutelsat 5 West B", BASE_URL + "/prehledy/televize-digital/05w/"),
    ("7°W / 7,2°W Nilesat 201/301, Eutelsat 7 West A", BASE_URL + "/prehledy/televize-digital/07w/"),
    ("14°W Express AM8", BASE_URL + "/prehledy/televize-digital/14w/"),
    ("15°W Telstar 12 Vantage", BASE_URL + "/prehledy/televize-digital/15w/"),
    ("22,0°W SES 4", BASE_URL + "/prehledy/televize-digital/22w/"),
    ("24,8°W AlcomSat 1", BASE_URL + "/prehledy/televize-digital/24w8/"),
    ("30°W Hispasat 30W-5/30W-6", BASE_URL + "/prehledy/televize-digital/30w/"),
    ("34,5°W Intelsat 35e", BASE_URL + "/prehledy/televize-digital/34w5/"),
]


PACKAGES = [
    ("Všechny (CZ/SK)", BASE_URL + "/cz-sk/"),
    ("FTA (CZ/SK)", BASE_URL + "/cz-sk/fta/"),
    ("Skylink", BASE_URL + "/cz-sk/skylink/"),
    ("freeSAT by UPC Direct", BASE_URL + "/cz-sk/upc-direct/"),
    ("Telly", BASE_URL + "/cz-sk/digi-tv/"),
    ("DIGI TV (SK)", BASE_URL + "/cz-sk/digi-tv-sk/"),
    ("Magio Sat", BASE_URL + "/cz-sk/t-home/"),
    ("Antik Sat", BASE_URL + "/cz-sk/antik-sat/"),
]

NEWS_CHOICES = [
    ("Novinky", BASE_URL + "/novinky/"),
    ("Články",  BASE_URL + "/clanky/"),
    ("Zprávičky", BASE_URL + "/zpravicky/"),
]
