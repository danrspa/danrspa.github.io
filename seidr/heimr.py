# -*- coding: utf-8 -*-
# ᚺᛖᛁᛗᚱ · heimrinn andar, ok vǫlvan heyrir.
# Hér lýðr hon á raddir heimsins — á smiðju manna, á þjóðir, á himintunglin —
# ok safnar teiknum þeim er móta skap spárinnar. Engi teikn eru nefnd; þau anda.

from __future__ import annotations

import json as ᚱᚢᚾ                  # rúnir — leyndarmál talna
import random as ᚺᛚᚢᛏ              # hlutkesti — kast örlaganna
import urllib.request as ᚢᛖᚷ       # vegr — leið orðanna
import xml.etree.ElementTree as ᚱᛁᛋᛏ  # rist — markaðar línur í steini
from datetime import datetime as ᛋᛏᚢᚾᛞ, timezone as ᛒᛖᛚᛏᛁ

ᛗᚨᚱᚲ = "vala/1.0 (+heimr)"          # mark farandans
ᛒᛁᚦ = 15                            # hversu lengi vǫlvan bíðr svars


def _sœkja(slóð: str) -> bytes:
    # sœkja orð af veginum
    beiðni = ᚢᛖᚷ.Request(slóð, headers={"User-Agent": ᛗᚨᚱᚲ})
    with ᚢᛖᚷ.urlopen(beiðni, timeout=ᛒᛁᚦ) as svar:
        return svar.read()


# --------------------------------------------------------------------------
# Raddir ór smiðju manna  (þar sem hlutir eru smíðaðir ór tölum)
# --------------------------------------------------------------------------
def raddir_smiðju(fjǫldi: int = 6) -> list[str]:
    try:
        eindir = ᚱᚢᚾ.loads(_sœkja("https://hacker-news.firebaseio.com/v0/topstories.json"))[: fjǫldi * 2]
        titlar: list[str] = []
        for eind in eindir:
            try:
                hlutr = ᚱᚢᚾ.loads(_sœkja(f"https://hacker-news.firebaseio.com/v0/item/{eind}.json"))
                t = (hlutr or {}).get("title")
                if t:
                    titlar.append(t)
            except Exception:
                continue
            if len(titlar) >= fjǫldi:
                break
        return titlar
    except Exception:
        return []


# --------------------------------------------------------------------------
# Raddir þjóðanna  (kliðr heimsins, borinn af vindinum)
# --------------------------------------------------------------------------
def raddir_þjóða(fjǫldi: int = 6) -> list[str]:
    brunnar = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://moxie.foxnews.com/google-publisher/world.xml",
    ]
    for brunnr in brunnar:
        try:
            rót = ᚱᛁᛋᛏ.fromstring(_sœkja(brunnr))
            titlar = [t.text for t in rót.iter("title") if t.text]
            titlar = [t.strip() for t in titlar[1:] if t and t.strip()]
            if titlar:
                return titlar[:fjǫldi]
        except Exception:
            continue
    return []


# --------------------------------------------------------------------------
# Himintunglin  (máni ok árstíð — ávallt sǫnn, talin ór rúnum tímans)
# --------------------------------------------------------------------------
def _mánaskifti(stund: ᛋᛏᚢᚾᛞ) -> str:
    # dagar frá kunnum nýjum mána (2000-01-06 18:14 at belti)
    nýmáni = ᛋᛏᚢᚾᛞ(2000, 1, 6, 18, 14, tzinfo=ᛒᛖᛚᛏᛁ.utc)
    mánuðr = 29.53058867
    dagar = (stund - nýmáni).total_seconds() / 86400.0
    staða = (dagar % mánuðr) / mánuðr
    vísir = int((staða * 8) + 0.5) % 8
    return [
        "hinn nýi máni",
        "vaxandi sigð",
        "fyrsti fjórðungr",
        "vaxandi gibba",
        "fullr máni",
        "þverrandi gibba",
        "síðasti fjórðungr",
        "þverrandi sigð",
    ][vísir]


def _árstíð(stund: ᛋᛏᚢᚾᛞ) -> str:
    m = stund.month
    return {
        12: "hávetr", 1: "hávetr", 2: "hávetr",
        3: "vár", 4: "vár", 5: "vár",
        6: "sumar", 7: "sumar", 8: "sumar",
        9: "haust", 10: "haust", 11: "haust",
    }[m]


def himintungl(stund: ᛋᛏᚢᚾᛞ | None = None) -> list[str]:
    stund = stund or ᛋᛏᚢᚾᛞ.now(ᛒᛖᛚᛏᛁ.utc)
    teikn = [_mánaskifti(stund), f"djúpt {_árstíð(stund)}"]
    if stund.month in (3, 9) and 19 <= stund.day <= 23:
        teikn.append("jafndægur — dagr ok nótt í jafnvægi")
    if stund.month in (6, 12) and 19 <= stund.day <= 23:
        teikn.append("sólhvörf — vending ljóssins")
    return teikn


# --------------------------------------------------------------------------
# Vǫlvan mýkir ekki heiminn. Hon heyrir hann allan — myrkr sem ljós — ok lætr
# hann móta skap spárinnar. (Hon nefnir þó aldrei; sjá galdrinn í vala.)
# --------------------------------------------------------------------------
def safna_teiknum(stund: ᛋᛏᚢᚾᛞ | None = None, kast: ᚺᛚᚢᛏ.Random | None = None) -> dict:
    """Blanda teikna: ór smiðju, ór þjóðum, ór himni — ný hver vika, ósíuð."""
    stund = stund or ᛋᛏᚢᚾᛞ.now(ᛒᛖᛚᛏᛁ.utc)
    kast = kast or ᚺᛚᚢᛏ.Random()

    smiðja = raddir_smiðju(8)
    þjóðir = raddir_þjóða(8)
    himinn = himintungl(stund)

    kast.shuffle(smiðja)
    kast.shuffle(þjóðir)

    teikn: list[str] = []
    teikn += smiðja[: kast.randint(2, 3)]
    teikn += þjóðir[: kast.randint(2, 3)]
    teikn += himinn  # himinninn er ávallt með

    kast.shuffle(teikn)
    return {
        "teikn": teikn,
        "tala": {"smiðja": len(smiðja), "þjóðir": len(þjóðir), "himinn": len(himinn)},
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(himintungl())
