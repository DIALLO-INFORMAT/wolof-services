"""Santé — trouver la pharmacie la plus proche.

Deux sources gratuites, combinées pour survivre aux pannes :

  1. Overpass API (gratuit, sans clé) — grande zone, mais serveur
     régulièrement saturé (502) ou timeout selon les réseaux
  2. API principale OpenStreetMap (api.openstreetmap.org) — fiable et
     rapide (2-3 s), mais limitée à ~50 000 nœuds par requête

Les deux sont interrogées en parallèle, les résultats fusionnés.
Si TOUT échoue : message wolof poli, JAMAIS de crash 500.
"""
from __future__ import annotations

import asyncio
import math
import time
import xml.etree.ElementTree as ET

import httpx

MIROIRS_OVERPASS = [
    "https://overpass.osm.ch/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

# API principale OSM : format minLon,minLat,maxLon,maxLat (longitude négative)
API_OSM = "https://api.openstreetmap.org/api/0.6/map"
# Degrés : on essaie du plus petit au plus grand (limite 50 000 nœuds)
BOITES = [0.012, 0.025, 0.006]

UA = "WolofServices/0.1 (projet langues, Senegal)"

REQUETE_OVERPASS = """
[out:json][timeout:20];
(
  node["amenity"="pharmacy"]({sud},{ouest},{nord},{est});
  way["amenity"="pharmacy"]({sud},{ouest},{nord},{est});
);
out center 20;
"""

# Cache en mémoire : {(lat, lon) arrondies: (resultats, horodatage)}
_CACHE: dict[tuple[float, float], tuple[list[dict], float]] = {}
DUREE_CACHE = 3600  # 1 heure


async def pharmacies_proches(lat: float | None = None, lon: float | None = None) -> dict:
    """Retourne les pharmacies les plus proches + un texte wolof simple.

    Ne lève jamais d'exception : si le réseau bloque, message poli.
    """
    if lat is None or lon is None:
        lat, lon = 14.72, -17.47  # centre de Dakar

    elements = await _rechercher(lat, lon)

    resultats = []
    for e in elements:
        resultats.append({
            "nom": e.get("nom", "Pharmacie"),
            "lat": e.get("lat"),
            "lon": e.get("lon"),
            "ouverture": e.get("ouverture", ""),
        })

    if not resultats:
        texte = ("Mboolek ak farmaasi ci biir bi. "
                 "Jërëm-jërëm, wàllu bi war na nekk war.")
    else:
        premier = resultats[0]["nom"]
        texte = (
            f"Farmaasi bi ci biir bi moo gën a néew : {premier}. "
            f"Dañu ko gise ci wàllu bi."
        )

    return {"pharmacies": resultats[:10], "texte": texte}


async def _rechercher(lat: float, lon: float) -> list[dict]:
    """Cache d'abord, puis Overpass + API OSM en parallèle."""
    cle = (round(lat, 3), round(lon, 3))
    entree = _CACHE.get(cle)
    if entree and (time.time() - entree[1]) < DUREE_CACHE:
        return entree[0]

    marge = 0.12
    query = REQUETE_OVERPASS.format(
        sud=round(lat - marge, 4),
        ouest=round(lon - marge, 4),
        nord=round(lat + marge, 4),
        est=round(lon + marge, 4),
    )

    async with httpx.AsyncClient(
        timeout=20, headers={"User-Agent": UA}
    ) as client:
        taches = [
            asyncio.create_task(_overpass(client, query)),
            asyncio.create_task(_osm_map(client, lat, lon)),
        ]
        reponses = await asyncio.gather(*taches, return_exceptions=True)

    # Fusion : on garde toutes les pharmacies trouvées, sans doublon
    fusion: dict[tuple[float, float], dict] = {}
    for rep in reponses:
        if isinstance(rep, list):
            for e in rep:
                cle2 = (round(e["lat"], 4), round(e["lon"], 4))
                fusion.setdefault(cle2, e)

    resultats = sorted(
        fusion.values(),
        key=lambda e: _distance(lat, lon, e["lat"], e["lon"]),
    )
    if resultats:
        _CACHE[cle] = (resultats, time.time())
    return resultats


async def _overpass(client: httpx.AsyncClient, query: str) -> list[dict]:
    """Interroge tous les miroirs Overpass en parallèle, le premier gagne."""
    taches = [
        asyncio.create_task(_essayer_overpass(client, url, query))
        for url in MIROIRS_OVERPASS
    ]
    reponses = await asyncio.gather(*taches, return_exceptions=True)
    for rep in reponses:
        if isinstance(rep, list) and rep:
            for t in taches:
                t.cancel()
            return rep
    return []


async def _essayer_overpass(client: httpx.AsyncClient, url: str, query: str) -> list[dict]:
    try:
        r = await client.post(url, data={"data": query})
        if r.status_code != 200:
            return []
        elements = []
        for e in r.json().get("elements", []):
            pos = e.get("center", e)
            if pos.get("lat") is None:
                continue
            tags = e.get("tags", {})
            elements.append({
                "nom": tags.get("name", "Pharmacie"),
                "lat": float(pos["lat"]),
                "lon": float(pos["lon"]),
                "ouverture": tags.get("opening_hours", ""),
            })
        return elements
    except (httpx.HTTPError, ValueError, KeyError):
        return []


async def _osm_map(client: httpx.AsyncClient, lat: float, lon: float) -> list[dict]:
    """API principale OSM : fiable, mais zone limitée (50 000 nœuds)."""
    for demi in BOITES:
        bbox = f"{lon - demi:.4f},{lat - demi:.4f},{lon + demi:.4f},{lat + demi:.4f}"
        try:
            r = await client.get(API_OSM, params={"bbox": bbox}, timeout=25)
            if r.status_code == 200:
                return _parser_xml(r.text)
            # 400 = trop de nœuds → on essaie une boîte plus petite
            if r.status_code != 400:
                return []
        except (httpx.HTTPError, ET.ParseError, ValueError):
            return []
    return []


def _parser_xml(texte: str) -> list[dict]:
    """Extrait les pharmacies du XML renvoyé par l'API OSM."""
    racine = ET.fromstring(texte)

    # Index des nœuds (pour calculer le centre des ways)
    nœuds = {
        n.get("id"): (float(n.get("lat")), float(n.get("lon")))
        for n in racine.findall("node")
    }

    def est_pharmacie(el) -> bool:
        return any(
            t.get("k") == "amenity" and t.get("v") == "pharmacy"
            for t in el.findall("tag")
        )

    def nom_de(el) -> str:
        for t in el.findall("tag"):
            if t.get("k") == "name":
                return t.get("v")
        return "Pharmacie"

    def ouverture_de(el) -> str:
        for t in el.findall("tag"):
            if t.get("k") == "opening_hours":
                return t.get("v")
        return ""

    resultats = []

    # Pharmacies = nœuds isolés
    for n in racine.findall("node"):
        if est_pharmacie(n):
            resultats.append({
                "nom": nom_de(n),
                "lat": float(n.get("lat")),
                "lon": float(n.get("lon")),
                "ouverture": ouverture_de(n),
            })

    # Pharmacies = ways (bâtiments) → centre géométrique
    for w in racine.findall("way"):
        if est_pharmacie(w):
            refs = [nd.get("ref") for nd in w.findall("nd")]
            coords = [nœuds[r] for r in refs if r in nœuds]
            if coords:
                resultats.append({
                    "nom": nom_de(w),
                    "lat": sum(c[0] for c in coords) / len(coords),
                    "lon": sum(c[1] for c in coords) / len(coords),
                    "ouverture": ouverture_de(w),
                })

    return resultats


def _distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance approximative en km (formule haversine simplifiée)."""
    dlat = (lat2 - lat1) * 111.0
    dlon = (lon2 - lon1) * 111.0 * math.cos(math.radians(lat1))
    return (dlat ** 2 + dlon ** 2) ** 0.5
