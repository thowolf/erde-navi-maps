// Paketliste (pakete.json) für Erde Navi: Name, Land, Rahmen, Datei, Grösse in Bytes, Datenstand.
import { readFileSync, statSync, writeFileSync, existsSync } from 'node:fs';

const [ordner, stand, quelle] = process.argv.slice(2);
const regionen = JSON.parse(readFileSync('regionen.json', 'utf8'));
const pakete = regionen
  .filter((r) => existsSync(`${ordner}/${r.id}.pmtiles`))
  .map((r) => ({ ...r, datei: `${r.id}.pmtiles`, bytes: statSync(`${ordner}/${r.id}.pmtiles`).size }));
const hilfe = existsSync(`${ordner}/hilfsdateien.zip`) ? statSync(`${ordner}/hilfsdateien.zip`).size : 0;
writeFileSync(`${ordner}/pakete.json`, JSON.stringify({ version: 1, stand, quelle, hilfsdateien: { datei: 'hilfsdateien.zip', bytes: hilfe }, pakete }, null, 1));
for (const p of pakete) console.log(`${p.id.padEnd(6)} ${(p.bytes / 1e6).toFixed(0).padStart(6)} MB  ${p.name}`);
