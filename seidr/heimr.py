# -*- coding: utf-8 -*-
# ᚺᛖᛁᛗᚱ · heimrinn andar, ok vǫlvan heyrir.
# Hon lýðr á raddir heimsins — á smiðju manna, á þjóðir norðrs ok suðrs, á þá
# sem standa utan hallar, á himintunglin — ok vegr ór þeim SKAP, eigi ORÐ.
#
# Hér er hin harða regla: ekkert hrátt orð heimsins fer til vǫlvunnar. Hon fær
# tǫlur einar — hita ok þunga ok ljós. Nefni hon engan atburð, þá er þat eigi
# af því at hon var beðin þess, heldr af því at hon sá hann aldri.

from __future__ import annotations

import json as ᚱᚢᚾ                  # rúnir — leyndarmál talna
import random as ᚺᛚᚢᛏ              # hlutkesti — kast örlaganna
import re as ᛚᛖᛁᛏ                   # leit — mynstr í orðum
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
def raddir_smiðju(fjǫldi: int = 8) -> list[str]:
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
# Brunnar þjóðanna  (eigi hallarinnar einnar — norðrit ok jaðarinn með)
# --------------------------------------------------------------------------
BRUNNAR_ÞJÓÐA = [
    # norðrit — hit kalda land sem kvæðit talar um
    ("https://www.icelandreview.com/feed/", "norðr"),
    ("https://www.nrk.no/toppsaker.rss", "norðr"),
    ("https://www.thelocal.se/feeds/rss.php", "norðr"),
    # heimrinn — tvær raddir, eigi ein
    ("https://feeds.bbci.co.uk/news/world/rss.xml", "heimr"),
    ("https://www.aljazeera.com/xml/rss/all.xml", "heimr"),
    # jaðarrinn — þeir sem standa utan hallar
    ("https://freedomnews.org.uk/feed/", "jaðarr"),
    ("https://crimethinc.com/feed", "jaðarr"),
]

ᚨᛏᛟᛗ = "{http://www.w3.org/2005/Atom}"


def _greinar(slóð: str) -> list[str]:
    """Titlar greinanna einna.

    Áðr var hér  titlar[1:]  — ok þá laust heiti brunnsins sjálfs inn sem teikn
    ('BBC News'), því at sumir brunnar bera heiti sitt tvisvar (rás ok mynd).
    Nú er gengit um <item>/<entry> ok tekinn beinn titill hvers — engi rásartitill."""
    rót = ᚱᛁᛋᛏ.fromstring(_sœkja(slóð))
    út: list[str] = []
    for eind in rót.iter("item"):
        t = eind.find("title")
        if t is not None and t.text and t.text.strip():
            út.append(t.text.strip())
    if not út:
        for eind in rót.iter(ᚨᛏᛟᛗ + "entry"):
            t = eind.find(ᚨᛏᛟᛗ + "title")
            if t is not None and t.text and t.text.strip():
                út.append(t.text.strip())
    return út


def raddir_þjóða(fjǫldi: int = 8, kast: ᚺᛚᚢᛏ.Random | None = None) -> list[str]:
    """Áðr tók hon ór fyrsta brunni sem svaraði — ok þat var ávallt hinn sami.
    Nú blandar hon ór ǫllum þeim er svara, svá at engi ein rǫdd ræðr skapinu."""
    kast = kast or ᚺᛚᚢᛏ.Random()
    safn: list[str] = []
    brunnar = list(BRUNNAR_ÞJÓÐA)
    kast.shuffle(brunnar)
    for slóð, _kyn in brunnar:
        try:
            greinar = _greinar(slóð)
        except Exception:
            continue
        kast.shuffle(greinar)
        safn += greinar[:3]
    kast.shuffle(safn)
    return safn[:fjǫldi]


# --------------------------------------------------------------------------
# Himintunglin  (máni ok árstíð — ávallt sǫnn, talin ór rúnum tímans)
# --------------------------------------------------------------------------
def _mánastaða(stund: ᛋᛏᚢᚾᛞ) -> float:
    """Staða mánans í hring sínum, 0.0 (nýr) … 1.0 (nýr aptr)."""
    nýmáni = ᛋᛏᚢᚾᛞ(2000, 1, 6, 18, 14, tzinfo=ᛒᛖᛚᛏᛁ.utc)
    dagar = (stund - nýmáni).total_seconds() / 86400.0
    return (dagar % 29.53058867) / 29.53058867


def _mánaskifti(stund: ᛋᛏᚢᚾᛞ) -> str:
    vísir = int((_mánastaða(stund) * 8) + 0.5) % 8
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


ᛗᚨᚾᚢᚦᛁᚱ = [
    "janúar", "febrúar", "marz", "apríl", "maí", "júní",
    "júlí", "ágúst", "september", "október", "nóvember", "desember",
]


def árstíð_heiti(stund: ᛋᛏᚢᚾᛞ | None = None) -> str:
    """Hin sanna árstíð, sǫgð berum orðum — svá at vǫlvan yrki eigi vetr í júlí."""
    stund = stund or ᛋᛏᚢᚾᛞ.now(ᛒᛖᛚᛏᛁ.utc)
    return f"{_árstíð(stund)} ({ᛗᚨᚾᚢᚦᛁᚱ[stund.month - 1]}, norðrhvel)"


