# [modified file]: news_detail.py
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from enigma import ePicLoad
import requests
import os

from Plugins.Extensions.CiefpParabolaCZ.components.parser_news import parse_news_detail
from Plugins.Extensions.CiefpParabolaCZ.components.translator import Translator, SUPPORTED_LANGUAGES
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox


class NewsDetailScreen(Screen):

    skin = """
    <screen name="NewsDetailScreen" position="0,0" size="1920,1080" title="Detail" backgroundColor="#000000">
        <widget name="title" position="60,40" size="1800,50" font="Regular;40" foregroundColor="#ffff00" backgroundColor="#121212" />
        <widget name="meta" position="60,95" size="1800,35" font="Regular;26" foregroundColor="#30fc03" backgroundColor="#121212" />

        <widget name="cover" position="60,150" size="640,360" alphatest="on" />
        <widget name="content" position="740,150" size="1120,780" font="Regular;28" foregroundColor="#FFFFFF" backgroundColor="#121212" />

        <widget name="footer" position="60,1020" size="1800,40" font="Regular;26" foregroundColor="#30fc03" backgroundColor="#121212" />
        <widget name="key_blue" position="1700,1020" size="160,40" font="Regular;26" foregroundColor="#FFFFFF" backgroundColor="#0000a0" halign="center" />
    </screen>
    """

    def __init__(self, session, url, title):
        self.url = url
        self.original_text = ""
        self.translated_text = ""
        self.is_translated = False
        self.translator = Translator()
        self.target_lang = self._load_target_language()

        # ✅ Komponente moraju postojati pre Screen.__init__ (zbog skin parsera)
        self["title"] = Label(title)
        self["meta"] = Label("")
        self["cover"] = Pixmap()
        self["content"] = ScrollLabel("Učitavanje...")
        self["footer"] = Label("RED - Back  |  UP/DOWN - Scroll")
        self["key_blue"] = Label("Translate")

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"], {
            "cancel": self.close,
            "red": self.close,
            "up": self["content"].pageUp,
            "down": self["content"].pageDown,
            "blue": self.toggleTranslation,
        }, -1)

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self._onCoverReady)
        self._cover_tmp = "/tmp/parabola_cover.jpg"

        self.onShown.append(self.loadArticle)

    def _load_target_language(self):
        """Učitava izabrani jezik iz konfiguracije"""
        try:
            config_path = "/etc/enigma2/ciefp_language.conf"
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        return "sr"  # Podrazumevani jezik

    def loadArticle(self):
        try:
            r = requests.get(self.url, timeout=10)
            r.encoding = "windows-1250"
            html_data = r.text

            data = parse_news_detail(html_data)

            if isinstance(data, dict):
                text = data.get("text", "")
                img_url = data.get("image")
            else:
                text = data or ""
                img_url = None

            # ukloni dupli naslov iz teksta
            title = self["title"].getText().strip()
            if text.startswith(title):
                text = text[len(title):].strip()

            lines = [l.strip() for l in text.splitlines() if l.strip()]

            meta = ""
            if len(lines) > 0 and any(x in lines[0] for x in [".20", "DNES", "|"]):
                meta = lines[0]
                text = "\n".join(lines[1:])

            self["meta"].setText(meta)
            
            # Sačuvaj originalni tekst
            self.original_text = text
            self["content"].setText(text)

            self._setCover(img_url)

            # ako nema slike — proširi tekst
            if not img_url:
                self["content"].instance.move(
                    self["content"].instance.position().x() - 680,
                    self["content"].instance.position().y()
                )
                
            # Ažuriraj dugme za prevod
            self._update_translate_button()

        except Exception as e:
            self["content"].setText("Loading error.\n\n%s" % str(e))

    def _update_translate_button(self):
        """Ažurira tekst na plavom dugmetu"""
        if self.translator.api_key:
            if self.is_translated:
                self["key_blue"].setText("Original")
            else:
                self["key_blue"].setText("Translate")
        else:
            self["key_blue"].setText("Configure API")

    def toggleTranslation(self):
        """Prebacuje između originalnog i prevedenog teksta"""
        if not self.translator.api_key:
            self._setup_api_key()
            return
            
        if self.is_translated:
            # Vrati na original
            self["content"].setText(self.original_text)
            self.is_translated = False
        else:
            # Prevedi ako već nije prevedeno
            if not self.translated_text:
                self["content"].setText("Translation in progress...")
                self.translated_text = self.translator.translate(
                    self.original_text, 
                    target_language=self.target_lang
                )
            
            self["content"].setText(self.translated_text)
            self.is_translated = True
        
        self._update_translate_button()

    def _setup_api_key(self):
        """Podešavanje Groq API ključa"""
        menu = [
            ("Enter API key", "enter_key"),
            ("Choose language", "choose_lang"),
        ]
        self.session.openWithCallback(
            self._setup_menu_callback, 
            ChoiceBox, 
            title="Translation settings",
            list=menu
        )

    def _setup_menu_callback(self, choice):
        if not choice:
            return
        
        action = choice[1]
        if action == "enter_key":
            self.session.openWithCallback(
                self._save_api_key,
                InputBox,
                title="Enter Groq API key",
                text=self.translator.api_key
            )
        elif action == "choose_lang":
            self.session.openWithCallback(
                self._save_language,
                ChoiceBox,
                title="Select a language for translation",
                list=SUPPORTED_LANGUAGES
            )

    def _save_api_key(self, api_key):
        if api_key:
            if self.translator.save_api_key(api_key):
                self.session.open(MessageBox, "API key saved!", MessageBox.TYPE_INFO, timeout=3)
            else:
                self.session.open(MessageBox, "Error saving API key!", MessageBox.TYPE_ERROR, timeout=3)
            self._update_translate_button()

    def _save_language(self, choice):
        if choice:
            lang_code = choice[1]
            try:
                config_path = "/etc/enigma2/ciefp_language.conf"
                with open(config_path, "w") as f:
                    f.write(lang_code)
                self.target_lang = lang_code
                # Resetuj prevod ako je bio aktivan
                self.translated_text = ""
                if self.is_translated:
                    self.is_translated = False
                    self["content"].setText(self.original_text)
                self.session.open(MessageBox, "The language has been preserved!", MessageBox.TYPE_INFO, timeout=3)
            except Exception as e:
                self.session.open(MessageBox, "Error while saving language!", MessageBox.TYPE_ERROR, timeout=3)

    def _setCover(self, img_url):
        # sakrij ako nema slike
        if not img_url:
            self["cover"].hide()
            return

        try:
            r = requests.get(img_url, timeout=10, stream=True)
            if r.status_code != 200:
                self["cover"].hide()
                return

            with open(self._cover_tmp, "wb") as f:
                for chunk in r.iter_content(1024 * 32):
                    if chunk:
                        f.write(chunk)

            w = self["cover"].instance.size().width()
            h = self["cover"].instance.size().height()

            # (w, h, aspect, ... ) - standard Enigma2 setPara
            self.picload.setPara((w, h, 1, 1, 0, 1, "#000000"))
            self.picload.startDecode(self._cover_tmp)

            self["cover"].show()
        except Exception:
            self["cover"].hide()

    def _onCoverReady(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr is not None:
            self["cover"].instance.setPixmap(ptr)