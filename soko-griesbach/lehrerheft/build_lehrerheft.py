"""Erzeugt das Lehrerheft (HTML) im Hausstil des Gymnasiums Leopoldinum Passau.
Aufruf: python3 build_lehrerheft.py <data.json> <skill-assets-ordner> <ausgabe.html>
Das PDF entsteht anschließend mit render_pdf.js (Kopf- und Fußzeile)."""
import base64, html, json, sys, pathlib

data_file, assets, out = sys.argv[1:4]
D = json.loads(pathlib.Path(data_file).read_text(encoding="utf-8"))
assets = pathlib.Path(assets)
font_b64 = base64.b64encode((assets / "fonts" / "BriLliant.ttf").read_bytes()).decode()
e = html.escape

CIPHER_PLAIN = "ZENTRALE MUENCHEN TRAUTENWOLFSTRASSE ACHT TARNUNG BAYERISCHE HOLZVERWERTUNGSGESELLSCHAFT"
CITY = {"griesbach": "Bad Griesbach", "muenchen": "München", "salzburg": "Salzburg", "budapest": "Budapest"}


def sol(q):
    t = q["type"]
    if t == "choice":
        return q["opts"][q["a"]]
    if t == "multi":
        return "Richtig: " + " · ".join(o["t"] for o in q["opts"] if o["c"]) + "<br><i>Falsch: " + " · ".join(e(o["t"]) for o in q["opts"] if not o["c"]) + "</i>"
    if t == "numbers":
        return ", ".join(f'{f["l"]}: {f["a"]}' for f in q["fields"])
    if t == "text":
        return " / ".join(a.capitalize() for a in q["accept"])
    if t == "cipher":
        return f"Trautenwolfstraße 8 (Schlüssel 8; Klartext: {CIPHER_PLAIN})"
    if t == "order":
        return " → ".join(f"{i+1}. {x}" for i, x in enumerate(q["items"]))
    if t == "match":
        return "<br>".join(f'{e(r["t"])} → <b>{e(q["cats"][r["a"]])}</b>' for r in q["rows"])
    if t == "route":
        return " → ".join(CITY[c] for c in q["a"])
    if t == "check":
        return "Haken nach Vorlage des Berichts"
    return ""


def sol_html(q):
    s = sol(q)
    return s if q["type"] in ("multi", "match") else e(s)


rows = []
for a in D["AKTEN"]:
    qs = "".join(f'<tr><td>{i+1}</td><td>{e(q["q"])}</td><td>{sol_html(q)}</td></tr>' for i, q in enumerate(a["qs"]))
    qs += f'<tr><td>K</td><td><i>{e(a["bonus"]["title"])}:</i> {e(a["bonus"]["q"]["q"])}</td><td>{sol_html(a["bonus"]["q"])}</td></tr>'
    rows.append(f'''<h3>Akte {a["no"]}: {e(a["title"])}</h3>
<p class="meta">Federführung: {e(a["role"])} · Richtzeit {a["min"]} Min. · Funkcode nach Lösung: <b class="code">{a["code"]}</b></p>
<table class="t"><thead><tr><th style="width:6%">Nr.</th><th style="width:40%">Ermittlungsfrage</th><th>Lösung</th></tr></thead><tbody>{qs}</tbody></table>''')
loesungen = "\n".join(rows)