def himintungl(stund: ᛋᛏᚢᚾᛞ | None = None) -> list[str]:
    stund = stund or ᛋᛏᚢᚾᛞ.now(ᛒᛖᛚᛏᛁ.utc)
    teikn = [_mánaskifti(stund), f"djúpt {_árstíð(stund)}"]
    if stund.month in (3, 9) and 19 <= stund.day <= 23:
        teikn.append("jafndægur — dagr ok nótt í jafnvægi")
    if stund.month in (6, 12) and 19 <= stund.day <= 23:
        teikn.append("sólhvörf — vending ljóssins")
    return teikn


# --------------------------------------------------------------------------
# Skapvísir  (heimrinn veginn, eigi lesinn)
#
# Hér verða orð at tǫlum. Engi setning heimsins kemzt lengra en hingat: þaðan
# af ferðast einungis hiti, þungi, járn, vald, þrjózka ok ljós.
# --------------------------------------------------------------------------
ᚨᛋᛁᚱ: dict[str, tuple[str, ...]] = {
    "ófriðr": (
        "war", "strike", "clash", "attack", "kill", "troops", "missile", "siege",
        "raid", "escalate", "battle", "bomb", "assault", "offensive", "militar",
        "krig", "angrep", "drept", "strid",
    ),
    "harmr": (
        "dead", "death", "died", "flee", "fled", "famine", "collapse", "victim",
        "quake", "flood", "drown", "mourn", "funeral", "displaced", "evacuat",
        "død", "flykt", "ulykke", "sorg",
    ),
    "járn": (
        "ai", "model", "chip", "comput", "code", "robot", "algorithm", "software",
        "data", "quantum", "neural", "silicon", "server", "kernel", "compiler",
        "llm", "gpu", "protocol", "machine",
    ),
    "vald": (
        "court", "law", "ban", "election", "president", "minister", "sanction",
        "parliament", "ruling", "regime", "senate", "treaty", "tariff", "policy",
        "vote", "regjering", "domstol", "val",
    ),
    "þrjózka": (
        "protest", "union", "mutual", "solidarity", "occupy", "resist", "commune",
        "squat", "anarch", "riot", "boycott", "picket", "autonom", "collective",
        "streik", "motstand",
    ),
}


def _vega(raddir: list[str]) -> dict[str, int]:
    """Hlutfall raddanna sem bera hvern ás — talit 0…10."""
    if not raddir:
        return {á: 0 for á in ᚨᛋᛁᚱ}
    lágt = [r.lower() for r in raddir]
    vog: dict[str, int] = {}
    for ás, orð in ᚨᛋᛁᚱ.items():
        n = sum(1 for r in lágt if any(o in r for o in orð))
        vog[ás] = round(10 * n / len(lágt))
    return vog


def skapvísir(
    stund: ᛋᛏᚢᚾᛞ | None = None,
    smiðja: list[str] | None = None,
    þjóðir: list[str] | None = None,
) -> dict:
    """Skap vikunnar í tǫlum einum. Engi eiginnǫfn, engi fyrirsagnir, engi staðir."""
    stund = stund or ᛋᛏᚢᚾᛞ.now(ᛒᛖᛚᛏᛁ.utc)
    smiðja = raddir_smiðju() if smiðja is None else smiðja
    þjóðir = raddir_þjóða() if þjóðir is None else þjóðir

    # Hverr ás veginn á þeim rǫddum sem hann varðar: smiðjan talar um járn,
    # þjóðirnar um ófrið ok vald. Væri allt vegit saman, kœfði tal smiðjunnar
    # harm heimsins — sextán fyrirsagnir, ok engi þeirra um hinn dauða.
    vog = _vega(þjóðir)
    vog["járn"] = _vega(smiðja)["járn"]
    staða = _mánastaða(stund)
    ljós = round(10 * (1 - abs(staða - 0.5) * 2))   # 0 at nýjum, 10 at fullum
    return {
        **vog,
        "ljós": ljós,
        "tungl": "vaxandi" if staða < 0.5 else "þverrandi",
        "árstíð": _árstíð(stund),
        "jafnvægi": bool(stund.month in (3, 9) and 19 <= stund.day <= 23),
        "hvörf": bool(stund.month in (6, 12) and 19 <= stund.day <= 23),
    }


def safna_teiknum(stund: ᛋᛏᚢᚾᛞ | None = None, kast: ᚺᛚᚢᛏ.Random | None = None) -> dict:
    """Skap vikunnar — ok hit hráa geymt til annálar einnar, aldri til vǫlvunnar."""
    stund = stund or ᛋᛏᚢᚾᛞ.now(ᛒᛖᛚᛏᛁ.utc)
    kast = kast or ᚺᛚᚢᛏ.Random()
    smiðja = raddir_smiðju()
    þjóðir = raddir_þjóða(kast=kast)
    return {
        "skap": skapvísir(stund, smiðja, þjóðir),
        "hrátt": smiðja + þjóðir,      # einungis til loggar; fer aldri í galdrinn
        "tala": {"smiðja": len(smiðja), "þjóðir": len(þjóðir)},
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(safna_teiknum()["skap"])
