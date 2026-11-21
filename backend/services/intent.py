"""Détection de l'intention : de quoi parle l'utilisateur ?

Technique volontairement simple : mots-clés wolof/français, sans accents.
Pour aller plus loin, on remplacera ce fichier par un petit LLM (voir llm.py).
"""
from __future__ import annotations

import unicodedata


def normaliser(texte: str) -> str:
    """Minuscules + suppression des accents : « météo » devient « meteo ».

    Indispensable car l'orthographe varie (français accentué, wolof ë…).
    Les caractères spéciaux wolof (ñ, ŋ) sont conservés tels quels.
    """
    t = (texte or "").lower().strip()
    out = []
    for c in t:
        if unicodedata.category(c) == "Mn":   # accent combinant → on l'ignore
            continue
        if c in "ñŋ":                          # on garde les lettres wolof
            out.append(c)
            continue
        decompose = unicodedata.normalize("NFD", c)
        decompose = "".join(
            x for x in decompose if unicodedata.category(x) != "Mn"
        )
        out.append(decompose or c)
    return "".join(out)


# Dictionnaire : intention -> mots-clés (déjà normalisés : sans accents)
MOTS_CLES: dict[str, list[str]] = {
    "meteo": [
        "meteo", "njafi", "tegg", "temps", "temperature",
        "abbes", "pluie", "llanu", "forecast",
    ],
    "marche": [
        "prix", "marche", "sokhna", "kosam", "combien",
        "acheter", "achat", "ndel", "riz", "mil", "poisson", "huile",
    ],
    "sante": [
        "pharmacie", "sante", "malade", "docteur", "medecin",
        "hopital", "doktor", "garde",
    ],
    "autre": ["conte", "histoire", "jerejef", "merci", "jamm"],  # salutations, contes…
}


def detecter(texte: str) -> tuple[str, str | None]:
    """Retourne (intention, paramètre_extrait).

    Exemples :
        "prix du riz à Dakar"  -> ("marche", "dakar")
        "météo biu Dakar"      -> ("meteo", "dakar")
        "pharmacie de garde"   -> ("sante", None)
        "bonjour"              -> ("autre", None)
    """
    t = normaliser(texte)

    # 1. Quelle intention ?
    intention = "autre"
    for nom, mots in MOTS_CLES.items():
        if any(m in t for m in mots):
            intention = nom
            break  # la première intention trouvée gagne

    # 2. Quelle ville ? (liste issue de config.py)
    from config import VILLES
    ville = None
    for nom_ville in VILLES:
        if nom_ville in t:
            ville = nom_ville
            break

    return intention, ville


def extraire_produit(texte: str) -> str | None:
    """Pour le marché : quel produit cherche-t-on ?"""
    produits = ["riz", "mil", "mais", "poisson", "huile", "sucre", "oeuf", "lait"]
    t = normaliser(texte)
    for p in produits:
        if p in t:
            return p
    return None
