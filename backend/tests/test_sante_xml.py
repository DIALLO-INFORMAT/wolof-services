"""Teste le parseur XML de l'API OSM — sans réseau, 100 % fiable."""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.sante import _distance, _parser_xml  # noqa: E402

XML = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6">
  <node id="1" lat="14.7038" lon="-17.4749">
    <tag k="amenity" v="pharmacy"/>
    <tag k="name" v="Pharmacie Stella"/>
    <tag k="opening_hours" v="Mo-Sa 08:30-20:30"/>
  </node>
  <node id="2" lat="14.7200" lon="-17.4700"/>
  <node id="3" lat="14.7190" lon="-17.4710"/>
  <node id="4" lat="14.7210" lon="-17.4690"/>
  <way id="10">
    <nd ref="2"/>
    <nd ref="3"/>
    <nd ref="4"/>
    <tag k="amenity" v="pharmacy"/>
    <tag k="name" v="Pharmacie du Marche"/>
  </way>
</osm>
"""


def test_parse_noeud():
    resultats = _parser_xml(XML)
    noms = [r["nom"] for r in resultats]
    assert "Pharmacie Stella" in noms, noms


def test_parse_way_centre():
    """Un way (bâtiment) doit donner son centre géométrique."""
    resultats = _parser_xml(XML)
    marche = next(r for r in resultats if r["nom"] == "Pharmacie du Marche")
    assert abs(marche["lat"] - 14.7200) < 0.001
    assert abs(marche["lon"] - (-17.4700)) < 0.001


def test_parse_horaire():
    resultats = _parser_xml(XML)
    stella = next(r for r in resultats if r["nom"] == "Pharmacie Stella")
    assert stella["ouverture"] == "Mo-Sa 08:30-20:30"


def test_parse_ignore_non_pharmacie():
    """Le nœud 2/3/4 ne sont pas des pharmacies : ne doivent pas apparaître seuls."""
    resultats = _parser_xml(XML)
    assert len(resultats) == 2, resultats


def test_distance():
    # ~1 km de latitude = 0.009 degrés
    d = _distance(14.70, -17.47, 14.709, -17.47)
    assert 0.9 < d < 1.1, d


if __name__ == "__main__":
    for nom, fn in sorted(globals().items()):
        if nom.startswith("test_") and callable(fn):
            fn()
            print(f"OK {nom}")
    print("\nTous les tests du parseur passent.")
