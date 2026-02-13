# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import time
import hashlib

try:
    # py3
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    # py2
    from urllib2 import Request, urlopen, URLError, HTTPError

from .constants import TMP_DIR


def _ensure_tmp():
    try:
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)
    except Exception:
        pass


def _cache_path(url):
    h = hashlib.md5(url.encode('utf-8')).hexdigest()
    return os.path.join(TMP_DIR, h + ".html")


def fetch_url(url, cache_ttl_sec=6 * 60 * 60, user_agent="Mozilla/5.0 (Enigma2) CiefpParabolaCZ/1.0"):
    """
    Jednostavan GET sa cache-om.
    - Ako cache postoji i nije istekao TTL, vraća cache.
    - Ako mreža pukne, vraća poslednji cache (ako postoji).
    """
    _ensure_tmp()
    path = _cache_path(url)

    now = int(time.time())
    try:
        if os.path.exists(path):
            age = now - int(os.path.getmtime(path))
            if age <= int(cache_ttl_sec):
                with open(path, "rb") as f:
                    return f.read(), True, None
    except Exception:
        pass

    try:
        req = Request(url, headers={"User-Agent": user_agent, "Accept": "text/html,*/*"})
        data = urlopen(req, timeout=15).read()
        try:
            with open(path, "wb") as f:
                f.write(data)
        except Exception:
            pass
        return data, False, None
    except (HTTPError, URLError, Exception) as e:
        # fallback na cache ako postoji
        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read(), True, e
        except Exception:
            pass
        return b"", False, e


def clear_cache():
    _ensure_tmp()
    removed = 0
    try:
        for fn in os.listdir(TMP_DIR):
            if fn.endswith(".html"):
                try:
                    os.remove(os.path.join(TMP_DIR, fn))
                    removed += 1
                except Exception:
                    pass
    except Exception:
        pass
    return removed
