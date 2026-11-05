"""Suchdaten pro Region, damit Erde Navi auch ohne Internet Adressen, Orte und POIs findet.

Zwei Schritte:
  python3 werkzeug/suche.py sammeln <auszug.osm.pbf> <sammlung.db>
      liest einen OpenStreetMap-Auszug (am besten vorher mit osmium tags-filter verkleinert) und legt alle
      Adressen, Orte und POIs in einer Sammel-Datenbank ab (Schweiz, Österreich, Deutschland zusammen).
  python3 werkzeug/suche.py regionen <sammlung.db> <aus> [kürzel,kürzel]
      schneidet daraus pro Region (Grenzen aus grenzen/<kürzel>.geojson) eine kleine SQLite-Datei mit
      Volltextindex und packt sie als <aus>/<kürzel>.suche.gz. Schreibt <aus>/suche.json (Kürzel → Datei, Bytes,
      entpackte Bytes) für die Paketliste.

Format der Suchdatei (Version 1, Erde Navi liest sie mit dem SQLite von Android):
  meta(k, v)               version, region, stand
  ort(id, art, typ, name, zusatz, lat, lon, rang)
                           art 0 = Ort, 1 = POI, 2 = Strasse (mit Hausnummern in nr); lat/lon in 1e-5 Grad
  nr(strasse, nrn, pos)    Hausnummern einer Strasse: nrn mit „|“ getrennt, pos = Positionen als
                           Varint-Differenzen (zigzag) zur vorherigen Nummer, beginnend bei der Strasse selbst
  suche                    FTS4 ohne Inhalt (docid = ort.id), Tokenizer „simple“ auf vereinfachtem Text:
                           klein, ohne Akzente, ß → ss (siehe vereinfache(); Erde Navi macht dasselbe)
POIs ohne Namen kommen nur für die Kategorien „in der Nähe“ hinein (Tankstelle, Parkplatz …), nicht in den Index.
"""
import gzip
import json
import os
import shutil
import sqlite3
import sys
import unicodedata

VERSION = 1

# Orte: Rang für die Reihenfolge (grössere Orte zuerst)
ORTE = {"city": 9, "town": 8, "village": 6, "suburb": 5, "quarter": 4, "hamlet": 4, "neighbourhood": 3,
        "locality": 2, "isolated_dwelling": 1, "farm": 1}

# POIs mit Namen: diese Schlüssel (alle Werte), ausser wo eine Auswahl steht
POI_SCHLUESSEL = ("amenity", "shop", "tourism", "leisure", "historic", "office", "craft", "healthcare",
                  "sport", "railway", "aeroway", "natural", "highway", "public_transport")
POI_AUSWAHL = {
    "railway": {"station", "halt", "tram_stop"},
    "aeroway": {"aerodrome", "terminal"},
    "natural": {"peak", "saddle", "waterfall", "glacier", "spring", "cave_entrance", "volcano"},
    "highway": {"services", "rest_area"},
    "public_transport": {"station"},
}
# Ohne Namen trotzdem aufnehmen (für „in der Nähe“), Name dann aus Marke oder Betreiber, sonst leer
KATEGORIEN = {
    "amenity=fuel", "amenity=charging_station", "amenity=parking", "amenity=toilets", "amenity=atm",
    "amenity=pharmacy", "amenity=hospital", "amenity=restaurant", "amenity=fast_food", "amenity=cafe",
    "highway=services", "highway=rest_area", "tourism=camp_site", "tourism=caravan_site", "tourism=hotel",
    "shop=supermarket", "shop=car_repair", "amenity=sanitary_dump_station", "amenity=drinking_water",
}

ERSATZ = {"ß": "ss", "æ": "ae", "œ": "oe", "ø": "o", "đ": "d", "ł": "l", "ı": "i", "þ": "th"}


def vereinfache(text):
    """Klein, ohne Akzente, ß → ss. Muss genau zu OfflineSuche.vereinfache() in Erde Navi passen."""
    t = text.lower()
    t = "".join(ERSATZ.get(c, c) for c in t)
    t = unicodedata.normalize("NFD", t)
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def e5(x):
    return int(round(x * 1e5))


def varint(n):
    n = (n << 1) ^ (n >> 63)  # zigzag
    b = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n:
            b.append(x | 0x80)
        else:
            b.append(x)
            return bytes(b)


# ---------------------------------------------------------------- Sammeln

