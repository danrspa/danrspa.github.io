# -*- coding: utf-8 -*-
# ᛗᛁᚾᚾᛁ · minni vǫlvunnar.
# Hon mundi ekki hvat hon hafði kveðit, ok því kvað hon hit sama um sinn ok sinn:
# skuggar, hvískr, frelsi, frost — sextán vikur ór einum brunni orða.
# Nú man hon. Þat sem einu sinni var kveðit, verðr eigi kveðit ǫðru sinni.

from __future__ import annotations

import hashlib as ᚺᚨᛋ               # hasl — mark ór mǫrgu
import re as ᛚᛖᛁᛏ                   # leit — mynstr í orðum
from collections import Counter as ᛏᚨᛚ

# Orð sem bera enga merking í samanburði
ᛋᛏᛟᛈ = frozenset("""
the a an and or but in of on at to for from by with as is are was were be been
that this these those it its his her their our we you i not no yet each all
what when where while through into over under again then than so if
""".split())

# Hversu líkt má nýtt kvæði vera hinu gamla áðr en þat telst endrtekning
LIKT_MARK = 0.22
# Hversu margar vikur aptr vǫlvan man í smáatriðum
MINNIS_DJUP = 12


# --------------------------------------------------------------------------
# Hættirnir — nýtt ker hverja viku, þótt rǫddin sé hin sama
# --------------------------------------------------------------------------
HÆTTIR = [
    "Tvau erindi, fjórar línur hvert. Stuðlar skulu bera hverja línu (fornyrðislag).",
    "Eitt órofit erindi, átta línur, engi rím.",
    "Þrjú stutt erindi, þrjár línur hvert.",
    "Sex línur. Hver lína hefst á nafnorði; engi lýsingarorð.",
    "Átta línur sem enda á spurningu er eigi verðr svarat.",
    "Tvau erindi, fjórar línur hvert. Hit fyrra spyrr, hit síðara svarar "
    "með mynd, eigi með orði.",
    "Sjau línur, hver styttri en hin fyrri.",
    "Eitt erindi, tíu línur, sem eitt andartak — engi punktr fyrr en at lyktum.",
    "Fjórar línur einar. Hvert orð skal vinna fyrir sér.",
    "Tvau erindi, fimm línur hvert, borin uppi af kenningum.",
    "Níu línur. Hin þriðja, sétta ok níunda skulu vera stakar — ein rǫdd á móti.",
    "Sex línur í annarri persónu — kvæðit ávarpar þann er les.",
    "Tvau erindi, fjórar línur hvert. Hit fyrra í fortíð, hit síðara í framtíð; "
    "hvárugt í nútíð.",
    "Átta línur. Engi lína má hefjast á sama staf sem hin næsta á undan.",
]


def háttr_vikunnar(vika: str, annálar: list[dict]) -> str:
    """Hættinum er kastat ór vikunni sjálfri — sami kastr hverja viku,
    en aldri sá er síðast var kveðinn við."""
    nýlegir = {a.get("háttr") for a in annálar[:3] if a.get("háttr")}
    mark = int(ᚺᚨᛋ.sha256(vika.encode("utf-8")).hexdigest()[:8], 16)
    for skref in range(len(HÆTTIR)):
        h = HÆTTIR[(mark + skref) % len(HÆTTIR)]
        if h not in nýlegir:
            return h
    return HÆTTIR[mark % len(HÆTTIR)]


# --------------------------------------------------------------------------
# Þreytt orð — brunnr sem þraut
# --------------------------------------------------------------------------
def _orð(texti: str) -> list[str]:
    return [o.lower() for o in ᛚᛖᛁᛏ.findall(r"[A-Za-z']+", texti)]


def _kjarni(texti: str) -> set[str]:
    return {o for o in _orð(texti) if o not in ᛋᛏᛟᛈ and len(o) > 3}