CSS = f"""
@font-face{{font-family:"BriLliant";src:url(data:font/ttf;base64,{font_b64}) format("truetype")}}
@page{{size:A4;margin:2.5cm 2cm 2cm 2cm}}
body{{font-family:Arial,Helvetica,sans-serif;font-size:11pt;line-height:1.45;color:#222}}
h1,h2,h3{{font-family:"BriLliant",Arial,sans-serif;font-weight:normal;color:#1F3553;margin:0}}
h1{{font-size:22pt;margin-bottom:4mm}}
h2{{font-size:16pt;margin:8mm 0 3mm;border-bottom:1pt solid #1F3553;padding-bottom:1mm;break-after:avoid}}
h3{{font-size:13pt;margin:5mm 0 1.5mm;break-after:avoid}}
p{{margin:0 0 2.5mm}}
.meta{{font-size:9.5pt;color:#1F3553}}
.code{{font-family:"Courier New",monospace;letter-spacing:.08em}}
.info{{background:#EEF1F5;border-left:4pt solid #1F3553;padding:3mm 4mm;margin:3mm 0;break-inside:avoid}}
.info b.k{{color:#1F3553}}
.warn{{border:1.2pt solid #E87722;padding:3mm 4mm;margin:3mm 0;break-inside:avoid}}
table.t{{border-collapse:collapse;width:100%;font-size:9.5pt;margin:2mm 0 4mm}}
table.t th{{background:#1F3553;color:#fff;text-align:left;padding:1.8mm 2mm;font-weight:bold}}
table.t td{{padding:1.6mm 2mm;vertical-align:top;border-bottom:.5pt solid #c9d1dc}}
table.t tbody tr:nth-child(even) td{{background:#EEF1F5}}
table.t tr{{break-inside:avoid}}
ul{{margin:0 0 3mm;padding-left:6mm}}
ol{{margin:0 0 3mm;padding-left:0;list-style:none}}
li{{margin-bottom:1mm}}
.nr{{color:#E87722;font-weight:bold}}
.lead{{font-size:12pt}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:5mm}}
.pb{{break-before:page}}
.small{{font-size:9pt;color:#555}}
"""

H = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Lehrerheft Soko Griesbach</title><style>{CSS}</style></head><body>

<h1>Soko Griesbach: Lehrerheft</h1>
<p class="lead">Escape Room zum Mord an Matthias Erzberger (1921) mit Schwerpunkt auf der Spur der Organisation Consul nach Bayern. Für Geschichte, Jahrgangsstufe 9 (Gymnasium), 90 Minuten, 5–6 Teams zu je 4–5 Schülerinnen und Schülern.</p>

<div class="info"><b class="k">Auf einen Blick</b>
<ul>
<li><b>Format:</b> hybrid. Die Web-App (Codes, Hinweise, Karte, Chiffrierscheibe, Fahndungsuhr) läuft auf mehreren Geräten pro Team. Die gedruckten Ermittlungsakten liegen auf dem Tisch.</li>
<li><b>Rolle der Klasse:</b> Sonderkommission der badischen Kriminalpolizei im August 1921.</li>
<li><b>Kernfrage:</b> Warum entkamen die Täter, obwohl sie schnell bekannt waren?</li>
<li><b>Ergebnis:</b> ein Ermittlungsbericht pro Team. Zum Abschluss folgt eine Lagebesprechung im Plenum mit Bezügen zur Gegenwart (Lübcke, Reker, Hollstein, NSU, Hass im Netz).</li>
<li><b>App-Link:</b> https://claude.ai/artifact/Pjn9CkJkeq3C8PqAusxVvD · <b>Lehrkraft-PIN:</b> 1921</li>
</ul></div>

<h2>1  Ablauf (90 Minuten)</h2>
<table class="t"><thead><tr><th style="width:13%">Zeit</th><th style="width:22%">Phase</th><th>Inhalt und Lehrkraft</th></tr></thead><tbody>
<tr><td>0–5′</td><td>Alarm</td><td>Telegramm vorlesen, Inhaltswarnung (siehe 6), Rollen verteilen, Teamnamen eintragen. Alle Teams starten die Fahndungsuhr gleichzeitig (70 Min.).</td></tr>
<tr><td>5–17′</td><td>Akte I: Der Tatort</td><td>Tathergang, Täterzahl, Planung (Meldezettel Ulm, Anfragen in Beuron). Leitung: Spurensicherung.</td></tr>
<tr><td>17–29′</td><td>Akte II: Opfer und Motiv</td><td>Waffenstillstand, Dolchstoßlegende, Helfferich-Kampagne, Attentat Hirschfeld, Reichstagsrede 1921, Hetze 1921 und heute (Lübcke). Leitung: Quellenanalyse.</td></tr>
<tr><td>29–42′</td><td>Akte III: Fahndung</td><td>Identität der Täter, Marine-Brigade Ehrhardt, Leibwächter in Regensburg, Fluchtweg auf der Karte. Leitung: Fahndung.</td></tr>
<tr><td>42–54′</td><td>Akte IV a: Das Netzwerk in München</td><td>Chiffre (Schlüssel 8), O.C.-Zentrale Trautenwolfstraße 8, Organigramm, Strategie. Alle Rollen.</td></tr>
<tr><td>54–65′</td><td>Akte IV b: Die schützende Hand</td><td>Pöhner, Pässe, Ordnungszelle, Kahr, Freispruch Killinger, Urteil zum Scheitern der Ermittlungen. Alle Rollen.</td></tr>
<tr><td>65–75′</td><td>Akte V: Abschluss und neue Spur</td><td>Bericht abgeben, Prognose, Telegramm vom 24.6.1922 (Rathenau), Gemeinsamkeiten der Opfer. Leitung: Aktenführung.</td></tr>
<tr><td>75–90′</td><td>Lagebesprechung</td><td>Im Lehrkraft-Modus über den Beamer öffnen: Was aus den Tätern wurde, Ergebnis Bayern, Zeitsprung, Mustervergleich, Urteilsfragen.</td></tr>
</tbody></table>
<p class="small">Puffer: Wenn die Zeit knapp wird, können die Kriminalrat-Akten entfallen, außerdem Akte II, Frage 3 (Zuordnung). Teams, die zurückliegen, bekommen den Funkcode der nächsten Akte von der Lehrkraft. Sehr schnelle Teams lösen die Kriminalrat-Akten.</p>

