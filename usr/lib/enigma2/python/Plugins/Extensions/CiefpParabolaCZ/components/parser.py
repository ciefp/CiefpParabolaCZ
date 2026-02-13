# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import re

try:
    # py3
    from html import unescape
except Exception:
    # py2
    try:
        from HTMLParser import HTMLParser
        unescape = HTMLParser().unescape
    except Exception:
        def unescape(x): return x

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

def strip_tags(s):
    if not s:
        return ""
    s = _TAG_RE.sub("", s)
    s = unescape(s)
    s = s.replace("\xa0", " ")
    s = _WS_RE.sub(" ", s).strip()
    return s

def _extract_table(html, class_name):
    # uzmi prvi <table ... class='...'> ili class="..."
    # parabola.cz koristi uglavnom jednostruke navodnike
    pat = re.compile(
        r"<table[^>]*class=(?:\"|')([^>]*?%s[^>]*?)(?:\"|')[^>]*>.*?</table>" % re.escape(class_name),
        re.IGNORECASE | re.DOTALL
    )
    m = pat.search(html)
    return m.group(0) if m else ""


def _extract_rows(table_html):
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.IGNORECASE | re.DOTALL)
    return rows

def _extract_cells(row_html):
    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, flags=re.IGNORECASE | re.DOTALL)
    return [strip_tags(c) for c in cells]

def parse_satellite_overview(html_bytes):
    """
    /prehledy/televize-digital/<pos>/
    očekuje: <table class="tabulka_v01">
    vraća list[dict] sa poljima:
      name,freq,pol,genre,lang,sr,fec,norma,mod,ca
    """
    try:
        html = html_bytes.decode("windows-1250", "ignore")
    except Exception:
        try:
            html = html_bytes.decode("utf-8", "ignore")
        except Exception:
            html = str(html_bytes)

    table = _extract_table(html, "tabulka_v01")
    if not table:
        return []

    rows = _extract_rows(table)
    items = []
    for r in rows:
        # preskoči header
        if "<th" in r.lower():
            continue
        cells = _extract_cells(r)
        # očekujemo bar 10-11 kolona (stanice, par, frekv, pol, žánr, jazyk, SR, FEC, norma, modulace, CA)
        if len(cells) < 9:
            continue
        # mapiranje po indeksu (parabola struktura)
        # 0 stanice, 1 par, 2 frekv, 3 pol, 4 žánr, 5 jazyk, 6 SR, 7 FEC, 8 norma, 9 modulace, 10 CA
        item = {
            "name": cells[0],
            "freq": cells[2] if len(cells) > 2 else "",
            "pol":  cells[3] if len(cells) > 3 else "",
            "genre": cells[4] if len(cells) > 4 else "",
            "lang": cells[5] if len(cells) > 5 else "",
            "sr": cells[6] if len(cells) > 6 else "",
            "fec": cells[7] if len(cells) > 7 else "",
            "norma": cells[8] if len(cells) > 8 else "",
            "mod": cells[9] if len(cells) > 9 else "",
            "ca": cells[10] if len(cells) > 10 else "",
        }
        items.append(item)
    return items

def parse_package_channels(html_bytes):
    """
    /cz-sk/skylink/  (i slične)
    očekuje: <table class="vysilace_vysilace tablesorter">
    vraća list[dict] sa poljima:
      program, genre, lang, sat, kmitpol, sr, fec, norma, mod, provider, kod
    (logo se preskače za start)
    """
    try:
        html = html_bytes.decode("windows-1250", "ignore")
    except Exception:
        try:
            html = html_bytes.decode("utf-8", "ignore")
        except Exception:
            html = str(html_bytes)

    table = _extract_table(html, "tablesorter")
    if not table:
        # fallback: bez tablesorter (nekad je samo vysilace_vysilace)
        table = _extract_table(html, "vysilace_vysilace")
    if not table:
        return []

    rows = _extract_rows(table)
    items = []
    for r in rows:
        if "<th" in r.lower():
            continue
        # preskoči service-id redove: obično <td colspan="...">service ID...
        if "colspan" in r.lower() and "service id" in r.lower():
            continue
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.IGNORECASE | re.DOTALL)
        if not cells:
            continue

        # logo je prva kolona, ostale su polja
        texts = [strip_tags(c) for c in cells]
        # očekujemo oko 12 kolona (logo + 11)
        if len(texts) < 10:
            continue

        # Indeksi (po parabola header-u):
        # 0 logo, 1 program, 2 žánr, 3 jazyk, 4 satelit, 5 kmit/pol, 6 SR, 7 FEC, 8 norma, 9 modulace, 10 poskytovatel, 11 kód
        item = {
            "program": texts[1] if len(texts) > 1 else "",
            "genre": texts[2] if len(texts) > 2 else "",
            "lang": texts[3] if len(texts) > 3 else "",
            "sat": texts[4] if len(texts) > 4 else "",
            "kmitpol": texts[5] if len(texts) > 5 else "",
            "sr": texts[6] if len(texts) > 6 else "",
            "fec": texts[7] if len(texts) > 7 else "",
            "norma": texts[8] if len(texts) > 8 else "",
            "mod": texts[9] if len(texts) > 9 else "",
            "provider": texts[10] if len(texts) > 10 else "",
            "kod": texts[11] if len(texts) > 11 else "",
        }
        # filtriraj prazne redove
        if item["program"]:
            items.append(item)

    return items

def parse_last_update(html_bytes):
    try:
        html = html_bytes.decode("windows-1250", "ignore")
    except Exception:
        html = str(html_bytes)
    m = re.search(r"Posledn[ií]\s+aktualizace:\s*([^<]+)", html, flags=re.IGNORECASE)
    return strip_tags(m.group(1)) if m else ""
