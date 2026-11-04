# Erde Navi – Kartenpakete

Offline-Karten für [Erde Navi](https://github.com/thowolf/erde-navi): Schweiz, Österreich und die 16 deutschen
Bundesländer einzeln, als [PMTiles](https://docs.protomaps.com/pmtiles/). Ein Workflow schneidet sie einmal im Monat
aus der [Protomaps](https://protomaps.com/)-Weltkarte aus und legt sie als Release **latest** ab:

- `<kürzel>.pmtiles` – die Karte einer Region (Kürzel siehe `regionen.json`)
- `hilfsdateien.zip` – Kartenstil hell/dunkel, Schriften und Symbole, damit die Karte ganz ohne Internet läuft
- `pakete.json` – Liste mit Namen, Rahmen, Grösse und Datenstand, die Erde Navi liest

Von Hand starten: Actions › Kartenpakete › Run workflow (optional nur einzelne Regionen, z. B. `ch,de-be`).

## Lizenzen

- Kartendaten © OpenStreetMap-Mitwirkende, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/)
- Kacheln und Kartenstil: [Protomaps](https://github.com/protomaps/basemaps) (BSD-3-Clause für Code, Daten ODbL)
- Schriften Noto Sans: SIL Open Font License
- Werkzeuge und Workflow in diesem Repo: Apache-2.0, siehe [LICENSE](LICENSE)