<h2>2  Lehrplanbezug und Kompetenzen</h2>
<p>LehrplanPLUS Gymnasium Bayern, Geschichte 9, Lernbereich zur Weimarer Republik: Belastungen der jungen Demokratie, politische Gewalt von rechts, Dolchstoßlegende, Versailler Vertrag, Haltung Bayerns gegenüber dem Reich. <i>Bitte die genaue Lernbereichsbezeichnung und Formulierung im aktuellen Lehrplan abgleichen.</i></p>
<table class="t"><thead><tr><th style="width:30%">Kompetenz</th><th>Umsetzung im Spiel</th></tr></thead><tbody>
<tr><td>Orientierung in Zeit und Raum</td><td>Rekonstruktion der Verfolgung und Flucht (Ordnungsaufgaben, Karte), Zeitleiste 1918–1958</td></tr>
<tr><td>Methodenkompetenz</td><td>Unterscheidung von Quelle, Darstellung und Rekonstruktion (Kennzeichnung jedes Materials), Quellenkritik (Kriminalrat II: Wer ist der Redner?), Auswertung von Fahndungsblättern und Satzung</td></tr>
<tr><td>Urteilskompetenz</td><td>Sachurteil: Warum scheiterten die Ermittlungen? Werturteil: Mitverantwortung der Hetzer, „erst Deutsche und dann Beamte“, Umgang mit Hetze heute</td></tr>
<tr><td>Narrative Kompetenz</td><td>Ermittlungsbericht: eine belegte, gegliederte Darstellung mit Unterscheidung von „belegt“ und „umstritten“ (Germanenorden)</td></tr>
<tr><td>Grundlegende Begriffe</td><td>Dolchstoßlegende, „Novemberverbrecher“, Erfüllungspolitik, Freikorps, Kapp-Putsch, Fememord, Organisation Consul, Ordnungszelle Bayern, Republikschutzgesetz</td></tr>
</tbody></table>
<p><b>Operatoren in den Aufgaben:</b> rekonstruieren, ordnen, zuordnen, entschlüsseln, vergleichen, beurteilen, Stellung nehmen.</p>

