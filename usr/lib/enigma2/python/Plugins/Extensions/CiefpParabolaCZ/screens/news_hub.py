# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.Pixmap import Pixmap

from .news_list import CiefpNewsList

try:
    from Tools.Directories import resolveFilename, SCOPE_PLUGINS
except Exception:
    resolveFilename = None
    SCOPE_PLUGINS = None


class CiefpNewsHub(Screen):
    skin = """
    <screen name="CiefpNewsHub" position="center,center" size="1920,1080" flags="wfNoBorder">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#040030" zPosition="-10" />

        <widget name="title" position="60,80" size="1800,60"
            font="Regular;34" halign="center" valign="center"
            foregroundColor="#ffff00" backgroundColor="#050505" />

        <widget name="header" position="60,140" size="1800,34"
            font="Regular;26" halign="left" valign="center"
            foregroundColor="#30fc03" backgroundColor="#050505" />

        <widget source="list" render="Listbox"
            position="60,180" size="1380,740"
            foregroundColor="#ffffff" backgroundColor="#1a1a1a"
            scrollbarMode="showOnDemand">
            <convert type="TemplatedMultiContent">
                {"template": [
                    MultiContentEntryText(pos=(20,0), size=(1200,42), font=0, text=0)
                ],
                "fonts": [gFont("Regular", 28)],
                "itemHeight": 42}
            </convert>
        </widget>

        <widget name="description" position="60,930" size="1800,40"
            font="Regular;26" halign="center" valign="center"
            foregroundColor="#ffff00" backgroundColor="#050505" />

        <!-- BACKGROUND (desno) -->
        <widget name="background" position="1460,180" size="400,740" alphatest="blend" zPosition="1" />

        <widget name="footer" position="60,950" size="1800,45" font="Regular;28"
            foregroundColor="#ffff00" backgroundColor="#050505" 
            halign="left" valign="center" />

        <widget name="key_red" position="60,1000" size="900,40" font="Bold;28"
            halign="center" valign="center" backgroundColor="#A00000" foregroundColor="#080808" />
        <widget name="key_ok" position="960,1000" size="900,40" font="Bold;28"
            halign="center" valign="center" backgroundColor="#029c84" foregroundColor="#080808" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)

        self["title"] = Label("News")
        self["header"] = Label("Zprávičky | Články | Novinky")
        self["description"] = Label("OK: Open | RED: Back")
        self["key_red"] = Label("Back")
        self["key_ok"] = Label("OK")

        self["background"] = Pixmap()
        self._bg_path = None
        if resolveFilename and SCOPE_PLUGINS:
            self._bg_path = resolveFilename(
                SCOPE_PLUGINS, "Extensions/CiefpParabolaCZ/images/background.png"
            )
        self.onShown.append(self._loadBackground)

        self["list"] = List([
            ("Zprávičky", "zpravicky"),
            ("Články", "clanky"),
            ("Novinky", "novinky"),
        ], enableWrapAround=True)

        self["actions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions"],
            {
                "ok": self.openCategory,
                "cancel": self.close,
                "red": self.close,
                "up": self.up,
                "down": self.down,
            },
            -1
        )

    def _loadBackground(self):
        try:
            if self._bg_path:
                self["background"].instance.setPixmapFromFile(self._bg_path)
                self["background"].show()
        except Exception:
            try:
                self["background"].hide()
            except Exception:
                pass

    def up(self):
        self["list"].selectPrevious()

    def down(self):
        self["list"].selectNext()

    def openCategory(self):
        cur = self["list"].getCurrent()
        if not cur:
            return
        name, typ = cur
        self.session.open(CiefpNewsList, name, typ)

