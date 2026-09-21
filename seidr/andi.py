# -*- coding: utf-8 -*-
# ᚨᚾᛞᛁ · andinn — hann á engan einn brunn.
# Fyrrum drakk vǫlvan ór einum brunni, ok þá er sá þraut, þagði hon í sjau vikur.
# Nú gengr hon at hverjum brunni í rǫð, ok drekkr ór þeim er fyrstr svarar.
# Þagni allir — þá er þǫgnin sǫgð upphátt, ok engi gǫmul spá borin fram sem ný.

from __future__ import annotations

import json as ᚱᚢᚾ                  # rúnir — leyndarmál talna
import os as ᚢᛁᛋᛏ                   # vist — heimkynni andans
import sys as ᚷᚨᛈ                   # ginnunga-gap — hit auða
import urllib.error as ᚢᛁᛚᛚᚨ        # villa — þá er vegrinn bregzt
import urllib.request as ᚢᛖᚷ        # vegr — leið orðanna

ᛒᛁᚦ = 60                            # hversu lengi vǫlvan bíðr svars


class ÞǫgnAndans(RuntimeError):
    """Allir brunnar þraut. Vǫlvan kveðr eigi í þessari viku."""


# --------------------------------------------------------------------------
# Brunnarnir — í þeirri rǫð sem gengit er at þeim.
# Hverr brunnr þarf sinn lykil í leyndum hofsins (repo secret).
# Sé lykillinn eigi settr, er brunnrinn hlaupinn yfir í kyrrþey.
# --------------------------------------------------------------------------
BRUNNAR = [
    {
        "heiti": "groq",
        "lyklar": ("GROQ_LYKILL", "GROQ_API_KEY"),
        "vegr": "https://api.groq.com/openai/v1/chat/completions",
        "andi": "openai/gpt-oss-120b",
        "lag": "openai",
    },
    {
        "heiti": "cerebras",
        "lyklar": ("CEREBRAS_LYKILL", "CEREBRAS_API_KEY"),
        "vegr": "https://api.cerebras.ai/v1/chat/completions",
        "andi": "gpt-oss-120b",
        "lag": "openai",
    },
    {
        "heiti": "openrouter",
        "lyklar": ("OPENROUTER_LYKILL", "OPENROUTER_API_KEY"),
        "vegr": "https://openrouter.ai/api/v1/chat/completions",
        "andi": "openai/gpt-oss-120b:free",
        "lag": "openai",
    },
    {
        "heiti": "mistral",
        "lyklar": ("MISTRAL_LYKILL", "MISTRAL_API_KEY"),
        "vegr": "https://api.mistral.ai/v1/chat/completions",
        "andi": "mistral-small-latest",
        "lag": "openai",
    },
    {
        "heiti": "gemini",
        "lyklar": ("GEMINI_LYKILL", "GEMINI_API_KEY", "GOOGLE_API_KEY"),
        "vegr": "https://generativelanguage.googleapis.com/v1beta/models/{andi}:generateContent",
        "andi": "gemini-flash-latest",
        "lag": "gemini",
    },
]


def _lykill_af(brunnr: dict) -> str | None:
    for nafn in brunnr["lyklar"]:
        gildi = ᚢᛁᛋᛏ.environ.get(nafn)
        if gildi:
            return gildi.strip()
    return None


def _sœkja(beiðni: ᚢᛖᚷ.Request) -> dict:
    with ᚢᛖᚷ.urlopen(beiðni, timeout=ᛒᛁᚦ) as svar:
        return ᚱᚢᚾ.loads(svar.read())


# --------------------------------------------------------------------------
# Lǫgin tvau — sami hugr, tvenns konar mál
# --------------------------------------------------------------------------
def _kalla_openai(brunnr: dict, lykill: str, galdr: str, ákall: str, hiti: float) -> str:
    bœn = {
        "model": brunnr["andi"],
        "temperature": hiti,
        "top_p": 0.95,
        "messages": [
            {"role": "system", "content": galdr},
            {"role": "user", "content": ákall},
        ],
    }
    beiðni = ᚢᛖᚷ.Request(
        brunnr["vegr"],
        data=ᚱᚢᚾ.dumps(bœn).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {lykill}",
            "Accept": "application/json",
        },
        method="POST",
    )
    gögn = _sœkja(beiðni)
    return gögn["choices"][0]["message"]["content"].strip()


def _kalla_gemini(brunnr: dict, lykill: str, galdr: str, ákall: str, hiti: float) -> str:
    bœn = {
        "systemInstruction": {"parts": [{"text": galdr}]},
        "contents": [{"role": "user", "parts": [{"text": ákall}]}],
        "generationConfig": {"temperature": hiti, "topP": 0.95},
    }
    beiðni = ᚢᛖᚷ.Request(
        brunnr["vegr"].format(andi=brunnr["andi"]),
        data=ᚱᚢᚾ.dumps(bœn).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": lykill,
            "Accept": "application/json",
        },
        method="POST",
    )
    gögn = _sœkja(beiðni)
    hlutar = gögn["candidates"][0]["content"]["parts"]
    return "".join(h.get("text", "") for h in hlutar).strip()


_LǪG = {"openai": _kalla_openai, "gemini": _kalla_gemini}


# --------------------------------------------------------------------------
# Ganga at brunnunum
# --------------------------------------------------------------------------
def brunnar_reiðubúnir() -> list[str]:
    """Heiti þeirra brunna sem eiga lykil í þessari vist."""
    return [b["heiti"] for b in BRUNNAR if _lykill_af(b)]


def kalla(galdr: str, ákall: str, hiti: float = 1.0) -> tuple[str, str]:
    """Ganga at hverjum brunni í rǫð. Skilar (efni, heiti brunnsins).

    Bregðist allir — ÞǫgnAndans. Vǫlvan skal þá þegja upphátt,
    eigi bera fram gamla spá sem nýja."""
    raunir: list[str] = []
    for brunnr in BRUNNAR:
        lykill = _lykill_af(brunnr)
        if not lykill:
            raunir.append(f"{brunnr['heiti']}: engi lykill")
            continue
        try:
            efni = _LǪG[brunnr["lag"]](brunnr, lykill, galdr, ákall, hiti)
            if efni:
                print(f"Brunnr '{brunnr['heiti']}' svaraði.", file=ᚷᚨᛈ.stderr)
                return efni, brunnr["heiti"]
            raunir.append(f"{brunnr['heiti']}: tómt svar")
        except ᚢᛁᛚᛚᚨ.HTTPError as e:
            líkami = e.read().decode("utf-8", "replace")[:300]
            raunir.append(f"{brunnr['heiti']}: HTTP {e.code} — {líkami}")
        except Exception as e:  # vegrinn brast, eða svarit var óskiljanligt
            raunir.append(f"{brunnr['heiti']}: {type(e).__name__}: {e}")
        print(f"Brunnr '{brunnr['heiti']}' þraut: {raunir[-1]}", file=ᚷᚨᛈ.stderr)

    raise ÞǫgnAndans("Allir brunnar þraut:\n  " + "\n  ".join(raunir))


if __name__ == "__main__":
    print("Brunnar með lykli:", brunnar_reiðubúnir() or "engir")