<h2>3  Vorbereitung</h2>
<ol>
<li><span class="nr">1</span> <b>App freigeben:</b> Der Link ist zunächst privat. Über „Teilen“ auf der Artifact-Seite für die Klasse freigeben (öffentlicher Link) und als QR-Code an die Wand projizieren. Das Deckblatt der Akten enthält bereits einen QR-Code zum Link. Als Alternative ohne Freigabe kann die Datei <i>soko-griesbach.html</i> auf die Schulgeräte kopiert und im Browser geöffnet werden.</li>
<li><span class="nr">2</span> <b>Drucken pro Team:</b> <i>Soko-Griesbach_Ermittlungsakten.pdf</i> (28 S., farbig oder s/w) und <i>Soko-Griesbach_Ermittlungsbericht.pdf</i> (2 S.). Für jede Akte empfiehlt sich ein eigener Umschlag (Deckblatt, Beweismittel, Ermittlungsbogen), der erst bei Freischaltung geöffnet wird.</li>
<li><span class="nr">3</span> <b>Hinweiskarten</b> (<i>Soko-Griesbach_Hinweiskarten.pdf</i>) nur dann ausdrucken und schneiden, wenn ohne App gespielt wird oder die Technik ausfällt.</li>
<li><span class="nr">4</span> <b>Geräte testen:</b> App einmal auf einem Schülergerät öffnen. Der Spielstand wird pro Gerät im Browser gespeichert. Nach der Stunde im Lehrkraft-Modus „Gerät zurücksetzen“ wählen.</li>
<li><span class="nr">5</span> <b>Beamer:</b> Auf dem Lehrer-PC App öffnen, „Lehrkraft“ wählen, PIN 1921 eingeben. Dort stehen alle Lösungen und Funkcodes, und die Lagebesprechung lässt sich direkt öffnen.</li>
</ol>

<h2>4  Technik in der Stunde</h2>
<ul>
<li><b>Mehrere Geräte pro Team:</b> Jedes Gerät hat seinen eigenen Stand. Sobald ein Gerät eine Akte löst, erscheint ein <b>Funkcode</b>. Die anderen Geräte geben ihn über „Funkcode eingeben“ ein und sind auf demselben Stand.</li>
<li><b>Hinweise:</b> drei Stufen pro Akte, kosten 1, 2 bzw. 4 Minuten. Stufe 3 enthält den Lösungsweg.</li>
<li><b>Fahndungsuhr:</b> 70 Minuten. Bei Ablauf erscheint „Die Täter sind über die Grenze“, das Spiel läuft aber weiter. Es gibt keine Rangliste, sondern einen gemeinsamen Countdown.</li>
<li><b>Fotos:</b> Porträts von Erzberger, Helfferich, Kahr und Rathenau sind eingebettet. Andere Fotos (Tatortfoto, Tillessen, Pöhner, Ehrhardt, Brigade Ehrhardt) öffnen sich über Links bzw. QR-Codes bei Wikimedia Commons. Die Geräte brauchen dafür Internet.</li>
</ul>

<h2 class="pb">5  Lösungen und Funkcodes</h2>
{loesungen}

<h2 class="pb">6  Inhaltswarnung und Umgang mit Belastung</h2>
<div class="warn"><b>Vorschlag zum Vorlesen:</b> „Wir ermitteln heute in einem echten Mordfall. Ihr werdet Quellen lesen, die voller Hass und Antisemitismus sind, und ein Polizeifoto des Toten ist verlinkt. Das Foto müsst ihr nicht öffnen, für die Lösung braucht ihr es nicht. Wenn euch etwas belastet, gebt mir ein Zeichen.“</div>
<ul>
<li>Das <b>Tatortfoto</b> (Polizei 1921, gemeinfrei) ist nur über einen Link mit Warnhinweis erreichbar und nicht im Druck abgebildet.</li>
<li>Der antisemitische Hetzvers in M 5.2 ist gerahmt und eingeordnet. Bitte in der Lagebesprechung ausdrücklich als Beispiel für Antisemitismus thematisieren und nicht vorlesen lassen.</li>
<li>Beim Gegenwartsbezug können Schülerinnen und Schüler mit eigenen Erfahrungen von Rassismus oder Bedrohung im Netz betroffen sein. Daher auf Freiwilligkeit achten. Auf Unterstützungsangebote (Vertrauenslehrkraft, Schulpsychologie) hinweisen.</li>
</ul>

