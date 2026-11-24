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
- Tabelle `info` (Zusatzangaben zu POIs, JSON aus `INFO_SCHLUESSEL`) ist optional: Schlüsselliste gleich halten wie
  `OrtInfo.SCHLUESSEL` in Erde Navi. Ältere App-Versionen lesen die Tabelle nicht und stören sich nicht daran.
- Modelle: `.github/workflows/models.yml` (manuell, Secret `HF_TOKEN`) spiegelt EmbeddingGemma 300M in das Release `modelle` (mit `--latest=false`, damit das Karten-Release `latest` unangetastet bleibt).
- Cloudflare R2 CDN: Workflows upload map packages to `https://cdn.erde.holostudio.ch/maps/latest/` (`karten.yml`, plus manual backfill from the `latest` release via `.github/workflows/r2-sync.yml`; `pakete.json` is always uploaded last with `max-age=300`) and EmbeddingGemma 300M to `https://cdn.erde.holostudio.ch/models/embeddinggemma-300m/` (`models.yml`), using repository secrets `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT`, and `R2_BUCKET`.
