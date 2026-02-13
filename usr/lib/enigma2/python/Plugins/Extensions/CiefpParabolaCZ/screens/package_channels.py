# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List

from ..components.fetcher import fetch_url
from ..components.parser import parse_package_channels, parse_last_update


class CiefpPackageChannels(Screen):
    skin = """
    <screen name="CiefpPackageChannels" position="center,center" size="1920,1080" flags="wfNoBorder">
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

        <!-- TABULAR LIST (isto kao satelite.list.py) -->
        <widget source="list" render="Listbox"
            position="100,180" size="1720,770"
            foregroundColor="#ffffff" backgroundColor="#1a1a1a"
            scrollbarMode="showOnDemand">

            <convert type="TemplatedMultiContent">
                {"template": [
                    MultiContentEntryText(pos=(10,0),   size=(420,42), font=0, text=0),  # Program
                    MultiContentEntryText(pos=(440,0),  size=(240,42), font=0, text=1),  # Žanr
                    MultiContentEntryText(pos=(690,0),  size=(220,42), font=0, text=2),  # Jezik
                    MultiContentEntryText(pos=(920,0),  size=(120,42), font=0, text=3),  # Sat
                    MultiContentEntryText(pos=(1050,0), size=(150,42), font=0, text=4),  # Kmit/Pol
                    MultiContentEntryText(pos=(1210,0), size=(130,42), font=0, text=5),  # SR
                    MultiContentEntryText(pos=(1350,0), size=(130,42), font=0, text=6),  # FEC
                    MultiContentEntryText(pos=(1490,0), size=(120,42), font=0, text=7),  # Norma
                    MultiContentEntryText(pos=(1620,0), size=(110,42), font=0, text=8),  # Mod
                    MultiContentEntryText(pos=(1740,0), size=(170,42), font=0, text=9)   # Provider/Kod (kratko)
                ],
                "fonts": [gFont("Regular", 28)],
                "itemHeight": 42
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

    def __init__(self, session, pkg_name, pkg_url):
        Screen.__init__(self, session)

        self.pkg_name = pkg_name
        self.pkg_url = pkg_url

        self["title"] = Label("Package: %s" % pkg_name)
        self["header"] = Label("Program | Žanr | Jezik | Sat | Kmit/Pol | SR | FEC | Norma | Mod | Provider/Kod")
        self["status"] = Label("Učitavam ...")

        # Source list (bez .l) - kao u satelite.list.py
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
        # kao u satelite.list.py: status = ime programa
        cur = self["list"].getCurrent()
        if cur:
            self["status"].setText(cur[0])

    def reload(self):
        data, from_cache, err = fetch_url(self.pkg_url, cache_ttl_sec=6 * 60 * 60)
        if err and not data:
            self["status"].setText("Greška: %s" % str(err))
            self["list"].setList([])
            return

        items = parse_package_channels(data)
        last_upd = parse_last_update(data)

        if not items:
            self["status"].setText("Nema rezultata ili se struktura stranice promenila.")
            self["list"].setList([])
            return

        rows = []
        for it in items[:5000]:
            program = it.get("program", "")
            genre = it.get("genre", "")
            lang = it.get("lang", "")
            sat = it.get("sat", "")
            kmitpol = it.get("kmitpol", "")
            sr = it.get("sr", "")
            fec = it.get("fec", "")
            norma = it.get("norma", "")
            mod = it.get("mod", "")
            provider = it.get("provider", "")
            kod = it.get("kod", "")

            sr_txt = ("SR:%s" % sr) if sr else ""
            fec_txt = ("FEC:%s" % fec) if fec else ""

            # zadnja kolona: provider + kod (kratko)
            tail = provider
            if kod:
                tail = ("%s | %s" % (provider, kod)) if provider else kod

            rows.append((program, genre, lang, sat, kmitpol, sr_txt, fec_txt, norma, mod, tail, it))

        self["list"].setList(rows)

        suffix = " (cache)" if from_cache else ""
        upd_txt = (" | update: %s" % last_upd) if last_upd else ""
        self["status"].setText("Učitano: %d kanala%s%s" % (len(items), suffix, upd_txt))
