# Datenschutzerklärung Erde Navi

[English below](#privacy-policy-erde-navi)

Stand: November 2026

Erde Navi ist eine Navigations-App für Auto, Motorrad, Wohnwagen, Wohnmobil und Lastwagen. Die App hat **kein Konto,
keine Werbung und keine Analyse- oder Tracking-Dienste**. Wir verkaufen keine Daten.

## Was auf deinem Gerät bleibt

- Fahrzeug und Masse, Einstellungen, Zuhause, Favoriten und die zuletzt angefahrenen Ziele
- dein TomTom-Schlüssel, falls du einen einträgst (verschlüsselt im Android Keystore)
- heruntergeladene Offline-Karten

Diese Daten verlassen das Gerät nicht. Sie werden gelöscht, wenn du die App deinstallierst oder ihre Daten löschst.

## Standort

Die App braucht deinen genauen Standort, um zu navigieren (auch im Hintergrund, solange eine Navigation läuft und die
Meldung in der Statusleiste sichtbar ist). Der Standort wird nicht gespeichert und nicht an uns geschickt. Er geht nur
an die unten genannten Dienste, soweit sie ihn für ihre Aufgabe brauchen.

## Dienste, mit denen die App spricht

| Dienst | Wozu | Was übermittelt wird |
|---|---|---|
| Valhalla, FOSSGIS e.V. (Deutschland) | Routen berechnen | Start (dein Standort), Zwischenziele, Ziel, Fahrzeugart und -masse |
| TomTom (nur mit eigenem Schlüssel) | Auto-Routen mit Verkehr, Suche, Verkehrslage | Start, Ziel, Suchtext, ungefährer Standort, dein Schlüssel |
| Photon, komoot (Deutschland) | Suche ohne TomTom | Suchtext, ungefährer Standort für nahe Treffer |
| Overpass API (Deutschland) | „Strecke voraus“ (Ausfahrten, Raststätten) | Verlauf der Route |
| OpenFreeMap | Kartenbild online | angezeigter Kartenausschnitt |
| GitHub (Microsoft) | Offline-Karten herunterladen | Abruf der Kartendatei |
| Google Play-Dienste | Standort des Geräts (Fused Location) | wie in den Bedingungen von Google |

Bei jedem Abruf sehen die Dienste technisch deine IP-Adresse. Es gelten ihre eigenen Datenschutzbestimmungen.

## Android Auto

In Android Auto zeigt die App dieselben Daten wie auf dem Handy. Es werden keine zusätzlichen Daten erhoben.

## Erde-App

Die Erde-App kann ein Ziel, Zwischenziele, das Fahrzeug und auf Wunsch deinen eigenen TomTom-Schlüssel an Erde Navi
übergeben. Das geschieht auf deinem Gerät (Link bzw. QR-Code), nicht über einen Server.

## Kontakt

Fragen über die Issues dieses Repositorys: https://github.com/thowolf/erde-navi-maps/issues

---

# Privacy policy Erde Navi

As of November 2026

Erde Navi is a navigation app for car, motorcycle, caravan, camper and truck. The app has **no account, no ads and no
analytics or tracking**. We do not sell data.

**Stays on your device:** vehicle and dimensions, settings, home, favourites and recent destinations, your TomTom key
if you enter one (encrypted in the Android Keystore), downloaded offline maps. Removed when you uninstall the app or
clear its data.

**Location:** needed to navigate (also in the background while navigation runs and its notification is shown). It is
not stored and not sent to us – only to the services below as far as they need it.

**Services:** Valhalla by FOSSGIS (routing: start, stops, destination, vehicle type and dimensions); TomTom, only with
your own key (car routes with traffic, search, traffic map: start, destination, search text, approximate location, your
key); Photon by komoot (search: text, approximate location); Overpass API (road ahead: route geometry); OpenFreeMap
(map tiles); GitHub (offline map download); Google Play services (device location). All of them see your IP address;
their own privacy policies apply.

**Android Auto** shows the same data as the phone; nothing extra is collected. **The Erde app** can hand over a
destination, stops, vehicle and optionally your own TomTom key on your device (link or QR code), not via a server.

**Contact:** https://github.com/thowolf/erde-navi-maps/issues
