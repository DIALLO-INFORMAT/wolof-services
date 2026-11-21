"""Tests rapides — lancer avec :  python -m pytest tests/ -q
ou directement :  python tests/test_services.py
"""
import asyncio
import sys
from pathlib import Path

# Windows : la console utilise cp1252, qui ne connaît pas ✅ ni le wolof
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import intent, marche  # noqa: E402


def test_detection_meteo():
    intention, ville = intent.detecter("meteo biu Dakar")
    assert intention == "meteo"
    assert ville == "dakar"


def test_detection_marche():
    intention, ville = intent.detecter("combien le prix du riz à Thies")
    assert intention == "marche"
    assert ville == "thies"


def test_detection_sante():
    intention, _ = intent.detecter("pharmacie de garde")
    assert intention == "sante"


def test_produit():
    assert intent.extraire_produit("prix du riz") == "riz"
    assert intent.extraire_produit("bonjour") is None


def test_prix():
    resultat = marche.prix_produits("prix du riz", "dakar")
    assert resultat["prix"], "le fichier prix_marche.csv doit contenir du riz"
    assert "riz" in resultat["texte"]


def test_meteo():
    from services import meteo
    resultat = asyncio.run(meteo.previsions("dakar"))
    assert "temperature" in resultat
    assert "Dakar" in resultat["texte"]


if __name__ == "__main__":
    for nom, fn in sorted(globals().items()):
        if nom.startswith("test_") and callable(fn):
            fn()
            print(f"✅ {nom}")
    print("\nTous les tests passent.")
