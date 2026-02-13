# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List

from ..components.fetcher import fetch_url
from ..components.parser import parse_satellite_overview


class CiefpSatellitesList(Screen):
    skin = """
    <screen name="CiefpSatellitesList" position="center,center" size="1920,1080" flags="wfNoBorder">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#040030" zPosition="-10" />

        <widget name="title" render="Label"
            position="100,80" size="1720,60"
            font="Regular;34"
            foregroundColor="#ffff00"
            backgroundColor="#050505"
            halign="center" valign="center" />

        <widget name="header" render="Label"
            position="100,140" size="1720,34"
            font="Regular;26"
            foregroundColor="#30fc03"
            backgroundColor="#050505"
            halign="left" valign="center" />

        <!-- TABULAR LIST -->
        <widget source="list" render="Listbox"
            position="100,180" size="1720,770"
            foregroundColor="#ffffff" backgroundColor="#1a1a1a"
            scrollbarMode="showOnDemand">

            <convert type="TemplatedMultiContent">
                {"template": [
                    MultiContentEntryText(pos=(10,0),   size=(500,42), font=0, text=0),  # Program
                    MultiContentEntryText(pos=(520,0),  size=(100,42), font=0, text=1),  # Freq
                    MultiContentEntryText(pos=(630,0),  size=(50,42),  font=0, text=2),  # Pol
                    MultiContentEntryText(pos=(690,0),  size=(210,42), font=0, text=3),  # Žanr
                    MultiContentEntryText(pos=(910,0),  size=(330,42), font=0, text=4),  # Jezik
                    MultiContentEntryText(pos=(1250,0), size=(120,42), font=0, text=5),  # SR
                    MultiContentEntryText(pos=(1380,0), size=(130,42), font=0, text=6),  # FEC
                    MultiContentEntryText(pos=(1520,0), size=(85,42),  font=0, text=7),  # Norma
                    MultiContentEntryText(pos=(1615,0), size=(90,42),  font=0, text=8)   # Mod
                ],
                "fonts": [gFont("Regular", 28)],
                "itemHeight": 35
                }
            </convert>

        </widget>

        <widget name="status" render="Label"
            position="100,950" size="1720,40"
            font="Regular;26"
            foregroundColor="#30fc03"
            backgroundColor="#050505"
            halign="left" valign="center" />

        <widget name="key_red" render="Label"
            position="100,1000" size="860,40"
            font="Bold;26"
            foregroundColor="#080808"
            backgroundColor="#a00000"
            halign="center" valign="center" />

        <widget name="key_green" render="Label"
            position="960,1000" size="860,40"
            font="Bold;26"
            foregroundColor="#080808"
            backgroundColor="#00a000"
            halign="center" valign="center" />
    </screen>
    """

    def __init__(self, session, sat_name, sat_url):
        Screen.__init__(self, session)

        self.sat_name = sat_name
        self.sat_url = sat_url

        self["title"] = Label("Satellite: %s" % sat_name)
        self["header"] = Label("Program / Channels   |  Freq  | Pol | Žanr | Jezik | SR | FEC | Norma | Mod")
        self["status"] = Label("Učitavam ...")

        # Source list (bez .l)
        self["list"] = List([])

        self["key_red"] = Label("Back")
        self["key_green"] = Label("Refresh")

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "cancel": self.close,
                "red": self.close,
                "green": self.reload,
                "ok": self.ok,
                "up": self.up,
                "down": self.down,
            },
            -1,
        )

        self.onFirstExecBegin.append(self.reload)

    def up(self):
        self["list"].selectPrevious()

    def down(self):
        self["list"].selectNext()

    def ok(self):
        # za sada samo status (kasnije možemo detail ekran)
        cur = self["list"].getCurrent()
        if cur:
            self["status"].setText(cur[0])

    def reload(self):
        html, from_cache, err = fetch_url(self.sat_url, cache_ttl_sec=12 * 60 * 60)
        if err and not html:
            self["status"].setText("Greška: %s" % str(err))
            self["list"].setList([])
            return

        items = parse_satellite_overview(html)
        if not items:
            self["status"].setText("Nema rezultata ili se struktura stranice promenila.")
            self["list"].setList([])
            return

        # mapiramo dict -> tuple (kolone) za TemplatedMultiContent
        rows = []
        for it in items:
            name = it.get("name", "")
            freq = it.get("freq", "")
            pol = it.get("pol", "")
            genre = it.get("genre", "")
            lang = it.get("lang", "")
            sr = it.get("sr", "")
            fec = it.get("fec", "")
            norma = it.get("norma", "")  # ako je kod tebe "norm", promeni ovde
            mod = it.get("mod", "")

            # SR/FEC da bude čitljivije
            sr_txt = ("SR:%s" % sr) if sr else ""
            fec_txt = ("FEC:%s" % fec) if fec else ""

            rows.append((name, freq, pol, genre, lang, sr_txt, fec_txt, norma, mod, it))

        self["list"].setList(rows)

        suffix = " (cache)" if from_cache else ""
        self["status"].setText("Učitano: %d kanala%s" % (len(rows), suffix))
