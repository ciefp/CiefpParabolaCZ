# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap

try:
    from Tools.Directories import resolveFilename, SCOPE_PLUGINS
except Exception:
    resolveFilename = None
    SCOPE_PLUGINS = None

from ..components.constants import SATELLITES, NEWS_CHOICES
from .satellite_list import CiefpSatellitesList
from .packages import CiefpPackagesList
from ..components.fetcher import clear_cache
from .news_hub import CiefpNewsHub



class CiefpParabolaCZMain(Screen):
    skin = """
    <screen name="CiefpParabolaCZMain" position="center,center" size="1920,1080" title="CiefpParabolaCZ - Parabola.CZ Viewer" flags="wfNoBorder">
        <!-- PANEL -->
        <eLabel position="0,0" size="1920,1080" backgroundColor="#040030" zPosition="-10" />
        <!-- TITLE -->
        <widget name="title" position="100,80" size="1720,60" font="Regular;34" halign="center" valign="center" foregroundColor="#ffff00" backgroundColor="#050505" zPosition="2" />
        <widget name="menu" position="100,150" size="1300,780" font="Regular;28" itemHeight="39" halign="left"  valign="center" foregroundColor="#ffffff" backgroundColor="#1a1a1a" scrollbarMode="showOnDemand" />
        <widget name="description" position="100,950" size="1720,40" font="Regular;26" halign="left"  valign="center" foregroundColor="#ffff00" backgroundColor="#050505" />

        <!-- BACKGROUND (desno) -->
        <widget name="background" position="1420,150" size="400,780" alphatest="on" zPosition="1" />

        <!-- KEYs -->
        <widget name="key_red" position="100,1000" size="430,40" font="Bold;28" halign="center" valign="center" foregroundColor="#080808" backgroundColor="#a00000" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/red.png" position="100,1000" size="430,40" alphatest="blend" zPosition="1" />

        <widget name="key_green" position="530,1000" size="430,40" font="Bold;28" halign="center" valign="center" foregroundColor="#080808" backgroundColor="#00a000" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/green.png" position="530,1000" size="430,40" alphatest="blend" zPosition="1" />

        <widget name="key_yellow" position="960,1000" size="430,40" font="Bold;28" halign="center" valign="center" foregroundColor="#080808" backgroundColor="#a09d00" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/yellow.png" position="960,1000" size="430,40" alphatest="blend" zPosition="1" />

        <widget name="key_blue" position="1390,1000" size="430,40" font="Bold;28" halign="center" valign="center" foregroundColor="#080808" backgroundColor="#0000a0" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/blue.png" position="1390,1000" size="430,40" alphatest="blend" zPosition="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)

        self["title"] = Label("CiefpParabolaCZ - Parabola.cz Viewer")
        self["description"] = Label("OK: Satellite list | GREEN: CZ/SK Packages | YELLOW: News | BLUE: Tools")
        self["menu"] = MenuList([s[0] for s in SATELLITES])

        self._bg_path = None
        try:
            self["background"] = Pixmap()
            if resolveFilename and SCOPE_PLUGINS:
                self._bg_path = resolveFilename(SCOPE_PLUGINS, "Extensions/CiefpParabolaCZ/images/background.png")
        except Exception:
            pass

        self.onLayoutFinish.append(self._applyBackground)


        self["key_red"] = Label("Exit")
        self["key_green"] = Label("CZ/SK Packages")
        self["key_yellow"] = Label("News")
        self["key_blue"] = Label("Tools")

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok": self.ok,
                "cancel": self.close,
                "red": self.close,
                "green": self.openPackages,
                "yellow": self.openNews,
                "blue": self.openTools,
                "up": self.up,
                "down": self.down,
            },
            -1,
        )


    def _applyBackground(self):
        if not self._bg_path:
            return
        try:
            self["background"].instance.setPixmapFromFile(self._bg_path)
        except Exception:
            try:
                self["background"].setPixmapFromFile(self._bg_path)
            except Exception:
                pass

    def up(self):
        self["menu"].up()

    def down(self):
        self["menu"].down()

    def ok(self):
        idx = self["menu"].getSelectionIndex()
        name, url = SATELLITES[idx]
        self.session.open(CiefpSatellitesList, name, url)

    def openPackages(self):
        self.session.open(CiefpPackagesList)

    def openNews(self):
        self.session.open(CiefpNewsHub)

    def openTools(self):
        tools = [("Clear Cache", "clear_cache")]
        self.session.openWithCallback(self._toolChosen, ChoiceBox, title="Tools", list=tools)

    def _toolChosen(self, choice):
        if not choice:
            return
        action = choice[1]
        from Screens.MessageBox import MessageBox
        if action == "clear_cache":
            removed = clear_cache()
            self.session.open(MessageBox, "Cache obrisan. Uklonjeno fajlova: %d" % removed, MessageBox.TYPE_INFO, timeout=5)
