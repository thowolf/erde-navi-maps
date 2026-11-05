# Erde Navi – Kartenpakete

Offline-Karten für [Erde Navi](https://github.com/thowolf/erde-navi): Schweiz, Österreich und die 16 deutschen
Bundesländer einzeln, als [PMTiles](https://docs.protomaps.com/pmtiles/). Ein Workflow schneidet sie einmal im Monat
aus der [Protomaps](https://protomaps.com/)-Weltkarte aus und legt sie als Release **latest** ab:

- `<kürzel>.pmtiles` – die Karte einer Region (Kürzel siehe `regionen.json`)
- `<kürzel>.routen.tar.gz` – Routendaten der Region ([Valhalla](https://github.com/valhalla/valhalla)-Kacheln, nur
  Strassen für Fahrzeuge), damit Erde Navi auch ohne Internet Routen rechnet. Gebaut aus dem Geofabrik-Auszug
  Schweiz/Österreich/Deutschland; Kacheln an Grenzen liegen in beiden Nachbarpaketen.
- `<kürzel>.suche.gz` – Suchdaten der Region (SQLite mit Volltextindex, gzip): Adressen mit Hausnummer, Orte und
  POIs, damit Erde Navi auch ohne Internet Ziele findet. Format in `werkzeug/suche.py`.
- `hilfsdateien.zip` – Kartenstil hell/dunkel, Schriften und Symbole, damit die Karte ganz ohne Internet läuft
- `pakete.json` – Liste mit Namen, Rahmen, Grösse und Datenstand, die Erde Navi liest

Von Hand starten: Actions › Kartenpakete › Run workflow (optional nur einzelne Regionen, z. B. `ch,de-be`, und ohne Routendaten).

## Datenschutz

Die Datenschutzerklärung der App steht in [DATENSCHUTZ.md](DATENSCHUTZ.md) (für den Play Store).

## Lizenzen

- Kartendaten © OpenStreetMap-Mitwirkende, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/)
- Kacheln und Kartenstil: [Protomaps](https://github.com/protomaps/basemaps) (BSD-3-Clause für Code, Daten ODbL)
- Routendaten: gebaut mit Valhalla (MIT), Daten ODbL
- Suchdaten: aus OpenStreetMap (ODbL), gelesen mit pyosmium (BSD-2-Clause)
- Schriften Noto Sans: SIL Open Font License
- Werkzeuge und Workflow in diesem Repo: Apache-2.0, siehe [LICENSE](LICENSE)
