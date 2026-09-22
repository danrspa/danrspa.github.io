# -*- coding: utf-8 -*-
# ᚺᛖᛁᛗᚱ · heimrinn andar, ok vǫlvan heyrir.
# Hon lýðr á raddir heimsins — á smiðju manna, á þjóðir norðrs ok suðrs, á þá
# sem standa utan hallar, á himintunglin — ok vegr ór þeim SKAP, eigi ORÐ.
#
# Hér er hin harða regla: ekkert hrátt orð heimsins fer til vǫlvunnar. Hon fær
# tǫlur einar — hita ok þunga ok ljós. Nefni hon engan atburð, þá er þat eigi
# af því at hon var beðin þess, heldr af því at hon sá hann aldri.

from __future__ import annotations

import concurrent.futures as ᚦᚱᛖᚦᛁᚱ  # þræðir — margar raddir í senn
import json as ᚱᚢᚾ                  # rúnir — leyndarmál talna
import random as ᚺᛚᚢᛏ              # hlutkesti — kast örlaganna
import re as ᛚᛖᛁᛏ                   # leit — mynstr í orðum
import sys as ᚷᚨᛈ                   # ginnunga-gap — hit auða
import urllib.request as ᚢᛖᚷ       # vegr — leið orðanna
import xml.etree.ElementTree as ᚱᛁᛋᛏ  # rist — markaðar línur í steini
from datetime import datetime as ᛋᛏᚢᚾᛞ, timezone as ᛒᛖᛚᛏᛁ

ᛗᚨᚱᚲ = "vala/1.0 (+heimr)"          # mark farandans
ᛒᛁᚦ = 15                            # hversu lengi vǫlvan bíðr svars


class HeimrÞegir(RuntimeError):
    """Engi straumr svaraði. Betra er þǫgn en kvæði ór tómi."""


def _sœkja(slóð: str) -> bytes:
    # sœkja orð af veginum
    beiðni = ᚢᛖᚷ.Request(slóð, headers={"User-Agent": ᛗᚨᚱᚲ})
    with ᚢᛖᚷ.urlopen(beiðni, timeout=ᛒᛁᚦ) as svar:
        return svar.read()


# --------------------------------------------------------------------------
# Raddir ór smiðju manna  (þar sem hlutir eru smíðaðir ór tölum)
# --------------------------------------------------------------------------
def raddir_smiðju(fjǫldi: int = 18) -> list[str]:
    """Áðr var hverr hlutr sóttr í sinni ferð, hverr á eftir ǫðrum. Nú fara
    allir sendimenn í senn. Ok fleiri raddir: átta voru of fáar til at vega
    með — ein rǫdd af átta stǫkk kvarðanum um heilan fjórðung."""
    def _titill(eind: int) -> str | None:
        try:
            hlutr = ᚱᚢᚾ.loads(
                _sœkja(f"https://hacker-news.firebaseio.com/v0/item/{eind}.json")
            )
            return (hlutr or {}).get("title")
        except Exception:
            return None

    try:
        eindir = ᚱᚢᚾ.loads(
            _sœkja("https://hacker-news.firebaseio.com/v0/topstories.json")
        )[:fjǫldi]
    except Exception:
        return []
    with ᚦᚱᛖᚦᛁᚱ.ThreadPoolExecutor(max_workers=10) as sveit:
        return [t for t in sveit.map(_titill, eindir) if t]


# --------------------------------------------------------------------------
# Brunnar þjóðanna  (eigi hallarinnar einnar — norðrit ok jaðarinn með)
# --------------------------------------------------------------------------
BRUNNAR_ÞJÓÐA = [
    # norðrit — hit kalda land sem kvæðit talar um. Sex raddir, því at tvær
    # þǫgðu í fyrstu rétt-gjǫrðu viku (stundar-þǫgn, eigi varanleg), ok þá
    # stóð norðrit — sjálft efni kvæðisins — á einum fœti.
    ("https://www.nrk.no/toppsaker.rss", "norðr"),
    ("https://www.svt.se/rss.xml", "norðr"),
    ("https://www.dr.dk/nyheder/service/feeds/allenyheder", "norðr"),
    ("https://www.ruv.is/rss/frettir", "norðr"),
    ("https://icelandmonitor.mbl.is/rss/", "norðr"),
    ("https://www.helsinkitimes.fi/?format=feed&type=rss", "norðr"),
    # heimrinn — tvær raddir, eigi ein
    ("https://feeds.bbci.co.uk/news/world/rss.xml", "heimr"),
    ("https://www.aljazeera.com/xml/rss/all.xml", "heimr"),
    # jaðarrinn — þeir sem standa utan hallar
    ("https://freedomnews.org.uk/feed/", "jaðarr"),
    ("https://crimethinc.com/feed", "jaðarr"),
    ("https://meduza.io/rss/en/all", "heimr"),
    # staðrinn — ein borg, nær. Heimrinn er eigi einungis fjarlægr.
    ("https://www.rtvutrecht.nl/rss/nieuws.xml", "staðr"),
    ("https://www.ad.nl/utrecht/rss.xml", "staðr"),
]

