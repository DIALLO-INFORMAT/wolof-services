"""Prix au marché — source locale data/prix_marche.csv.

Le Sénégal n'a pas encore d'API publique de prix : on constitue notre propre
base (à enrichir avec les prix réels de Sandaga, Thies, Touba…).
"""
from __future__ import annotations

import csv
from pathlib import Path

from services.intent import extraire_produit

FICHIER = Path(__file__).resolve().parent.parent / "data" / "prix_marche.csv"


def _charger() -> list[dict]:
    if not FICHIER.exists():
        return []
    with FICHIER.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def prix_produits(texte: str, ville: str | None = None) -> dict:
    """Retourne les prix correspondant à la demande, + un texte wolof simple."""
    lignes = _charger()
    produit = extraire_produit(texte)

    if ville:
        lignes = [l for l in lignes if l["ville"].lower() == ville]
    if produit:
        lignes = [l for l in lignes if l["produit"].lower() == produit]

    if not lignes:
        return {
            "prix": [],
            "texte": "Mboolek, xam-xam bi weesu ci biir bi. "
                     "Dañu ko yégal ci kanam.",
        }

    premier = lignes[0]
    detail = ", ".join(
        f"{l['produit']} {l['prix']} F CFA ({l['unite']}) à {l['ville']}"
        for l in lignes[:5]
    )
    texte = f"Ndel bi : {detail}. Jamm rekk."
    return {"prix": lignes[:5], "texte": texte, "produit": produit}
