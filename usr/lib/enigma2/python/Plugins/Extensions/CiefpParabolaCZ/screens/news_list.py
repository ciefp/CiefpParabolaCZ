# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label

from ..components.fetcher import fetch_url
from ..components.parser_news import parse_news_list


class CiefpNewsList(Screen):
    PAGE_SIZE = 10  # koliko stavki prikazujemo na jednom ekranu (interni page)

    skin = """
    <screen name="CiefpNewsList" position="center,center" size="1920,1080" flags="wfNoBorder">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#040030" zPosition="-10" />

        <widget name="title" position="60,40" size="1800,60" font="Regular;42"
            foregroundColor="#ffff00" backgroundColor="#050505" 
            halign="center" valign="center" />

        <widget name="header" position="60,95" size="1800,28" font="Regular;26"
            foregroundColor="#30fc03" backgroundColor="#050505"
            halign="left" valign="center" transparent="1" />

        <widget source="list" render="Listbox"
            position="60,130" size="1800,810"
            scrollbarMode="showNever"
            enableWrapAround="1"
            backgroundColor="#1a1a1a">

            <convert type="TemplatedMultiContent">
                {"template": [
                    MultiContentEntryText(pos=(0,0), size=(120,78), font=0, text=0),
                    MultiContentEntryText(pos=(140,0), size=(1650,36), font=1, text=1),
                    MultiContentEntryText(pos=(140,38), size=(1650,36), font=2, text=2),
                ],
                "fonts": [gFont("Regular", 28), gFont("Regular", 28), gFont("Regular", 24)],
                "itemHeight": 78}
            </convert>
        </widget>

        <widget name="footer" position="60,950" size="1800,45" font="Regular;28"
            foregroundColor="#ffff00" backgroundColor="#050505" 
            halign="left" valign="center" />

        <widget name="key_red" position="60,1000" size="600,40" font="Bold;28"
            halign="center" valign="center" backgroundColor="#A00000" foregroundColor="#080808" />
        <widget name="key_green" position="660,1000" size="600,40" font="Bold;28"
            halign="center" valign="center" backgroundColor="#008000" foregroundColor="#080808" />
        <widget name="key_yellow" position="1260,1000" size="600,40" font="Bold;28"
            halign="center" valign="center" backgroundColor="#B0A000" foregroundColor="#080808" />
    </screen>
    """

    def __init__(self, session, name, typ):
        Screen.__init__(self, session)
        self.catName = name
        self.typ = typ

        # web stranice (parabola /stranka-x/)
        self.web_page = 1

        # interna paginacija (10 po ekranu)
        self.ui_page = 1

        self.items_all = []  # sve stavke sa jedne web stranice

        self["title"] = Label("News: %s" % name)
        self["header"] = Label("Datum | Naslov | Opis")
        self["footer"] = Label("")
        self["key_red"] = Label("Back")
        self["key_green"] = Label("Next")
        self["key_yellow"] = Label("Prev")

        self["list"] = List([], enableWrapAround=True)

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "ChannelSelectBaseActions"],
            {
                "ok": self.openArticle,
                "green": self.nextUiPage,
                "yellow": self.prevUiPage,
                "cancel": self.close,
                "red": self.close,

                # LEFT/RIGHT = interna strana (10 stavki)
                "left": self.prevUiPage,
                "right": self.nextUiPage,

                # CH+/CH- (pageUp/pageDown) = web strana
                "nextBouquet": self.nextWebPage,  # CH+
                "prevBouquet": self.prevWebPage,  # CH-

                "up": self.up,
                "down": self.down,
            },
            -1,
        )

        self.reloadWebPage()

    # ---------------- navigation ----------------

    def up(self):
        try:
            self["list"].selectPrevious()
        except Exception:
            pass

    def down(self):
        try:
            self["list"].selectNext()
        except Exception:
            pass

    def prevUiPage(self):
        if self.ui_page > 1:
            self.ui_page -= 1
            self.renderUiPage()

    def nextUiPage(self):
        maxp = self.maxUiPages()
        if self.ui_page < maxp:
            self.ui_page += 1
            self.renderUiPage()

    def prevWebPage(self):
        if self.typ == "novinky":
            return  # po želji kasnije
        if self.web_page > 1:
            self.web_page -= 1
            self.reloadWebPage()

    def nextWebPage(self):
        if self.typ == "novinky":
            return
        self.web_page += 1
        self.reloadWebPage()

    # ---------------- paging helpers ----------------

    def maxUiPages(self):
        if not self.items_all:
            return 1
        n = len(self.items_all)
        p = n // self.PAGE_SIZE
        if n % self.PAGE_SIZE:
            p += 1
        return max(1, p)

    # ---------------- URL + load ----------------

    def _makeUrl(self, web_page):
        if self.typ == "novinky":
            return "https://www.parabola.cz/novinky/"

        if self.typ == "zpravicky":
            if web_page <= 1:
                return "https://www.parabola.cz/zpravicky/"
            return "https://www.parabola.cz/zpravicky/stranka-%d/" % web_page

        if self.typ == "clanky":
            if web_page <= 1:
                return "https://www.parabola.cz/clanky/"
            return "https://www.parabola.cz/clanky/stranka-%d/" % web_page

        return "https://www.parabola.cz/"

    def reloadWebPage(self):
        url = self._makeUrl(self.web_page)

        try:
            data = fetch_url(url)  # može bytes ili tuple
            self.items_all = parse_news_list(data, self.typ) or []
        except Exception as e:
            self.items_all = []
            self["list"].setList([])
            self["footer"].setText("Greška: %s" % str(e))
            return

        # reset interne strane na 1 pri promeni web strane
        self.ui_page = 1
        self.renderUiPage()

    # ---------------- render 10 items ----------------

    def renderUiPage(self):
        start = (self.ui_page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        chunk = self.items_all[start:end]

        rows = []
        for it in chunk:
            rows.append(
                (
                    it.get("date", ""),
                    it.get("title", ""),
                    it.get("desc", ""),
                    it.get("url", ""),
                )
            )

        self["list"].setList(rows)

        self["footer"].setText(
            "Učitano: %d | web: %d | strana: %d/%d (LEFT/RIGHT)  (CH+/CH- web)" %
            (len(self.items_all), self.web_page, self.ui_page, self.maxUiPages())
        )

    # ---------------- open detail ----------------

    def openItem(self):
        sel = self["list"].getCurrent()
        if not sel:
            return

        url = ""
        try:
            url = sel[3]
        except Exception:
            url = ""

        if not url:
            return

        try:
            from .news_detail import CiefpNewsDetail
            self.session.open(CiefpNewsDetail, self.catName, url)
        except Exception:
            pass

    def openArticle(self):
        cur = self["list"].getCurrent()
        if not cur:
            return

        # cur je tuple: (date, title, desc, url)
        try:
            title = cur[1] or ""
            url = cur[3] or ""
        except Exception:
            return

        if not url:
            return

        from .news_detail import NewsDetailScreen
        self.session.open(NewsDetailScreen, url, title)