KYN = ("norðr", "heimr", "jaðarr", "staðr")

ᚨᛏᛟᛗ = "{http://www.w3.org/2005/Atom}"


def _greinar(slóð: str, atlǫgur: int = 2) -> list[str]:
    """Titlar greinanna einna.

    Áðr var hér  titlar[1:]  — ok þá laust heiti brunnsins sjálfs inn sem teikn
    ('BBC News'), því at sumir brunnar bera heiti sitt tvisvar (rás ok mynd).
    Nú er gengit um <item>/<entry> ok tekinn beinn titill hvers — engi rásartitill."""
    # Tveir brunnar þǫgðu í fyrstu viku (ParseError, HTTPError) en svǫruðu báðir
    # skjótt eftir — stundar-hnot, eigi lokat hlið. Því er reynt tvisvar.
    for atlaga in range(atlǫgur):
        try:
            rót = ᚱᛁᛋᛏ.fromstring(_sœkja(slóð))
            break
        except Exception:
            if atlaga == atlǫgur - 1:
                raise
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


def raddir_þjóða(fjǫldi: int = 12, kast: ᚺᛚᚢᛏ.Random | None = None) -> list[str]:
    """Áðr tók hon ór fyrsta brunni sem svaraði — ok þat var ávallt hinn sami.
    Nú svara allir samtímis, ok hvert kyn á sinn hlut: norðr, heimr, jaðarr,
    staðr. Áðr var blandat ok skorit af handahófi, ok þá gat heilt kyn horfit
    ór vikunni af tilviljun einni."""
    kast = kast or ᚺᛚᚢᛏ.Random()
    eftir_kyni: dict[str, list[str]] = {k: [] for k in KYN}
    þagðir: list[str] = []

    with ᚦᚱᛖᚦᛁᚱ.ThreadPoolExecutor(max_workers=len(BRUNNAR_ÞJÓÐA)) as sveit:
        verk = {sveit.submit(_greinar, s): (s, k) for s, k in BRUNNAR_ÞJÓÐA}
        for v in ᚦᚱᛖᚦᛁᚱ.as_completed(verk):
            slóð, kyn = verk[v]
            try:
                greinar = v.result()
            except Exception as e:
                þagðir.append(f"{slóð.split('/')[2]} ({type(e).__name__})")
                continue
            if greinar:
                eftir_kyni[kyn] += greinar
            else:
                þagðir.append(f"{slóð.split('/')[2]} (tómr)")

    if þagðir:   # rotnun brunnanna skal sjást, eigi hverfa í kyrrþey
        print("Brunnar sem þǫgðu: " + ", ".join(sorted(þagðir)), file=ᚷᚨᛈ.stderr)

    hlutr = max(1, fjǫldi // len(KYN))
    safn: list[str] = []
    for kyn in KYN:
        greinar = eftir_kyni[kyn]
        kast.shuffle(greinar)
        safn += greinar[:hlutr]
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
# Orðin voru áðr leitat sem hlutar orða, ok þá varð "rain" at járni (ai),
# "band" at valdi (ban), "available" at járni. Skapit var hávaði einn.
# Nú er leitat at heilum orðum; stjarna merkir stofn ("militar*" = militant,
# military, militarised).
ᚨᛋᛁᚱ: dict[str, tuple[str, ...]] = {
    "ófriðr": (
        "war", "wars", "warfare", "clash*", "attack*", "kill*", "troops",
        "missile*", "siege", "raid*", "escalat*", "battle*", "bomb*",
        "assault*", "offensive", "militar*", "airstrike*", "shelling",
        "krig*", "angrep*", "drept", "drepn*", "anfall*", "dödad*", "dræbt*",
        "strid", "stríð*", "árás*", "våld*", "vold*",
        "oorlog*", "aanval*", "geweld*", "gevecht*", "leger", "aanslag*", "schiet*",
    ),
    "harmr": (
        "dead", "death*", "died", "flee*", "fled", "famine", "collapse*",
        "victim*", "quake*", "flood*", "drown*", "mourn*", "funeral",
        "displaced", "evacuat*", "casualt*", "toll",
        "død", "død*", "döda", "flykt*", "ulykke*", "olyck*", "sorg",
        "omkom*", "látin*", "slys*", "offer", "ofre",
        "dood", "overled*", "slachtoffer*", "ramp", "rampen", "gewond*", "vermist*",
    ),
    "járn": (
        "ai", "model*", "chip*", "comput*", "code", "coding", "robot*",
        "algorithm*", "software", "data", "dataset*", "quantum", "neural",
        "silicon", "server*", "kernel", "compiler*", "llm*", "gpu*",
        "protocol*", "machine*", "artificial", "intelligence", "transformer*",
        "encrypt*", "decrypt*", "semiconductor*", "processor*", "firmware",
        "database*", "browser*", "linux", "kernel*", "crypto*", "startup*",
        "cloud", "compiler*", "runtime", "framework*", "benchmark*",
        "digitaal", "kunstmatige", "algoritme*", "technolog*",
    ),
    "vald": (
        "court*", "law", "laws", "ban", "bans", "banned", "election*",
        "president*", "minister*", "sanction*", "parliament*", "ruling*",
        "regime*", "senate", "treaty", "tariff*", "policy", "vote*",
        "regjering*", "regering*", "ríkisstjórn*", "domstol*", "dómstól*",
        "valg", "valet", "kosning*", "forbud*", "förbud*", "bann",
        "statsminister*", "ráðherra",
        "rechtbank*", "verbod*", "kabinet*", "gemeente*", "raad", "uitspraak*",
        "verkiezing*",
    ),
    "þrjózka": (
        "protest*", "union*", "solidarity", "occupy", "occupation", "resist*",
        "commune", "squat*", "anarch*", "riot*", "boycott*", "picket*",
        "autonom*", "collective*", "strike*", "walkout*",
        "streik*", "strejk*", "verkfall*", "motstand*", "mótmæl*",
        "fagforening*", "fack*", "demonstration*",
        "staking*", "demonstratie*", "kraak*", "krak*", "bezetting*", "vakbond*",
    ),
}

# Hvert orð verðr at mynstri: heilt orð, eða stofn ef stjarna fylgir.
ᛗᚤᚾᛋᛏᚱ: dict[str, ᛚᛖᛁᛏ.Pattern] = {
    ás: ᛚᛖᛁᛏ.compile(
        "|".join(
            r"\b" + ᛚᛖᛁᛏ.escape(o[:-1]) + r"\w*" if o.endswith("*")
            else r"\b" + ᛚᛖᛁᛏ.escape(o) + r"\b"
            for o in orð
        ),
        ᛚᛖᛁᛏ.I,
    )
    for ás, orð in ᚨᛋᛁᚱ.items()
}


# Vika þar sem þriðjungr raddanna ber einn ás er heit vika. Væri talit beint
# í hundraðshlutum, stœði kvarðinn jafnan í 0-2, ok skapit væri dautt.
ᛗᛖᛏᛏᚢᚾ = {"járn": 0.70}
ᛗᛖᛏᛏᚢᚾ_ALMENN = 0.35


def _vega(raddir: list[str]) -> dict[str, int]:
    """Hlutfall raddanna sem bera hvern ás — teygt yfir kvarðann 0…10."""
    if not raddir:
        return {á: 0 for á in ᚨᛋᛁᚱ}
    vog: dict[str, int] = {}
    for ás, mynstr in ᛗᚤᚾᛋᛏᚱ.items():
        n = sum(1 for r in raddir if mynstr.search(r))
        mett = ᛗᛖᛏᛏᚢᚾ.get(ás, ᛗᛖᛏᛏᚢᚾ_ALMENN)
        vog[ás] = min(10, round(10 * (n / len(raddir)) / mett))
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
    # Þegðu allir straumar, yrði skapit tómt (0 á hverjum ás) ok vǫlvan kvæði
    # ór engu — sama þǫgn ok fyrr, í nýjum klæðum. Hér er hon stöðvuð.
    if len(smiðja) + len(þjóðir) < 4:
        raise HeimrÞegir(
            f"Heimrinn þegir: {len(smiðja)} raddir ór smiðju, "
            f"{len(þjóðir)} ór þjóðum. Engi spá verðr ort ór engu."
        )
    return {
        "skap": skapvísir(stund, smiðja, þjóðir),
        "hrátt": smiðja + þjóðir,      # einungis til loggar; fer aldri í galdrinn
        "tala": {"smiðja": len(smiðja), "þjóðir": len(þjóðir)},
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(safna_teiknum()["skap"])
