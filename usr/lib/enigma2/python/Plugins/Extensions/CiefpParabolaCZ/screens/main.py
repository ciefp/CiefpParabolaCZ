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
        tools = [
            ("Clear Cache", "clear_cache"),
            ("Translation settings", "translate_settings")
        ]
        self.session.openWithCallback(self._toolChosen, ChoiceBox, title="Tools", list=tools)

    def _toolChosen(self, choice):
        if not choice:
            return
        
        action = choice[1]
        
        if action == "clear_cache":
            from Screens.MessageBox import MessageBox
            removed = clear_cache()
            self.session.open(MessageBox, "Cache cleared. Files removed.: %d" % removed, MessageBox.TYPE_INFO, timeout=5)
        
        elif action == "translate_settings":
            self._open_translate_settings()

    def _open_translate_settings(self):
        """Otvara podešavanje za prevod"""
        from Plugins.Extensions.CiefpParabolaCZ.components.translator import Translator, SUPPORTED_LANGUAGES
        from Screens.ChoiceBox import ChoiceBox
        from Screens.InputBox import InputBox
        from Screens.MessageBox import MessageBox
        
        translator = Translator()
        
        # Prvi nivo menija
        menu = []
        if not translator.api_key:
            menu.append(("Enter Groq API key", "set_key"))
        else:
            menu.append(("Change Groq API key", "set_key"))
            menu.append(("Test connection", "test"))
            menu.append(("Delete API key", "delete_key"))
        
        menu.append(("Choose a language for translation", "set_lang"))
        menu.append(("Back", "back"))
        
        self.session.openWithCallback(self._translate_menu_callback, ChoiceBox, title="Translation settings", list=menu)
    
    def _translate_menu_callback(self, choice):
        if not choice:
            return
        
        action = choice[1]
        
        if action == "set_key":
            self._set_api_key()
        elif action == "test":
            self._test_connection()
        elif action == "delete_key":
            self._delete_api_key()
        elif action == "set_lang":
            self._set_language()
        # else "back" - samo se vrati
    
    def _set_api_key(self):
        from Plugins.Extensions.CiefpParabolaCZ.components.translator import Translator
        from Screens.InputBox import InputBox
        
        translator = Translator()
        self.session.openWithCallback(
            self._save_api_key,
            InputBox,
            title="Enter Groq API key",
            text=translator.api_key
        )
    
    def _save_api_key(self, api_key):
        if api_key:
            from Plugins.Extensions.CiefpParabolaCZ.components.translator import Translator
            from Screens.MessageBox import MessageBox
            
            translator = Translator()
            if translator.save_api_key(api_key):
                self.session.open(MessageBox, "✓ API key saved!", MessageBox.TYPE_INFO, timeout=3)
            else:
                self.session.open(MessageBox, "✗ Error saving API key!", MessageBox.TYPE_ERROR, timeout=3)

    def _test_connection(self):
        from Plugins.Extensions.CiefpParabolaCZ.components.translator import Translator
        from Screens.MessageBox import MessageBox

        translator = Translator()
        success, message = translator.test_connection()  # ← Ovo vraća (bool, string)

        if success:
            self.session.open(MessageBox, "✓ " + message, MessageBox.TYPE_INFO, timeout=5)
        else:
            self.session.open(MessageBox, "✗ " + message, MessageBox.TYPE_ERROR, timeout=5)

    def _delete_api_key(self):
        from Screens.MessageBox import MessageBox
        
        self.session.openWithCallback(
            self._delete_confirmed,
            MessageBox,
            "Are you sure you want to delete the API key?",
            MessageBox.TYPE_YESNO
        )
    
    def _delete_confirmed(self, confirmed):
        if confirmed:
            from Screens.MessageBox import MessageBox
            import os
            
            try:
                config_path = "/etc/enigma2/ciefp_translate.conf"
                if os.path.exists(config_path):
                    os.remove(config_path)
                self.session.open(MessageBox, "✓ API key has been deleted.", MessageBox.TYPE_INFO, timeout=3)
            except Exception as e:
                self.session.open(MessageBox, "✗ Error while deleting: " + str(e), MessageBox.TYPE_ERROR, timeout=3)
    
    def _set_language(self):
        from Plugins.Extensions.CiefpParabolaCZ.components.translator import SUPPORTED_LANGUAGES
        from Screens.ChoiceBox import ChoiceBox
        
        self.session.openWithCallback(
            self._save_language,
            ChoiceBox,
            title="Select a language for translation",
            list=SUPPORTED_LANGUAGES
        )
    
    def _save_language(self, choice):
        if choice:
            from Screens.MessageBox import MessageBox
            
            lang_code = choice[1]
            try:
                config_path = "/etc/enigma2/ciefp_language.conf"
                with open(config_path, "w") as f:
                    f.write(lang_code)
                self.session.open(MessageBox, "✓ The language has been preserved!", MessageBox.TYPE_INFO, timeout=3)
            except Exception as e:
                self.session.open(MessageBox, "✗ Error saving language: " + str(e), MessageBox.TYPE_ERROR, timeout=3)