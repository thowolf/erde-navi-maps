"""Grenzen der Regionen als GeoJSON für `pmtiles extract --region`.

Quelle: Natural Earth 1:10 Mio (gemeinfrei) – Länder (CH, AT) und Bundesländer (DE-xx).
Mit etwa 2 km Rand, damit an der Grenze nichts abgeschnitten wird. Schreibt grenzen/<kürzel>.geojson.
Aufruf: python3 werkzeug/grenzen.py <laender.geojson> <bundeslaender.geojson>
"""
import json
import os
import sys

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

RAND_GRAD = 0.025  # etwa 2 km

laender, provinzen = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
regionen = json.load(open("regionen.json", encoding="utf-8"))
os.makedirs("grenzen", exist_ok=True)

for r in regionen:
    iso = r["iso"]
    if "-" in iso:
        teile = [f for f in provinzen["features"] if f["properties"].get("iso_3166_2") == iso]
    else:
        teile = [f for f in laender["features"] if iso in (f["properties"].get("ISO_A2"), f["properties"].get("ISO_A2_EH"))]
    if not teile:
        sys.exit(f"Keine Grenze für {r['id']} ({iso}) gefunden")
    flaeche = unary_union([shape(f["geometry"]) for f in teile]).buffer(RAND_GRAD).simplify(0.005)
    with open(f"grenzen/{r['id']}.geojson", "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"id": r["id"]}, "geometry": mapping(flaeche)}]}, f)
    print(f"{r['id']:6} {iso:6} Fläche {flaeche.area:.2f} Grad², Rahmen {[round(x, 2) for x in flaeche.bounds]}")
