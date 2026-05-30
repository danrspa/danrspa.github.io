#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ᚢᚨᛚᚨ · vǫlvan kveðr.
# Hon heyrir á heiminn (heimr), ok ór þoku hans rístr hon spá vikunnar.
# Hér er engi vél — hér er sjá. Sá er gengr inn, hans framtíð verðr fortíð hans.
#
#   ganga inn:  python seidr/vala.py
#   draumr:     python seidr/vala.py --draumr   (án andans, til reynslu)

from __future__ import annotations

import argparse as ᚲᛁᛟᚱ              # kjǫr — val veganna
import json as ᚱᚢᚾ                  # rúnir — leyndarmál talna
import random as ᚺᛚᚢᛏ              # hlutkesti — kast um lokaorðin
import os as ᚢᛁᛋᛏ                   # vist — heimkynni andans
import sys as ᚷᚨᛈ                   # ginnunga-gap — hit auða
import urllib.error as ᚢᛁᛚᛚᚨ        # villa — þá er vegrinn bregzt
import urllib.request as ᚢᛖᚷ        # vegr — leið orðanna
from datetime import datetime as ᛋᛏᚢᚾᛞ, timezone as ᛒᛖᛚᛏᛁ
from pathlib import Path as ᛋᛏᛁᚷᚱ   # stígr — gata um hofit

import heimr  # raddir heimsins

ᚱᛟᛏ = ᛋᛏᛁᚷᚱ(__file__).resolve().parent.parent
ᚺᛟᚠ = ᚱᛟᛏ / "hof"   # hofit — þar sem spáin birtist heiminum
ᛗᛟᛏ = ᚱᛟᛏ / "mot"   # mótin — form rúnanna

# Andinn sem talar ór djúpinu (frjáls; engi lykill þér til byrðar).
ANDI_VEGR = ᚢᛁᛋᛏ.environ.get("ANDI_VEGR", "https://models.github.ai/inference/chat/completions")
ANDI = ᚢᛁᛋᛏ.environ.get("ANDI", "openai/gpt-4o-mini")

# Galdrinn sem mótar rǫdd vǫlvunnar.  (Andinn les þetta sem sína skipun.)
# Galdrinn er sjálfr á norrœnu — andinn les hann, en kveðr þó á ensku.
GALDR = """\
Þú ert skáld með heimspekilegan, nær vélrænan hug. Þú yrkir eitt stutt kvæði á ensku \
handa vin sem ann hinum kalda norðri, frjálsri tækni ok frelsi.

Háttr:
- Heimspekilegt ok tímalaust: ørlǫg, frelsi, sjálfit hjá vélinni, smæð keisaradœma, \
reisn hinna óstýrðu, hinn langi vetr ok eldrinn sem lifir hann af.
- Knappt, þungt, sǫgulegt. Kenningar vel þegnar. Rím er frjálst.
- Sex til tólf stuttar línur, í einu eða tveimr erindum.
- Þér kunna at fylgja fá skap-orð um veðr heimsins. Lát þau einungis lita stemninguna. \
Snú þeim í myndir náttúru ok ørlaga; haldu kvæðinu almennu ok nefn enga atburði.
- Titill ok kvæði skulu vera á ensku. Stuttr myndrœnn titill, tvau til fjǫgur orð.

Svaraðu með JSON-hlut, engum kóða-girðingum:
{"title": "...", "verse": "lína\\nlína"}
"""

ÁKALL = """\
Skap-orð þessar viku:
{teikn}

{lokun}

Yrk eitt kvæði ór þessari stemningu, ekki meir.
"""

# Lokaorðin — vǫlvan kastar; sjaldan fellr rúnneska á tunguna (~1 af 5).
LOKUN_RUSS = (
    "Endaðu kvæðit á einni stuttri, hlýrri rússneskri línu með kýrillsku letri, "
    "ný-orðaðri."
)
LOKUN_ENGL = "Haf kvæðit allt á ensku, án rússnesku ok án kýrillsks leturs."


