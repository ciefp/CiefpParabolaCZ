from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from enigma import ePicLoad
import requests
import os

from Plugins.Extensions.CiefpParabolaCZ.components.parser_news import parse_news_detail


class NewsDetailScreen(Screen):

    skin = """
    <screen name="NewsDetailScreen" position="0,0" size="1920,1080" title="Detail" backgroundColor="#000000">
        <widget name="title" position="60,40" size="1800,50" font="Regular;40" foregroundColor="#ffff00" backgroundColor="#121212" />
        <widget name="meta" position="60,95" size="1800,35" font="Regular;26" foregroundColor="#30fc03" backgroundColor="#121212" />

        <widget name="cover" position="60,150" size="640,360" alphatest="on" />
        <widget name="content" position="740,150" size="1120,780" font="Regular;28" foregroundColor="#FFFFFF" backgroundColor="#121212" />

        <widget name="footer" position="60,1020" size="1800,40" font="Regular;26" foregroundColor="#30fc03" backgroundColor="#121212" />
    </screen>
    """

    def __init__(self, session, url, title):
        self.url = url

        # ✅ Komponente moraju postojati pre Screen.__init__ (zbog skin parsera)
        self["title"] = Label(title)
        self["meta"] = Label("")
        self["cover"] = Pixmap()
        self["content"] = ScrollLabel("Učitavanje...")
        self["footer"] = Label("RED - Back  |  UP/DOWN - Scroll")

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"], {
            "cancel": self.close,
            "red": self.close,
            "up": self["content"].pageUp,
            "down": self["content"].pageDown,
        }, -1)

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self._onCoverReady)
        self._cover_tmp = "/tmp/parabola_cover.jpg"

        self.onShown.append(self.loadArticle)

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
            self["content"].setText(text)

            self._setCover(img_url)

            # ako nema slike — proširi tekst
            if not img_url:
                self["content"].instance.move(
                    self["content"].instance.position().x() - 680,
                    self["content"].instance.position().y()
                )

        except Exception as e:
            self["content"].setText("Greška pri učitavanju.\n\n%s" % str(e))

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

