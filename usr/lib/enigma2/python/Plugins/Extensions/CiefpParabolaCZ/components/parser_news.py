# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import re
import html as ihtml


def _to_text(data):
    """
    Enigma fetcher nekad vrati bytes, nekad str, a nekad tuple (data, headers) ili (data, code).
    Ovde sve svodimo na unicode string.
    """
    if data is None:
        return ""

    # ako je tuple/list: uzmi prvi element (najčešće raw html)
    if isinstance(data, (tuple, list)) and data:
        data = data[0]

    if isinstance(data, bytes):
        return data.decode("utf-8", "ignore")

    if isinstance(data, str):
        return data

    # fallback
    try:
        return str(data)
    except Exception:
        return ""


def _strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return ihtml.unescape(s).strip()


def _short_date_from_cz_datetime(dt):
    """
    Ulaz npr: '11.02.2026 12:32'
    Izlaz: '11/2'
    """
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", dt or "")
    if not m:
        return ""
    d = int(m.group(1))
    mo = int(m.group(2))
    return "%d/%d" % (d, mo)


def parse_news_list(html_data, typ):
    """
    Vraca listu item-a:
      {"date": "11/2", "title": "...", "desc": "...", "url": "..."}
    """
    html = _to_text(html_data)
    if not html:
        return []

    items = []

    # -------------------------
    # NOVINKY (rubrika satelitske promene)
    # -------------------------
    if typ == "novinky":
        # Parabola "Novinky na satelitech" blokovi su:
        # <div class="h5">11/2: ....</div>
        # <div class="novinky">opis...</div>
        blocks = re.findall(
            r'<div class="h5">(.*?)</div>\s*<div class="novinky">(.*?)</div>',
            html,
            re.S | re.I,
        )
        for h5, body in blocks:
            h5_txt = _strip_tags(h5)
            body_txt = _strip_tags(body)

            # h5 obično počinje sa "11/2:" ili "11/2 -"
            d = ""
            m = re.match(r"^\s*(\d{1,2}/\d{1,2})\s*[:\-]\s*(.*)$", h5_txt)
            if m:
                d = m.group(1).strip()
                title = m.group(2).strip()
            else:
                title = h5_txt.strip()

            items.append(
                {
                    "date": d,
                    "title": title,
                    "desc": body_txt,
                    "url": "",  # novinky liste nemaju direkt link po stavci
                }
            )
        return items

    # -------------------------
    # ZPRÁVIČKY / ČLÁNKY
    # (u HTML-u su tipično: <h2><a href='...'>Naslov</a></h2> DATUM ... <br> perex ... <p class='pocet_komentaru'>...)
    # -------------------------
    # primer iz tvojih fajlova:
    # <h2><a href='/zpravicky/40944/.../'>Neki naslov</a></h2>
    # 12.02.2026 17:25 <span class='...'>DNES!</span><br>
    # opis...
    # <p class='pocet_komentaru'>...

    pattern = (
        r"<h2>\s*<a\s+href=['\"](?P<url>[^'\"]+)['\"][^>]*>\s*(?P<title>.*?)\s*</a>\s*</h2>\s*"
        r"(?P<dt>\d{1,2}\.\d{1,2}\.\d{4}\s+\d{1,2}:\d{2}).*?<br\s*/?>\s*"
        r"(?P<desc>.*?)(?:<p\s+class=['\"]pocet_komentaru['\"]|<div\s+class=['\"]clear_both['\"])"
    )

    for m in re.finditer(pattern, html, re.S | re.I):
        url = m.group("url").strip()
        title = _strip_tags(m.group("title"))
        dt = m.group("dt").strip()
        desc = _strip_tags(m.group("desc"))

        # kompletan URL
        if url.startswith("/"):
            full_url = "https://www.parabola.cz" + url
        else:
            full_url = url

        items.append(
            {
                "date": _short_date_from_cz_datetime(dt),
                "title": title,
                "desc": desc,
                "url": full_url,
            }
        )

    return items

def parse_news_detail(html):
    html = _to_text(html)
    if not html:
        return {"text": "Nije pronađen tekst članka.", "image": None}

    # 1) pokušaj izvući og:image (najčešće cover)
    img = None
    mimg = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        html, re.I
    )
    if mimg:
        img = mimg.group(1).strip()

    # 2) ako nema og:image, uzmi prvu sliku iz article/text bloka
    if not img:
        mblock = re.search(r'<div[^>]+class=["\']text["\'][^>]*>(.*?)</div>', html, re.S | re.I)
        block = mblock.group(1) if mblock else html
        mimg2 = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', block, re.I)
        if mimg2:
            img = mimg2.group(1).strip()

    # normalizuj relativni URL
    if img and img.startswith("/"):
        img = "https://www.parabola.cz" + img

    # --- tekst (kao što već radi) ---
    m = re.search(r'<div[^>]+class=["\']text["\'][^>]*>(.*?)</div>', html, re.S | re.I)
    if not m:
        m = re.search(r'<article.*?>(.*?)</article>', html, re.S | re.I)
    if not m:
        return {"text": "Nije pronađen tekst članka.", "image": img}

    content = m.group(1)
    content = re.sub(r'<script.*?</script>', '', content, flags=re.S | re.I)
    content = re.sub(r'<style.*?</style>', '', content, flags=re.S | re.I)
    content = re.sub(r'<br\s*/?>', '\n', content, flags=re.I)
    content = re.sub(r'</p>', '\n\n', content, flags=re.I)
    content = re.sub(r'<[^>]+>', ' ', content)
    content = ihtml.unescape(content)
    content = re.sub(r'\n\s*\n+', '\n\n', content)

    return {"text": content.strip(), "image": img}
