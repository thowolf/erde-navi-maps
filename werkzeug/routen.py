"""Routendaten (Valhalla-Kacheln) pro Region verpacken, für Routen ohne Internet in Erde Navi.

Eingabe: ein Ordner mit Valhalla-Kacheln für den ganzen Raum (Schweiz, Österreich, Deutschland), gebaut aus
OpenStreetMap, und die Grenzen aus grenzen/<kürzel>.geojson. Jede Region bekommt alle Kacheln, die ihre Fläche
(plus Rand) berühren. Kacheln an der Grenze liegen darum in zwei Paketen; die App legt sie nur einmal ab.

Schreibt <aus>/<kürzel>.routen.tar.gz und <aus>/routen.json (Kürzel → Datei, Bytes, entpackte Bytes).
Aufruf: python3 werkzeug/routen.py <kacheln> <aus> [kürzel,kürzel]
"""
import io
import json
import os
import sys
import tarfile

from shapely.geometry import box, shape
from shapely.ops import unary_union

# Kachelgrösse in Grad je Ebene (0 = Autobahnen, 1 = Hauptstrassen, 2 = alle übrigen Strassen)
GROESSE = {0: 4.0, 1: 1.0, 2: 0.25}
RAND_GRAD = 0.1  # etwa 8–11 km, damit Strassen über die Grenze hinaus anschliessen


def kachel_rahmen(pfad):
    """'2/000/818/660.gph' → (ebene, Rahmen) oder None für andere Dateien."""
    teile = pfad.split("/")
    if len(teile) < 2 or not teile[-1].endswith(".gph"):
        return None
    ebene = int(teile[0])
    if ebene not in GROESSE:
        return None
    nummer = int("".join(teile[1:])[: -len(".gph")])
    g = GROESSE[ebene]
    spalten = int(360 / g)
    zeile, spalte = divmod(nummer, spalten)
    x, y = -180 + spalte * g, -90 + zeile * g
    return ebene, box(x, y, x + g, y + g)


def main():
    kacheln, aus = sys.argv[1:3]
    nur = set(filter(None, (sys.argv[3] if len(sys.argv) > 3 else "").split(",")))
    regionen = json.load(open("regionen.json", encoding="utf-8"))
    alle = []
    for wurzel, _, dateien in os.walk(kacheln):
        for d in dateien:
            pfad = os.path.relpath(os.path.join(wurzel, d), kacheln).replace(os.sep, "/")
            r = kachel_rahmen(pfad)
            if r:
                alle.append((pfad, r[1]))
    if not alle:
        sys.exit(f"Keine Kacheln in {kacheln}")
    print(f"{len(alle)} Kacheln gefunden")

    liste = {}
    for reg in regionen:
        rid = reg["id"]
        if nur and rid not in nur:
            continue
        geo = json.load(open(f"grenzen/{rid}.geojson", encoding="utf-8"))
        flaeche = unary_union([shape(f["geometry"]) for f in geo["features"]]).buffer(RAND_GRAD)
        auswahl = sorted(p for p, rahmen in alle if rahmen.intersects(flaeche))
        datei = f"{rid}.routen.tar.gz"
        entpackt = 0
        # Feste Zeitstempel und Besitzer, damit gleiche Daten die gleiche Datei ergeben
        with tarfile.open(os.path.join(aus, datei), "w:gz", compresslevel=9) as tar:
            for p in auswahl:
                inhalt = open(os.path.join(kacheln, p), "rb").read()
                info = tarfile.TarInfo(p)
                info.size = len(inhalt)
                info.mtime = 0
                tar.addfile(info, io.BytesIO(inhalt))
                entpackt += len(inhalt)
        groesse = os.path.getsize(os.path.join(aus, datei))
        liste[rid] = {"datei": datei, "bytes": groesse, "entpackt": entpackt, "kacheln": len(auswahl)}
        print(f"{rid:6} {len(auswahl):5} Kacheln  {entpackt / 1e6:7.0f} MB entpackt  {groesse / 1e6:6.0f} MB Download")
    json.dump(liste, open(os.path.join(aus, "routen.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
