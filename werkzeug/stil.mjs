// Kartenstil (MapLibre) für die Offline-Pakete, aus @protomaps/basemaps erzeugt: hell und dunkel, Beschriftung deutsch.
// Platzhalter, die Erde Navi beim Laden ersetzt: {PMTILES} (Pfad zur Kartendatei), {GLYPHS} und {SPRITE} (Ordner der Hilfsdateien).
import { layers, namedFlavor } from '@protomaps/basemaps';
import { writeFileSync } from 'node:fs';

const ziel = process.argv[2] || '.';
for (const flavor of ['light', 'dark']) {
  const stil = {
    version: 8,
    glyphs: '{GLYPHS}/{fontstack}/{range}.pbf',
    sprite: `{SPRITE}/${flavor}`,
    sources: {
      protomaps: {
        type: 'vector',
        url: '{PMTILES}',
        attribution: '© OpenStreetMap-Mitwirkende · Protomaps',
      },
    },
    layers: layers('protomaps', namedFlavor(flavor), { lang: 'de' }),
  };
  writeFileSync(`${ziel}/stil-${flavor}.json`, JSON.stringify(stil));
  console.log(`stil-${flavor}.json: ${stil.layers.length} Ebenen`);
}
