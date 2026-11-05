# Erde Navi – Kartenpakete

- Öffentliches Repo nur für die Offline-Kartenpakete von Erde Navi (`thowolf/erde-navi`, dort gelten die Regeln).
- Deutsch, Schweizer Schreibweise (ss statt ß), auch in Kommentaren und Commit-Texten.
- Keine Schlüssel, kein App-Code hier. Kartendaten sind ODbL: Quelle „© OpenStreetMap-Mitwirkende“ immer nennen.
- `regionen.json` ist die einzige Liste der Regionen (Kürzel bleiben stabil, Erde Navi speichert sie).
- Format von `pakete.json` nur mit `version` erhöhen ändern – ältere Erde-Navi-Versionen lesen es (und lehnen höhere
  Versionen ab). Zusätzliche, optionale Felder (wie `routen`, `suche`) gehen ohne Erhöhung, weil die App unbekannte Felder überspringt.
- Routendaten: Valhalla-Version im Workflow gleich halten wie `valhalla-mobile` in Erde Navi (sonst passen die Kacheln nicht).
- Suchdaten (`werkzeug/suche.py`): Format über die Tabelle `meta` (version). `vereinfache()` muss genau zu
  `OfflineSuche.vereinfache()` in Erde Navi passen (klein, ohne Akzente, ß → ss), sonst findet die App nichts.
