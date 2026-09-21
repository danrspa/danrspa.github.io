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
from datetime import datetime as ᛋᛏᚢᚾᛞ, timezone as ᛒᛖᛚᛏᛁ
from pathlib import Path as ᛋᛏᛁᚷᚱ   # stígr — gata um hofit

import andi   # brunnar djúpsins
import heimr  # raddir heimsins
import minni  # þat sem þegar var kveðit

ᚱᛟᛏ = ᛋᛏᛁᚷᚱ(__file__).resolve().parent.parent
ᚺᛟᚠ = ᚱᛟᛏ / "hof"   # hofit — þar sem spáin birtist heiminum
ᛗᛟᛏ = ᚱᛟᛏ / "mot"   # mótin — form rúnanna

# Andinn á engan einn brunn lengr — sjá andi.py. Sá brunnr sem fyrstr svarar, talar.

# Galdrinn sem mótar rǫdd vǫlvunnar.  (Andinn les þetta sem sína skipun.)
# Galdrinn er sjálfr á norrœnu — andinn les hann, en kveðr þó á ensku.
GALDR = """\
Þú ert skáld með heimspekilegan, nær vélrænan hug. Þú yrkir eitt stutt kvæði á ensku \
handa vin sem ann hinum kalda norðri, frjálsri tækni ok frelsi.

Háttr:
- Heimspekilegt ok tímalaust: ørlǫg, frelsi, sjálfit hjá vélinni, smæð keisaradœma, \
reisn hinna óstýrðu, ok eldrinn sem lifir af þat sem at honum sœkir.
- Knappt, þungt, sǫgulegt. Kenningar vel þegnar. Rím er frjálst.
- Þér eru gefnar tǫlur um veðr heimsins — ófriðr, harmr, járn, vald, þrjózka, ljós. \
Þær eru stemning ein. Nefn þær aldri, hvorki at heiti né tǫlu; snú þeim í myndir \
náttúru ok ørlaga. Þú sér engar fyrirsagnir, því at engar eru þér gefnar.
- Engi eiginnǫfn: engi lǫnd, engir menn, engar borgir, engi fyrirtœki, engi vélaheiti.
- Engi norrœn orð í kvæðinu sjálfu. Kvæðit er á ensku, allt.
- Titill ok kvæði skulu vera á ensku. Stuttr myndrœnn titill, tvau til fjǫgur orð.
- Árstíðin sem þér er sǫgð er hin sanna. Yrk í hennar ljósi, eigi í vetri sem eigi er.
- Forðastu hin slitnu orð sem þér eru talin. Þau eru þegar kveðin til þurrðar. \
Finn nýja mynd í staðinn — engan skugga, engan hvískr, engan neista er áðr brann.
- Titillinn skal eigi vera "X of Y". Nefn hlut, eigi hugtak.

Svaraðu með JSON-hlut, engum kóða-girðingum:
{"title": "...", "verse": "lína\\nlína"}
"""