def þreytt_orð(annálar: list[dict], fjǫldi: int = 22) -> list[str]:
    """Orð sem vǫlvan hefir þegar slitit — þau skal hon eigi taka upp aptr.

    Talit er í kvæðum, eigi í orðum: eitt kvæði sem endrtekit var sjau sinnum
    er enn eitt kvæði. Ella myndi ein endrtekning kæfa hin sǫnnu slitnu orð."""
    séð: set[str] = set()
    tal = ᛏᚨᛚ()
    for a in annálar[:MINNIS_DJUP]:
        vísur = a.get("vísur", "").strip()
        if not vísur or vísur in séð:
            continue
        séð.add(vísur)
        tal.update(_kjarni(vísur))       # hvert orð talit einu sinni per kvæði
    return [o for o, n in tal.most_common() if n >= 2][:fjǫldi]


def þreyttir_titlar(annálar: list[dict], fjǫldi: int = 10) -> list[str]:
    return [a["titill"] for a in annálar[:fjǫldi] if a.get("titill")]


# --------------------------------------------------------------------------
# Dómr um endrtekning
# --------------------------------------------------------------------------
def líking(a: str, b: str) -> float:
    x, y = _kjarni(a), _kjarni(b)
    if not x or not y:
        return 0.0
    return len(x & y) / len(x | y)


def er_endrtekning(spá: dict, annálar: list[dict]) -> str | None:
    """Skilar sǫk ef kvæðit er endrtekning — annars None."""
    vísur, titill = spá.get("vísur", ""), spá.get("titill", "")
    if not vísur.strip():
        return "tómar vísur"
    for a in annálar:
        if a.get("vísur", "").strip() == vísur.strip():
            return f"samhljóða spánni frá {a.get('vika')}"
        if titill and a.get("titill", "").lower() == titill.lower():
            return f"titill þegar borinn í {a.get('vika')}"
        l = líking(vísur, a.get("vísur", ""))
        if l > LIKT_MARK:
            return f"of líkt spánni frá {a.get('vika')} ({l:.0%})"
    if ᛚᛖᛁᛏ.match(r"^(Echoes|Whispers|Embers|Beneath|Under|Shadows)\b", titill, ᛚᛖᛁᛏ.I):
        return f"slitinn titil-háttr: '{titill}'"
    # Tveir titlar í rǫð er hefjast eins ('Iron Dawn', 'Iron Pulse') eru einn titill
    fyrsta = titill.split()[0].lower() if titill.split() else ""
    for a in annálar[:4]:
        gamalt = (a.get("titill") or "").split()
        if fyrsta and gamalt and gamalt[0].lower() == fyrsta:
            return f"titill hefst sem sá frá {a.get('vika')}: '{fyrsta}'"
    return None


# --------------------------------------------------------------------------
# Lekadómr — vǫrn gegn því at heimrinn sjáist berum orðum
#
# Galdrinn bað hana nefna engan atburð. Hon nefndi Jemen. Bón dugir eigi einum
# veikum anda; hér er mælt, eigi beðit.
# --------------------------------------------------------------------------
# Norrœn orð er borizt hafa í kvæðit sem vorð heimsins (djúpt haust, vaxandi gibba)
NORRŒNT = ᛚᛖᛁᛏ.compile(
    r"\b(gibba|haust|hávetr|vetr|sumar|vár|máni|tungl|sigð|jafndægur|"
    r"sólhvörf|djúpt|vaxandi|þverrandi|ófriðr|harmr|járn|vald|þrjózka|ljós)\b",
    ᛚᛖᛁᛏ.I,
)
# Orð sem eiga heima í frétt, eigi í kvæði
FRÉTTAMÁL = ᛚᛖᛁᛏ.compile(
    r"\b(ai|llm|gpu|ci|api|ceo|algorithm|software|startup|server|kernel|"
    r"compiler|protocol|dataset|blockchain|percent|quarterly|lawsuit|"
    r"parliament|senate|tariff|sanctions?)\b",
    ᛚᛖᛁᛏ.I,
)
# Eiginnǫfn sem hvorki hefja línu né eru "I"
EIGINNAFN = ᛚᛖᛁᛏ.compile(r"(?<![.\n!?\"'—-]\s)(?<!^)\b([A-Z][a-z]{2,})\b", ᛚᛖᛁᛏ.M)
LEYFÐ_NǪFN = frozenset("""
I A The A God Death Winter Summer Spring Autumn North South East West
Monday Tuesday Wednesday Thursday Friday Saturday Sunday
""".split())