def sammeln(pbf, ziel):
    import osmium  # nur hier nötig

    if os.path.exists(ziel):
        os.remove(ziel)
    db = sqlite3.connect(ziel)
    db.executescript("""
        pragma journal_mode = off; pragma synchronous = off;
        create table adr(strasse text, plz text, ort text, nr text, lat int, lon int);
        create table obj(art int, typ text, name text, zusatz text, lat int, lon int, rang int);
    """)
    puffer_adr, puffer_obj = [], []

    def weg():
        db.executemany("insert into adr values(?,?,?,?,?,?)", puffer_adr)
        db.executemany("insert into obj values(?,?,?,?,?,?,?)", puffer_obj)
        puffer_adr.clear()
        puffer_obj.clear()

    class Leser(osmium.SimpleHandler):
        def objekt(self, t, lat, lon):
            nr = t.get("addr:housenumber")
            strasse = t.get("addr:street") or t.get("addr:place")
            plz, ort = t.get("addr:postcode", ""), t.get("addr:city", "")
            if nr and strasse:
                # „12;14“ oder „12,14“ → einzelne Nummern
                for n in nr.replace(",", ";").split(";"):
                    n = n.strip()
                    if n:
                        puffer_adr.append((strasse.strip(), plz, ort, n, e5(lat), e5(lon)))
            name = t.get("name")
            p = t.get("place")
            if name and p in ORTE:
                puffer_obj.append((0, p, name, "", e5(lat), e5(lon), ORTE[p]))
            else:
                for k in POI_SCHLUESSEL:
                    v = t.get(k)
                    if not v or (k in POI_AUSWAHL and v not in POI_AUSWAHL[k]):
                        continue
                    typ = f"{k}={v}"
                    n = name or t.get("brand") or t.get("operator") or ""
                    if name or typ in KATEGORIEN:
                        zus = " ".join(x for x in (plz, ort or t.get("addr:place", "")) if x)
                        puffer_obj.append((1, typ, n, zus, e5(lat), e5(lon), 1 if name else 0))
                    break
            if len(puffer_adr) + len(puffer_obj) > 200_000:
                weg()

        def node(self, n):
            if n.tags:
                self.objekt(n.tags, n.location.lat, n.location.lon)

        def way(self, w):
            t = w.tags
            if not t or "addr:housenumber" not in t and "name" not in t and not any(k in t for k in ("amenity", "highway", "tourism", "shop")):
                return
            if t.get("highway") not in (None, "services", "rest_area"):
                return  # Strassen selbst kommen über die Adressen
            try:
                la = [n.lat for n in w.nodes]
                lo = [n.lon for n in w.nodes]
            except osmium.InvalidLocationError:
                return
            if la:
                self.objekt(t, sum(la) / len(la), sum(lo) / len(lo))

    Leser().apply_file(pbf, locations=True, idx="sparse_file_array,sammlung.knoten")
    weg()
    if os.path.exists("sammlung.knoten"):
        os.remove("sammlung.knoten")
    db.execute("create index adr_lage on adr(lat, lon)")
    db.execute("create index obj_lage on obj(lat, lon)")
    db.commit()
    a = db.execute("select count(*) from adr").fetchone()[0]
    o = db.execute("select art, count(*) from obj group by art").fetchall()
    print(f"Gesammelt: {a} Adressen, {dict(o)} (0 = Orte, 1 = POIs)")
    db.close()


# ---------------------------------------------------------------- Regionen

