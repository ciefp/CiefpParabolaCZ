# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap  

from ..components.constants import PACKAGES
from .package_channels import CiefpPackageChannels

try:
    from Tools.Directories import resolveFilename, SCOPE_PLUGINS
except Exception:
    resolveFilename = None
    SCOPE_PLUGINS = None


class CiefpPackagesList(Screen):
    skin = """
    <screen name="CiefpPackagesList" position="center,center" size="1920,1080" title="CZ/SK Packages" flags="wfNoBorder">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#040030" zPosition="-10" />

        <widget name="title" render="Label" position="100,80" size="1720,60" font="Regular;34"
            halign="center" valign="center" foregroundColor="#ffff00" backgroundColor="#050505" zPosition="2" />

        <widget name="menu" position="100,150" size="1300,780" font="Regular;28" itemHeight="38"
            halign="left" valign="center" foregroundColor="#ffffff" backgroundColor="#1a1a1a" scrollbarMode="showOnDemand" />

        <widget name="description" render="Label" position="100,950" size="1720,40" font="Regular;26"
            halign="left" valign="center" foregroundColor="#ffff00" backgroundColor="#050505" />

        <!-- BACKGROUND (desno) -->
        <widget name="background" position="1420,150" size="400,780" alphatest="blend" zPosition="1" />

        <widget name="key_red" position="100,1000" size="860,40" font="Bold;26"
            halign="center" valign="center" foregroundColor="#080808" backgroundColor="#a00000" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/red.png" position="100,1000" size="860,40" alphatest="blend" zPosition="1" />

        <widget name="key_green" position="960,1000" size="860,40" font="Bold;26"
            halign="center" valign="center" foregroundColor="#080808" backgroundColor="#00a000" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/green.png" position="960,1000" size="860,40" alphatest="blend" zPosition="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)

        self["title"] = Label("CZ/SK Packages")
        self["description"] = Label("OK: Open package | RED: Back")

        self["menu"] = MenuList([p[0] for p in PACKAGES])
        self["key_red"] = Label("Back")
        self["key_green"] = Label("Select")

        self["background"] = Pixmap() 

        self._bg_path = None
        if resolveFilename and SCOPE_PLUGINS:
            self._bg_path = resolveFilename(
                SCOPE_PLUGINS,
                "Extensions/CiefpParabolaCZ/images/background.png"
            )

        # učitaj pixmap tek kad je screen “na ekranu”
        self.onShown.append(self._loadBackground)

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "cancel": self.close,
                "red": self.close,
                "green": self.ok,
                "ok": self.ok,
                "up": self.up,
                "down": self.down,
            },
            -1,
        )

    def _loadBackground(self):
        try:
            if self._bg_path:
                self["background"].instance.setPixmapFromFile(self._bg_path)
                self["background"].show()
        except Exception:
            # ako pukne, samo sakrij, da ne ruši screen
            try:
                self["background"].hide()
            except Exception:
                pass

    def up(self):
        self["menu"].up()

    def down(self):
        self["menu"].down()

    def ok(self):
        idx = self["menu"].getSelectionIndex()
        name, url = PACKAGES[idx]
        self.session.open(CiefpPackageChannels, name, url)