def leki(spá: dict, hrátt: list[str] | None = None) -> str | None:
    """Skilar sǫk ef heimrinn sést berum orðum í kvæðinu — annars None."""
    texti = f"{spá.get('titill','')}\n{spá.get('vísur','')}"

    m = NORRŒNT.search(texti)
    if m:
        return f"norrœnt teikn laust inn í kvæðit: '{m.group(0)}'"

    m = FRÉTTAMÁL.search(texti)
    if m:
        return f"fréttamál í kvæðinu: '{m.group(0)}'"

    # Orð tekin beint ór fyrirsǫgnum vikunnar. Borit saman um stofn (5 stafi),
    # svá at 'Yemenis' í frétt grípi 'Yemen' í kvæði.
    # Einungis sérkennileg orð eru talin: eiginnǫfn (hástafr inni í línu) eða
    # lǫng orð (7+). Ella greip dómrinn 'still' ok 'storm' — mál skáldsins sjálfs.
    if hrátt:
        stofnar = set()
        for r in hrátt:
            for o in ᛚᛖᛁᛏ.findall(r"\b[A-Za-z]{5,}\b", r):
                sérkennilegt = (o[0].isupper() and not r.startswith(o)) or len(o) >= 7
                if sérkennilegt and o.lower() not in ᛋᛏᛟᛈ:
                    stofnar.add(o.lower()[:5])
        for o in ᛚᛖᛁᛏ.findall(r"\b[A-Za-z]{5,}\b", texti):
            if o.lower() not in ᛋᛏᛟᛈ and o.lower()[:5] in stofnar:
                return f"orð tekit ór fyrirsǫgn: '{o}'"

    # Eiginnǫfn eru vegin í vísunum einum — titill má vera með hástǫfum at hætti.
    nǫfn = [n for n in EIGINNAFN.findall(spá.get("vísur", "")) if n not in LEYFÐ_NǪFN]
    if nǫfn:
        return f"eiginnafn í vísunum: '{nǫfn[0]}'"

    return None


# --------------------------------------------------------------------------
# Formdómr — þat sem beðit var um, ok þat sem kom
#
# Galdrinn bað um tvau erindi ok fjórar línur hvert; andinn sendi tvær línur.
# Bón dugir eigi. Hér er talit.
# --------------------------------------------------------------------------
LÍNUR_FÆST, LÍNUR_FLEST = 4, 14


def vanefndir(spá: dict, þreytt: list[str] | None = None) -> str | None:
    """Skilar sǫk ef kvæðit heldr eigi þat sem um var beðit — annars None."""
    línur = [l for l in spá.get("vísur", "").splitlines() if l.strip()]
    if len(línur) < LÍNUR_FÆST:
        return f"of stutt: {len(línur)} línur, {LÍNUR_FÆST} hit fæsta"
    if len(línur) > LÍNUR_FLEST:
        return f"of langt: {len(línur)} línur, {LÍNUR_FLEST} hit flesta"

    # Ein lína sem er heilt erindi í dulargervi — andinn hnoðar stundum saman
    if any(len(l) > 120 for l in línur):
        return "lína of lǫng — erindi hnoðat í eina línu"

    if þreytt:
        orð = {o.lower() for o in ᛚᛖᛁᛏ.findall(r"[A-Za-z']+", spá.get("vísur", ""))}
        slitin = sorted(orð & {t.lower() for t in þreytt})
        if slitin:
            return "slitin orð endrtekin: " + ", ".join(slitin[:4])
    return None


def lesa_annála(leið) -> list[dict]:
    import json as ᚱᚢᚾ
    if not leið.exists():
        return []
    try:
        return ᚱᚢᚾ.loads(leið.read_text(encoding="utf-8"))
    except Exception:
        return []