ÁKALL = """\
Skap heimsins þessa viku — tǫlur einar, 0 til 10. Þær eru veðr, eigi efni:
{skap}

Árstíðin nú: {árstíð}.

Ker þessarar viku (haltu þat nákvæmliga):
{háttr}

Slitin orð — engi þeirra má standa í kvæðinu:
{þreytt}

Titlar þegar bornir — engi líkr þeim:
{titlar}

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
def _skap_í_línur(skap: dict) -> str:
    """Skapit ritat svá at engi setning heimsins fylgi með."""
    raðir = [
        f"  ófriðr    {skap['ófriðr']:2d}/10",
        f"  harmr     {skap['harmr']:2d}/10",
        f"  járn      {skap['járn']:2d}/10",
        f"  vald      {skap['vald']:2d}/10",
        f"  þrjózka   {skap['þrjózka']:2d}/10",
        f"  ljós      {skap['ljós']:2d}/10  ({skap['tungl']} tungl)",
    ]
    if skap.get("jafnvægi"):
        raðir.append("  jafndægur — dagr ok nótt jǫfn")
    if skap.get("hvörf"):
        raðir.append("  sólhvörf — vending ljóssins")
    return "\n".join(raðir)


def spyrja_andann(
    skap: dict,
    árstíð: str,
    háttr: str,
    þreytt: list[str],
    titlar: list[str],
    rúss: bool = False,
    hiti: float = 1.0,
) -> tuple[dict, str]:
    ákall = ÁKALL.format(
        skap=_skap_í_línur(skap),
        árstíð=árstíð,
        háttr=háttr,
        þreytt=", ".join(þreytt) if þreytt else "(engi enn)",
        titlar="\n".join(f"- {t}" for t in titlar) if titlar else "(engir enn)",
        lokun=(LOKUN_RUSS if rúss else LOKUN_ENGL),
    )
    efni, brunnr = andi.kalla(GALDR, ákall, hiti)
    return _lesa_spá(efni), brunnr


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


def kveða_spá(
    skap: dict,
    stund: ᛋᛏᚢᚾᛞ,
    vika: str,
    annálar: list[dict],
    rúss: bool = False,
    hrátt: list[str] | None = None,
) -> tuple[dict, str, str]:
    """Kveðr, ok dœmir sjálf um sitt verk. Sé kvæðit endrtekning, kveðr hon aptr
    með heitara blóði. Þagni allir brunnar — þá þegir hon upphátt (ÞǫgnAndans);
    hér er engi gǫmul spá borin fram sem ný. Þat var sǫk hinna sjau vikna."""
    árstíð = heimr.árstíð_heiti(stund)
    háttr = minni.háttr_vikunnar(vika, annálar)
    þreytt = minni.þreytt_orð(annálar)
    titlar = minni.þreyttir_titlar(annálar)
    print(f"Háttr: {háttr}", file=ᚷᚨᛈ.stderr)
    print(f"Slitin orð ({len(þreytt)}): {', '.join(þreytt)}", file=ᚷᚨᛈ.stderr)

    síðasta_sǫk = "engi tilraun"
    for tilraun in range(1, 4):
        hiti = 0.9 + 0.15 * tilraun
        try:
            spá, brunnr = spyrja_andann(
                skap, árstíð, háttr, þreytt, titlar, rúss, hiti
            )
        except andi.ÞǫgnAndans:
            raise
        except Exception as e:
            síðasta_sǫk = f"{type(e).__name__}: {e}"
            print(f"Tilraun {tilraun} brást: {síðasta_sǫk}", file=ᚷᚨᛈ.stderr)
            continue
        sǫk = (
            minni.leki(spá, hrátt)
            or minni.vanefndir(spá, þreytt)
            or minni.er_endrtekning(spá, annálar)
        )
        if not sǫk:
            return spá, brunnr, háttr
        síðasta_sǫk = sǫk
        print(f"Tilraun {tilraun} hafnat — {sǫk}", file=ᚷᚨᛈ.stderr)

    raise andi.ÞǫgnAndans(
        f"Vǫlvan náði engri nýrri spá í þremr tilraunum ({síðasta_sǫk})."
    )


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

    leið = ᚺᛟᚠ / "annalar.json"
    annálar = minni.lesa_annála(leið)
    fyrri = [a for a in annálar if a.get("vika") != vika]

    brunnr, háttr = "draumr", "—"
    if args.draumr:
        spá = gǫmul_spá()
    else:
        teikn = heimr.safna_teiknum(nú)
        rúss = ᚺᛚᚢᛏ.random() < 0.2   # sjaldan fellr rúnneskan á tunguna (~1 af 5)
        print(f"Raddir ({teikn['tala']}) | rúnneska={rúss}", file=ᚷᚨᛈ.stderr)
        print(f"Skap: {teikn['skap']}", file=ᚷᚨᛈ.stderr)
        try:
            spá, brunnr, háttr = kveða_spá(
                teikn["skap"], nú, vika, fyrri, rúss, teikn["hrátt"]
            )
        except andi.ÞǫgnAndans as e:
            # Vǫlvan þegir heldr en at endrtaka sik. Hofit stendr sem þat stóð;
            # helgisiðrinn fellr, svá at þǫgnin sjáist.
            print(f"\nÞǫGN ANDANS:\n{e}", file=ᚷᚨᛈ.stderr)
            print(
                f"Brunnar með lykli: {andi.brunnar_reiðubúnir() or 'engir'}",
                file=ᚷᚨᛈ.stderr,
            )
            print("Ekkert ritat. Spá fyrri viku stendr óhreyfð.", file=ᚷᚨᛈ.stderr)
            return 1

    ᚺᛟᚠ.mkdir(parents=True, exist_ok=True)

    skrá_spá = {
        "titill": spá["titill"],
        "vísur": spá["vísur"],
        "vika": vika,
        "dagr": nú.strftime("%Y-%m-%d"),
        "dagr_heiti": dagr_heiti,
        "háttr": háttr,
        "brunnr": brunnr,
    }
    (ᚺᛟᚠ / "spa.json").write_text(
        ᚱᚢᚾ.dumps(skrá_spá, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # annálarnir — hver spá geymd, hin nýjasta efst, ein per viku.
    # Draumr er eigi ristr: hann skal aldri mengja minni vǫlvunnar.
    annálar = [skrá_spá] + fyrri
    if not args.draumr:
        leið.write_text(ᚱᚢᚾ.dumps(annálar, ensure_ascii=False, indent=2), encoding="utf-8")

    # hjartsláttr hofsins — svá at þǫgn sjáist innan viku, eigi eptir sjau
    (ᚺᛟᚠ / "heilsa.json").write_text(
        ᚱᚢᚾ.dumps(
            {
                "síðasta_spá": nú.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "vika": vika,
                "brunnr": brunnr,
                "annálar": len(annálar),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

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