<h2>7  Erwartungshorizont Ermittlungsbericht</h2>
<table class="t"><thead><tr><th style="width:24%">Abschnitt</th><th>Erwartet</th></tr></thead><tbody>
<tr><td>1. Tathergang</td><td>26.8.1921, späterer Vormittag, Kniebisstraße bei Bad Griesbach, Spaziergang mit Carl Diez. Zwei Täter, acht Treffer, tödliche Kopfschüsse, Diez schwer verletzt. Geplante Tat (Verfolgung, falsche Namen, Nachfragen in Beuron).</td></tr>
<tr><td>2. Täter und Auftraggeber</td><td>Heinrich Tillessen und Heinrich Schulz, ehemalige Offiziere, Marine-Brigade Ehrhardt, Kapp-Putsch, O.C. Den Auftrag gab Manfred von Killinger (militärische Abteilung der O.C.), nach Sabrow mit Billigung Ehrhardts. Die Rolle des Germanenordens ist umstritten (Sabrow und Gebhardt).</td></tr>
<tr><td>3. Motiv</td><td>Erzberger als „Novemberverbrecher“ (Waffenstillstand 1918, Dolchstoßlegende), Finanzreform, Rufmordkampagne Helfferichs, erstes Attentat 1920. Politisches Ziel der O.C.: Unruhen provozieren, Staatsstreich, Diktatur.</td></tr>
<tr><td>4. Spur nach Bayern</td><td>Zentrale in der Trautenwolfstraße 8 in München (Tarnfirma), Leibwächter-Stelle in Regensburg, Flucht über München. Die Münchner Polizei unter Pöhner (Frick, politische Abteilung) warnte die Täter und stellte Pässe aus. Kahr verweigerte die Republikschutz-Verordnung („Ordnungszelle“).</td></tr>
<tr><td>5. Urteil</td><td>Die Ermittlungen scheiterten nicht an fehlenden Spuren, sondern an der Deckung durch Teile von Staat und Justiz in Bayern, an der verweigerten Auslieferung durch Ungarn und am Freispruch Killingers. Bewertung: Die Feinde der Republik saßen auch in ihren eigenen Behörden („Republik ohne Republikaner“).</td></tr>
<tr><td>6. Prognose</td><td>Die O.C. besteht weiter, weitere Anschläge sind zu erwarten (z. B. auf „Erfüllungspolitiker“ wie Rathenau).</td></tr>
</tbody></table>
<p class="small">Bewertungsvorschlag (optional, z. B. als mündliche Note für das Team): Sachrichtigkeit 40 %, Belege mit M-Nummern 20 %, Unterscheidung von belegt und umstritten 15 %, Begründetheit des Urteils 25 %.</p>

<h2>8  Moderation der Lagebesprechung</h2>
<ol>
<li><span class="nr">1</span> <b>Auflösung (3′):</b> Zeitleiste vorlesen lassen. Impuls: „Wer wurde zur Rechenschaft gezogen, und wann?“ Erwartet: erst 1947 bzw. 1950. Die NS-Amnestie von 1933 schützte die Täter, die Justiz der Nachkriegszeit hob sie auf.</li>
<li><span class="nr">2</span> <b>Bayern (3′):</b> Die Teams nennen ihr Urteil aus dem Bericht (Abschnitt 5). Wichtig ist die Einordnung: „Bayern“ meint hier Teile von Regierung, Polizei und Justiz, nicht die ganze Bevölkerung. Die BVP entzog Kahr 1921 die Unterstützung.</li>
<li><span class="nr">3</span> <b>Zeitsprung (4′):</b> Die Karten Lübcke, Reker, Hollstein, NSU und Hass im Netz kurz vorstellen. Bayern-Bezug: Fünf der zehn NSU-Morde geschahen in Nürnberg und München, der NSU-Prozess fand vor dem OLG München statt.</li>
<li><span class="nr">4</span> <b>Muster (2′):</b> Tabelle 1921 und heute. Unterschied deutlich machen: Heute werden die Täter verurteilt, und die Debatte betrifft Versäumnisse der Behörden (NSU), nicht deren offene Deckung.</li>
<li><span class="nr">5</span> <b>Urteilsfragen (3′):</b> eine Frage auswählen, Blitzlicht oder Think-Pair-Share.</li>
</ol>

