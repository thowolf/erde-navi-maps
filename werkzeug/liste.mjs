// Paketliste (pakete.json) für Erde Navi: Name, Land, Rahmen, Datei, Grösse in Bytes, Datenstand.
// Routendaten (falls gebaut) stehen pro Paket unter „routen“ (Datei, Download-Bytes, entpackte Bytes).
// Suchdaten (Adressen, Orte, POIs) ebenso unter „suche“.
// „routen“ und „suche“ sind zusätzliche Felder: ältere Erde-Navi-Versionen überspringen sie, darum bleibt version 1.
import { readFileSync, statSync, writeFileSync, existsSync } from 'node:fs';

const [ordner, stand, quelle] = process.argv.slice(2);
const regionen = JSON.parse(readFileSync('regionen.json', 'utf8'));
const lies = (n) => (existsSync(`${ordner}/${n}`) ? JSON.parse(readFileSync(`${ordner}/${n}`, 'utf8')) : {});
const routen = lies('routen.json');
const suche = lies('suche.json');
const pakete = regionen
  .filter((r) => existsSync(`${ordner}/${r.id}.pmtiles`))
  .map((r) => {
    const p = { ...r, datei: `${r.id}.pmtiles`, bytes: statSync(`${ordner}/${r.id}.pmtiles`).size };
    const rt = routen[r.id];
    if (rt && existsSync(`${ordner}/${rt.datei}`)) p.routen = { datei: rt.datei, bytes: rt.bytes, entpackt: rt.entpackt };
    const su = suche[r.id];
    if (su && existsSync(`${ordner}/${su.datei}`)) p.suche = { datei: su.datei, bytes: su.bytes, entpackt: su.entpackt };
    return p;
  });
const hilfe = existsSync(`${ordner}/hilfsdateien.zip`) ? statSync(`${ordner}/hilfsdateien.zip`).size : 0;
writeFileSync(`${ordner}/pakete.json`, JSON.stringify({ version: 1, stand, quelle, hilfsdateien: { datei: 'hilfsdateien.zip', bytes: hilfe }, pakete }, null, 1));
for (const p of pakete) {
  const r = p.routen ? `  Routen ${(p.routen.bytes / 1e6).toFixed(0).padStart(5)} MB` : '';
  const s = p.suche ? `  Suche ${(p.suche.bytes / 1e6).toFixed(0).padStart(4)} MB` : '';
  console.log(`${p.id.padEnd(6)} ${(p.bytes / 1e6).toFixed(0).padStart(6)} MB${r}${s}  ${p.name}`);
}
