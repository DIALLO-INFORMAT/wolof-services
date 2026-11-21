"""Météo — API Open-Meteo : gratuite, sans clé, sans inscription.

Docs : https://open-meteo.com/en/docs
"""
from __future__ import annotations

import httpx

from config import VILLES

DEFAUT = ("dakar", VILLES["dakar"])

# Petit lexique wolof pour la réponse (à faire valider par des locuteurs)
WOLUF_CIEL = {
    "clear": "ci leen",           # dégagé
    "cloudy": "ci biir bëj",
    "rain": "ci tëgg",
}


async def previsions(ville: str | None = None) -> dict:
    """Retourne {ville, temperature, vent, ciel, texte} pour une ville du Sénégal."""
    nom, coords = DEFAUT
    if ville and ville in VILLES and VILLES[ville]:
        nom, coords = ville, VILLES[ville]

    lat, lon = coords
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,wind_speed_10m,weather_code"
        "&timezone=Africa/Dakar"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()["current"]

    temp = data["temperature_2m"]
    vent = data["wind_speed_10m"]
    code = data.get("weather_code", 0)
    ciel = _vers_ciel(code)

    texte = (
        f"À {nom.capitalize()}, {temp} degrés, vent {vent} km/h, {ciel}. "
        f"Jamm rekk, dañu ko jaral."
    )
    return {
        "ville": nom,
        "temperature": temp,
        "vent": vent,
        "ciel": ciel,
        "texte": texte,
    }


def _vers_ciel(code: int) -> str:
    """Traduit les codes météo d'Open-Meteo en mots simples."""
    if code == 0:
        return "leen (dégagé)"
    if code in (1, 2, 3):
        return "bëj ak àll (nuages)"
    if code in (45, 48):
        return "brume"
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "tëgg (pluie)"
    if code in (71, 73, 75, 77, 85, 86):
        return "sàkk"
    if code in (95, 96, 99):
        return "àddo ak tëgg (orage)"
    return "ci leen"