<h2 class="pb">9  Quellen, Bildnachweis und Hinweise zur Prüfung</h2>
<h3>Forschungsliteratur</h3>
<ul>
<li>Cord Gebhardt: Der Fall des Erzberger-Mörders Heinrich Tillessen. Ein Beitrag zur Justizgeschichte nach 1945, Tübingen 1995 (Tathergang S. 42–48, Germanenorden S. 54, Verfahren S. 31–37).</li>
<li>Martin Sabrow: Der Rathenaumord. Rekonstruktion einer Verschwörung gegen die Republik von Weimar, München 1994 (Flucht, Pässe, Killinger S. 19–27, 50–55).</li>
<li>Martin Sabrow: Organisation Consul (O.C.), 1920–1922, in: Historisches Lexikon Bayerns (Zentrale Trautenwolfstraße 8, Tarnfirma, Duldung durch Pöhner).</li>
<li>Christopher Dowe: Matthias Erzberger. Ein Leben für die Demokratie, Stuttgart 2011 (Umsturzstrategie S. 149).</li>
<li>Lexikon der Politischen Strafprozesse: „Erzberger-Attentat“ (Pässe durch Pöhner, Begleitung durch den Salzburger Polizeipräsidenten, Killinger-Prozess).</li>
<li>Günter Randecker: Erzberger-Attentäter schmiedeten die Mordpläne auch von Ulm aus, Schwäbische Zeitung, 24.8.2021 (Meldezettel, Beuron, Geheimstatut).</li>
<li>Artikel der deutschsprachigen Wikipedia zu Erzberger, Tillessen, Schulz, Killinger, Pöhner, Organisation Consul, Ordnungszelle, Republikschutzgesetz, Rathenau, Mordfall Walter Lübcke, Henriette Reker und NSU (abgerufen am 27.10.2026). Sie dienen nur als Zugang, die Fakten wurden an den dort genannten Belegen festgemacht.</li>
</ul>
<h3>Originalquellen</h3>
<ul>
<li>Reichstagsrede vom 27.9.1921: Verhandlungen des Reichstags, I. Wahlperiode, Bd. 351, 134. Sitzung, S. 4568 f., online in GHDI, Dokument 4619.</li>
<li>Satzung der O.C. (Zitate) nach Wikipedia „Organisation Consul“, Hitler-Zitat zu Pöhner und Frick nach Wikipedia „Ernst Pöhner“.</li>
</ul>
<h3>Bilder</h3>
<ul>
<li>Erzberger, Helfferich, Rathenau: Bain News Service, Library of Congress (George Grantham Bain Collection), keine bekannten Rechte. Kahr: Artur Braun 1920, gemeinfrei (Wikimedia Commons).</li>
<li>Nur verlinkt: Tatortfoto 1921 (Busam, Oberkirch, gemeinfrei), Tillessen 1921 (Spaarnestad, gemeinfrei), Pöhner (gemeinfrei), Ehrhardt 1920 (Nationaal Archief, gemeinfrei), Brigade Ehrhardt (Bundesarchiv Bild 119-1983-0012, CC BY-SA 3.0 DE).</li>
</ul>
<h3>Kennzeichnung und offene Punkte</h3>
<div class="info">
<ul>
<li><b>Rekonstruktion bzw. Spielmaterial</b> (in Gestaltung oder Wortlaut nachgestellt, inhaltlich belegt): Fernspruch 1.1, Aussage Diez 1.2, Tatortskizze 1.5, Meldezettel 1.6 (Inhalt belegt, Gestaltung nachgestellt), Chiffre 4.1 (frei erfunden; belegt ist nur, dass chiffrierte Anweisungen gefunden wurden), Telegramm vom 24.6.1922.</li>
<li><b>Redner am 27.9.1921:</b> GHDI nennt Reichspräsident Ebert. Der Text selbst („Ich eröffne die erste Sitzung …“, „Vorsitzenden dieses Hauses“) weist auf Reichstagspräsident Paul Löbe hin. Diese Zuschreibung ergibt sich aus dem Text, bitte vor dem Einsatz im Original (Reichstagsprotokolle online) gegenprüfen.</li>
<li><b>Nur über eine Quelle belegt:</b> das Geheimstatut „Verräter verfallen der Feme“ (Randecker 2021) und die Begleitung durch den Salzburger Polizeipräsidenten (Lexikon der Politischen Strafprozesse).</li>
<li><b>Hetzvers zu Rathenau:</b> vielfach zitiert. Die Seitenangabe bei Sabrow 1999 wurde nicht am Original geprüft.</li>
<li><b>BKA-Zahl 2024</b> (84.172 PMK-Straftaten) nach ZDFheute. Vor dem Einsatz aktuelle Zahlen prüfen, inzwischen liegt die Statistik 2025 vor (85.837).</li>
</ul></div>
</body></html>"""
pathlib.Path(out).write_text(H, encoding="utf-8")
print("ok", out)