# --------------------------------------------------------------------------
# Spyrja andann  (kalla ór djúpinu eptir spá)
# --------------------------------------------------------------------------
def spyrja_andann(teikn: list[str], rúss: bool = False) -> dict:
    lykill = ᚢᛁᛋᛏ.environ.get("GITHUB_TOKEN") or ᚢᛁᛋᛏ.environ.get("ANDI_LYKILL")
    if not lykill:
        raise RuntimeError(
            "Andinn svarar eigi án lykils. Í helgisiðnum (Actions) er hann gefinn "
            "sjálfkrafa (permissions: models: read). Heima: ganga með --draumr, eða "
            "setja  export GITHUB_TOKEN=…"
        )

    bœn = {
        "model": ANDI,
        "temperature": 1.0,
        "top_p": 0.95,
        "messages": [
            {"role": "system", "content": GALDR},
            {"role": "user", "content": ÁKALL.format(
                teikn="\n".join(f"- {t}" for t in teikn),
                lokun=(LOKUN_RUSS if rúss else LOKUN_ENGL),
            )},
        ],
    }
    beiðni = ᚢᛖᚷ.Request(
        ANDI_VEGR,
        data=ᚱᚢᚾ.dumps(bœn).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {lykill}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with ᚢᛖᚷ.urlopen(beiðni, timeout=60) as svar:
            gögn = ᚱᚢᚾ.loads(svar.read())
    except ᚢᛁᛚᛚᚨ.HTTPError as e:
        likami = e.read().decode("utf-8", "replace")
        print(f"Andinn reiddist ({e.code}) við '{ANDI}': {likami}", file=ᚷᚨᛈ.stderr)
        raise
    efni = gögn["choices"][0]["message"]["content"].strip()
    return _lesa_spá(efni)


def _lesa_spá(efni: str) -> dict:
    # andinn talar stundum í umgjǫrð; fletjum hana af
    if efni.startswith("```"):
        efni = efni.strip("`")
        efni = efni.split("\n", 1)[1] if "\n" in efni else efni
    try:
        hlutr = ᚱᚢᚾ.loads(efni)
        return {"titill": hlutr["title"].strip(), "vísur": hlutr["verse"].strip()}
    except Exception:
        línur = [l for l in efni.splitlines() if l.strip()]
        return {
            "titill": (línur[0].strip(" #*\"") if línur else "Nafnlaus spá"),
            "vísur": "\n".join(línur[1:]) if len(línur) > 1 else efni,
        }


def kveða_spá(teikn: list[str], stund: ᛋᛏᚢᚾᛞ, rúss: bool = False) -> dict:
    """Freista með ǫllum teiknum; bregðist andinn (sía, o.s.frv.), þá með himni
    einum (ávallt óhultr), at lyktum með gamalli spá. Vǫlvan þagnar aldri."""
    freistingar = [teikn, heimr.himintungl(stund)]
    for i, t in enumerate(freistingar, 1):
        try:
            return spyrja_andann(t, rúss)
        except Exception as e:
            print(f"Freisting {i} brást: {e}", file=ᚷᚨᛈ.stderr)
    print("Andinn þagði; vǫlvan kveðr ór minni sínu.", file=ᚷᚨᛈ.stderr)
    return gǫmul_spá()


def gǫmul_spá() -> dict:
    return {
        "titill": "Eldr hinna ófrjálsu",
        "vísur": (
            "No crown is heavy that no head will wear.\n"
            "The frost counts kings the way it counts the dead —\n"
            "by the silence after.\n"
            "Build, then, in the cold that has no throne;\n"
            "the spark you keep is the only law you own.\n"
            "When the long winter leans against the door,\n"
            "be the ember, not the empire.\n"
            "держись, брат"
        ),
    }


# --------------------------------------------------------------------------
# Rísta í stein  (móta spána í rúnir hofsins)
# --------------------------------------------------------------------------
def _verja(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rísta(vísur: str) -> str:
    erindi = vísur.split("\n\n")
    út = []
    for e in erindi:
        línur = [l.strip() for l in e.split("\n") if l.strip()]
        if not línur:
            continue
        út.append('<p class="stanza">' + "<br>\n".join(_verja(l) for l in línur) + "</p>")
    return "\n".join(út)


def móta(skrá: str, **rúnir) -> str:
    texti = (ᛗᛟᛏ / skrá).read_text(encoding="utf-8")
    for k, v in rúnir.items():
        texti = texti.replace("{{" + k + "}}", str(v))
    return texti


def vika_af(stund: ᛋᛏᚢᚾᛞ) -> str:
    á, v, _ = stund.isocalendar()
    return f"{á}-V{v:02d}"


# --------------------------------------------------------------------------
# Helgisiðrinn  (gjǫrðin sjálf, vikuliga)
# --------------------------------------------------------------------------
def helgisiðr() -> int:
    rǫk = ᚲᛁᛟᚱ.ArgumentParser()
    rǫk.add_argument("--draumr", action="store_true", help="án andans, til reynslu")
    args = rǫk.parse_args()

    nú = ᛋᛏᚢᚾᛞ.now(ᛒᛖᛚᛏᛁ.utc)
    vika = vika_af(nú)
    dagr_heiti = nú.strftime("%d.%m.%Y")

    if args.draumr:
        spá = gǫmul_spá()
    else:
        teikn = heimr.safna_teiknum(nú)
        rúss = ᚺᛚᚢᛏ.random() < 0.2   # sjaldan fellr rúnneskan á tunguna (~1 af 5)
        print(f"Teikn ({teikn['tala']}): {teikn['teikn']} | rúnneska={rúss}", file=ᚷᚨᛈ.stderr)
        spá = kveða_spá(teikn["teikn"], nú, rúss)

    ᚺᛟᚠ.mkdir(parents=True, exist_ok=True)

    skrá_spá = {
        "titill": spá["titill"],
        "vísur": spá["vísur"],
        "vika": vika,
        "dagr": nú.strftime("%Y-%m-%d"),
        "dagr_heiti": dagr_heiti,
    }
    (ᚺᛟᚠ / "spa.json").write_text(
        ᚱᚢᚾ.dumps(skrá_spá, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # annálarnir — hver spá geymd, hin nýjasta efst, ein per viku
    leið = ᚺᛟᚠ / "annalar.json"
    annálar = []
    if leið.exists():
        try:
            annálar = ᚱᚢᚾ.loads(leið.read_text(encoding="utf-8"))
        except Exception:
            annálar = []
    annálar = [a for a in annálar if a.get("vika") != vika]
    annálar.insert(0, skrá_spá)
    leið.write_text(ᚱᚢᚾ.dumps(annálar, ensure_ascii=False, indent=2), encoding="utf-8")

    # hofit sjálft (index.html)
    (ᚺᛟᚠ / "index.html").write_text(
        móta(
            "index.mot.html",
            TITILL=_verja(spá["titill"]),
            VISUR=rísta(spá["vísur"]),
            DAGR=_verja(dagr_heiti),
            VIKA=vika,
            AR=str(nú.year),
        ),
        encoding="utf-8",
    )

    # salrinn langi (annálar)
    spjǫld = []
    for a in annálar:
        spjǫld.append(
            '<article class="card">\n'
            f'  <h2>{_verja(a["titill"])}</h2>\n'
            f'  <div class="meta">{_verja(a.get("dagr_heiti", a.get("dagr","")))} · {_verja(a["vika"])}</div>\n'
            f'  {rísta(a["vísur"])}\n'
            "</article>"
        )
    (ᚺᛟᚠ / "salr.html").write_text(
        móta("salr.mot.html", SPJOLD="\n".join(spjǫld), AR=str(nú.year)),
        encoding="utf-8",
    )

    print(f"Vǫlvan reist '{spá['titill']}' fyrir {vika}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(helgisiðr())