def baue_region(sammlung, flaeche, ziel, region, stand):
    """Schreibt die Suchdatei einer Region. flaeche = shapely-Fläche (mit Rand)."""
    import shapely

    shapely.prepare(flaeche)
    x0, y0, x1, y1 = flaeche.bounds
    rahmen = (e5(y0), e5(y1), e5(x0), e5(x1))

    def drin(rows, ilat, ilon):
        if not rows:
            return []
        lats = [r[ilat] / 1e5 for r in rows]
        lons = [r[ilon] / 1e5 for r in rows]
        maske = shapely.contains_xy(flaeche, lons, lats)
        return [r for r, m in zip(rows, maske) if m]

    if os.path.exists(ziel):
        os.remove(ziel)
    db = sqlite3.connect(ziel)
    db.executescript(f"""
        pragma journal_mode = off; pragma synchronous = off; pragma page_size = 4096;
        create table meta(k text primary key, v text);
        create table ort(id integer primary key, art int, typ text, name text, zusatz text, lat int, lon int, rang int);
        create table nr(strasse integer primary key, nrn text, pos blob);
        create virtual table suche using fts4(content="", text, prefix="2,3");
    """)
    db.executemany("insert into meta values(?,?)", [("version", str(VERSION)), ("region", region), ("stand", stand)])
    sel = "between ? and ? and lon between ? and ?"
    i = 0
    zeilen_ort, zeilen_fts = [], []

    # Orte und POIs
    objs = drin(sammlung.execute(f"select art, typ, name, zusatz, lat, lon, rang from obj where lat {sel}", rahmen).fetchall(), 4, 5)
    gesehen = set()
    for art, typ, name, zus, la, lo, rang in objs:
        # Gleiches Objekt doppelt (Punkt und Fläche) → einmal
        sch = (art, typ, name, la // 30, lo // 30)
        if sch in gesehen:
            continue
        gesehen.add(sch)
        i += 1
        zeilen_ort.append((i, art, typ, name, zus, la, lo, rang))
        if name:
            zeilen_fts.append((i, vereinfache(f"{name} {zus}")))

    # Strassen mit Hausnummern: Eingang und Gebäude tragen oft dieselbe Nummer → Mittelpunkt pro Nummer
    adr = drin(sammlung.execute(f"select strasse, plz, ort, nr, lat, lon from adr where lat {sel}", rahmen).fetchall(), 4, 5)
    strassen = {}
    for st, plz, ort, nr, la, lo in adr:
        strassen.setdefault((st, plz, ort), {}).setdefault(nr, []).append((la, lo))
    zeilen_nr = []
    for (st, plz, ort), nummern in strassen.items():
        punkte = {n: (sum(p[0] for p in ps) // len(ps), sum(p[1] for p in ps) // len(ps)) for n, ps in nummern.items()}
        mla = sum(p[0] for p in punkte.values()) // len(punkte)
        mlo = sum(p[1] for p in punkte.values()) // len(punkte)
        i += 1
        zus = " ".join(x for x in (plz, ort) if x)
        zeilen_ort.append((i, 2, "", st, zus, mla, mlo, len(punkte)))
        zeilen_fts.append((i, vereinfache(f"{st} {zus}")))
        reihe = sorted(punkte, key=lambda n: (len(n), n))
        pos = bytearray()
        la0, lo0 = mla, mlo
        for n in reihe:
            la, lo = punkte[n]
            pos += varint(la - la0) + varint(lo - lo0)
            la0, lo0 = la, lo
        zeilen_nr.append((i, "|".join(reihe), bytes(pos)))

    db.executemany("insert into ort values(?,?,?,?,?,?,?,?)", zeilen_ort)
    db.executemany("insert into nr values(?,?,?)", zeilen_nr)
    db.executemany("insert into suche(docid, text) values(?,?)", zeilen_fts)
    db.execute("create index ort_typ on ort(typ) where art = 1")
    db.commit()
    db.execute("insert into suche(suche) values('optimize')")
    db.commit()
    db.execute("vacuum")
    db.close()
    return {"orte": sum(1 for z in zeilen_ort if z[1] == 0), "pois": sum(1 for z in zeilen_ort if z[1] == 1),
            "strassen": len(zeilen_nr), "adressen": sum(len(z[1].split("|")) for z in zeilen_nr)}


def regionen(sammlung_pfad, aus, nur_text="", stand=""):
    from shapely.geometry import shape
    from shapely.ops import unary_union

    nur = set(filter(None, nur_text.split(",")))
    sammlung = sqlite3.connect(sammlung_pfad)
    liste = {}
    for reg in json.load(open("regionen.json", encoding="utf-8")):
        rid = reg["id"]
        if nur and rid not in nur:
            continue
        geo = json.load(open(f"grenzen/{rid}.geojson", encoding="utf-8"))
        flaeche = unary_union([shape(f["geometry"]) for f in geo["features"]])
        db = os.path.join(aus, f"{rid}.suche.db")
        zahlen = baue_region(sammlung, flaeche, db, rid, stand)
        datei = f"{rid}.suche.gz"
        with open(db, "rb") as ein, gzip.GzipFile(os.path.join(aus, datei), "wb", compresslevel=9, mtime=0) as gz:
            shutil.copyfileobj(ein, gz, 1 << 20)
        entpackt = os.path.getsize(db)
        os.remove(db)
        bytes_ = os.path.getsize(os.path.join(aus, datei))
        liste[rid] = {"datei": datei, "bytes": bytes_, "entpackt": entpackt}
        print(f"{rid:6} {zahlen['adressen']:9} Adressen {zahlen['orte']:7} Orte {zahlen['pois']:8} POIs"
              f"  {entpackt / 1e6:6.0f} MB entpackt  {bytes_ / 1e6:5.0f} MB Download")
    json.dump(liste, open(os.path.join(aus, "suche.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "sammeln":
        sammeln(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == "regionen":
        regionen(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "", os.environ.get("STAND", ""))
    else:
        sys.exit(__doc__)
