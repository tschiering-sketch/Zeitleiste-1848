// Erzeugt die Druckfassungen (PDF) aus den Daten der App.
// Aufruf: node build_print.js <data.json> <qr.json> <fonts.css> <ausgabeordner>
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [dataFile, qrFile, fontFile, outDir] = process.argv.slice(2);
const D = JSON.parse(fs.readFileSync(dataFile, "utf8"));
const QR = JSON.parse(fs.readFileSync(qrFile, "utf8"));
const FONTS = fs.readFileSync(fontFile, "utf8");
const APP_URL = "https://claude.ai/artifact/Pjn9CkJkeq3C8PqAusxVvD";

const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const kindLabel = { q: "Originalquelle", d: "Darstellung", r: "Rekonstruktion · Spielmaterial" };
const PENALTY = [1, 2, 4];

const CSS = `
${FONTS}
@page{size:A4;margin:16mm 15mm 16mm 15mm}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font-family:"Archivo",Arial,sans-serif;font-size:10.5pt;line-height:1.45;color:#111}
:root{--ink:#111;--ink-soft:#4a4a4a;--paper:#fff;--paper-2:#f4f1ea;--rule:#b9b2a2;--stamp:#a3241b;--folder:#c4943f}
.page{break-after:page}
.page:last-child{break-after:auto}
.doc{font-family:"Courier Prime","Courier New",monospace;font-size:10pt;line-height:1.5}
.doc p+p{margin-top:.5em}
p{margin:0}
.small{font-size:8.5pt;color:var(--ink-soft)}
/* Aktendeckel */
.cover{height:262mm;border:2.5pt solid var(--ink);padding:14mm 12mm;display:flex;flex-direction:column;gap:8mm;position:relative}
.cover .top{display:flex;justify-content:space-between;font-family:"Courier Prime",monospace;font-size:10pt}
.cover .behoerde{font-stretch:75%;font-weight:800;text-transform:uppercase;letter-spacing:.1em;font-size:13pt;border-bottom:1.5pt solid var(--ink);padding-bottom:3mm}
.cover .no{font-family:"Courier Prime",monospace;font-weight:700;font-size:40pt;line-height:1}
.cover h1{font-stretch:72%;font-weight:800;text-transform:uppercase;font-size:38pt;line-height:.95;margin:0}
.cover .sub{font-size:14pt}
.cover .stamp{position:absolute;right:14mm;top:58mm;transform:rotate(-9deg);border:3pt double var(--stamp);color:var(--stamp);font-family:"Courier Prime",monospace;font-weight:700;font-size:18pt;padding:2mm 6mm;letter-spacing:.15em}
.cover table{border-collapse:collapse;width:100%;font-family:"Courier Prime",monospace;font-size:10pt;margin-top:auto}
.cover td{border:1pt solid var(--ink);padding:2mm 3mm;vertical-align:top}
.cover td:first-child{width:38%;font-weight:700}
.cover .auftrag{border:1.5pt solid var(--ink);padding:4mm 5mm;font-size:11.5pt}
/* Materialien */
h2.sec{font-stretch:78%;font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:13pt;border-bottom:1.5pt solid var(--ink);padding-bottom:1.5mm;margin:0 0 4mm}
.mat{border:1pt solid var(--rule);background:var(--paper-2);padding:3.5mm 4.5mm;margin-bottom:4mm;break-inside:avoid}
.mat header{display:flex;justify-content:space-between;gap:4mm;align-items:baseline;margin-bottom:2mm}
.mat .mno{font-family:"Courier Prime",monospace;font-weight:700}
.mat h4{display:inline;font-size:11pt;font-stretch:88%;margin:0}
.kind{font-size:7pt;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:.5mm 1.5mm;white-space:nowrap}
.kind.q{background:#111;color:#fff}.kind.d{border:.8pt solid #444;color:#444}.kind.r{border:.8pt dashed var(--stamp);color:var(--stamp)}
.src{font-size:7.5pt;color:var(--ink-soft);border-top:.6pt solid var(--rule);padding-top:1.5mm;margin-top:2.5mm}
dl.kv{display:grid;grid-template-columns:max-content 1fr;gap:1mm 4mm;margin:0}
dl.kv dt{font-weight:700;font-stretch:88%}dl.kv dd{margin:0}
.photo{display:grid;grid-template-columns:34mm 1fr;gap:4mm;align-items:start}
.photo img{width:34mm;border:1.2mm solid #fff;box-shadow:0 0 0 .4pt #999;filter:sepia(.2)}
.warnbox{border:1.5pt solid var(--stamp);padding:2.5mm 3.5mm;display:grid;gap:1.5mm}
.warnbox b{color:var(--stamp);text-transform:uppercase;letter-spacing:.05em;font-size:8.5pt}
.quote{font-family:"Courier Prime",monospace;border-left:2pt solid #111;padding-left:3mm;margin-top:2mm}
.qrbox{display:flex;gap:3mm;align-items:center;margin-top:2mm}
.qrbox svg{width:22mm;height:22mm}
.qrbox span{font-size:8.5pt}
.telegram{font-family:"Courier Prime",monospace;text-transform:uppercase;border:1pt solid var(--rule);padding:3mm}
ul{margin:0;padding-left:5mm}
/* Karte */
.mapbox svg{width:100%;height:auto;display:block}
.map-bg{fill:#f4f1ea}.map-grid{stroke:#d5cfc0;stroke-width:1}
.region{fill:#777;font-family:Archivo,sans-serif;font-size:15px;font-weight:800;letter-spacing:.3em;opacity:.45}
.city circle{fill:#fff;stroke:#111;stroke-width:2}.city text{fill:#111;font-family:Archivo,sans-serif;font-size:13px;font-weight:600}
.city .hit{fill:transparent}.route{display:none}
/* Arbeitsbogen */
.q{border:1.2pt solid var(--ink);padding:3mm 4.5mm;margin-bottom:4mm;break-inside:avoid}
.q .qn{font-family:"Courier Prime",monospace;font-size:8.5pt;color:var(--ink-soft)}
.q .qt{font-weight:700;margin:1mm 0 2mm}
.opt{display:flex;gap:2.5mm;margin:1.2mm 0}
.box{width:3.6mm;height:3.6mm;border:1pt solid #111;flex:none;margin-top:.8mm}
.lines div{border-bottom:.6pt solid #999;height:8mm}
table.m{border-collapse:collapse;width:100%;font-size:9.5pt}
table.m td,table.m th{border:.8pt solid #999;padding:1.5mm 2mm;vertical-align:top;text-align:left}
.order{list-style:none;margin:0;padding:0}
.order li{display:flex;gap:3mm;margin:1.2mm 0}
.order .nr{width:8mm;height:6mm;border:1pt solid #111;flex:none}
.bonus{border:1.5pt dashed var(--folder);padding:3mm 4.5mm;break-inside:avoid}
.bonus h4{margin:0 0 1.5mm;text-transform:uppercase;letter-spacing:.06em;font-stretch:85%}
.mat.hasfig{break-inside:auto}
/* Telegramm-Blatt */
.sealed .cut{font-family:"Courier Prime",monospace;font-size:9pt;color:#555;text-align:center;margin-bottom:6mm}
.figs{display:flex;gap:4mm}.fig{margin:0;max-width:110mm}.figimg img{width:100%;border:1mm solid #fff;box-shadow:0 0 0 .4pt #999}
.fig figcaption{font-size:8.5pt;color:#4a4a4a;font-family:"Courier Prime",monospace}
.telegram{margin-top:3mm;font-size:11pt}
/* Chiffrierscheibe */
.strip{font-family:"Courier Prime",monospace;font-weight:700;font-size:12pt;letter-spacing:2.6mm;border:1pt dashed #111;padding:2mm 3mm;white-space:nowrap;overflow:hidden}
.cryp{font-family:"Courier Prime",monospace;font-weight:700;font-size:12pt;letter-spacing:.15em;border:1pt dashed #111;padding:3mm;word-break:break-all}
/* Hinweiskarten */
.cards{display:grid;grid-template-columns:1fr 1fr;gap:0}
.card{border:1pt dashed #777;padding:5mm;min-height:62mm;display:flex;flex-direction:column;gap:2mm;break-inside:avoid}
.card .h{display:flex;justify-content:space-between;font-family:"Courier Prime",monospace;font-weight:700}
.card .cost{color:var(--stamp)}
.card .t{font-size:10.5pt}
.card .fold{margin-top:auto;font-size:7.5pt;color:#777}
/* Bericht */
.field{margin-bottom:5mm;break-inside:avoid}
.field b{display:block;font-size:11.5pt}
.field span{font-size:9pt;color:var(--ink-soft)}
.field .lines div{height:9mm}
.head{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2pt solid #111;padding-bottom:2mm;margin-bottom:5mm}
.head h1{font-stretch:75%;font-weight:800;text-transform:uppercase;font-size:24pt;margin:0;line-height:1}
.head .meta{font-family:"Courier Prime",monospace;font-size:9.5pt;text-align:right}
`;

function qrize(html) {
  return html.replace(/<a class="ext" href="([^"]+)"[^>]*>([^<]+)<\/a>/g, (m, url, label) =>
    `<div class="qrbox">${QR[url] || ""}<span><b>${label.replace(" ↗", "")}</b><br>QR-Code mit dem Tablet scannen</span></div>`);
}

function matHTML(m) {
  let body = m.html;
  if (m.no === "4.1") {
    const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    body = `<p>Ein Kurier trug eine Nachricht bei sich. Der Schlüssel ist eine Zahl, die ihr am Tatort gefunden habt. Jeder Buchstabe wurde um diese Zahl im Alphabet <b>nach hinten</b> verschoben.</p>
      <div class="cryp" style="margin:3mm 0">${D.cipher}</div>
      <p class="small">Chiffrierscheibe zum Ausschneiden: Schneidet beide Streifen aus. Legt den unteren Streifen so unter den oberen, dass unter dem Geheimbuchstaben der Klartext steht. Ihr könnt auch die Chiffrierscheibe in der App nutzen.</p>
      <div class="strip" style="margin-top:2mm">${A}</div><div class="strip" style="margin-top:2mm">${A}${A}</div>`;
  }
  body = qrize(body);
  if (m.figs) body += `<div style="display:flex;gap:4mm;flex-wrap:wrap;margin-top:2mm">${m.figs.map(f => f.sensitive
    ? `<div class="warnbox" style="flex:1"><b>Fotos der Leichenschau</b><p>Im Druck nicht abgebildet. Sie sind nur in der App zu sehen, unscharf gestellt und mit Warnhinweis.</p></div>`
    : `<figure style="margin:0;flex:1 1 60mm;max-width:${m.wide && m.figs.length===1 ? "100mm" : "80mm"}"><img src="${D.IMG[f.img]}" style="width:100%;border:1mm solid #fff;box-shadow:0 0 0 .4pt #999"><figcaption class="small" style="font-family:'Courier Prime',monospace">${esc(f.cap)}</figcaption></figure>`).join("")}</div>`;
  if (m.img && D.IMG[m.img] && !D.IMG[m.img].startsWith("__")) body = `<div class="photo"><img src="${D.IMG[m.img]}" alt=""><div>${body}</div></div>`;
  return `<article class="mat${m.figs ? " hasfig" : ""}"><header><div><span class="mno">M ${m.no}</span> <h4>${esc(m.title)}</h4></div><span class="kind ${m.kind}">${kindLabel[m.kind]}</span></header>${body}<div class="src">${esc(m.src)}</div></article>`;
}

const lines = n => `<div class="lines">${"<div></div>".repeat(n)}</div>`;

function qHTML(q, label) {
  let inner = "";
  if (q.type === "choice") inner = q.opts.map(o => `<div class="opt"><span class="box"></span><span>${esc(o)}</span></div>`).join("");
  else if (q.type === "multi") inner = `<p class="small">Mehrere Antworten können richtig sein.</p>` + q.opts.map(o => `<div class="opt"><span class="box"></span><span>${esc(o.t)}</span></div>`).join("");
  else if (q.type === "numbers") inner = q.fields.map(f => `${esc(f.l)}: ______ &nbsp;&nbsp; `).join("");
  else if (q.type === "text" || q.type === "cipher") inner = lines(q.type === "cipher" ? 3 : 1);
  else if (q.type === "order") {
    // gemischte, aber feste Reihenfolge für den Druck
    const idx = q.items.map((_, i) => i).sort((a, b) => ((a * 7 + 3) % q.items.length) - ((b * 7 + 3) % q.items.length));
    inner = `<p class="small">Tragt die Reihenfolge ein (1 = älteste).</p><ol class="order">${idx.map(i => `<li><span class="nr"></span><span>${esc(q.items[i])}</span></li>`).join("")}</ol>`;
  } else if (q.type === "match") inner = `<table class="m"><tr><th>Aussage</th><th style="width:30%">Muster / Person</th></tr>${q.rows.map(r => `<tr><td>${esc(r.t)}</td><td></td></tr>`).join("")}</table><p class="small" style="margin-top:2mm">Zur Auswahl: ${q.cats.map(esc).join(" · ")}</p>`;
  else if (q.type === "route") inner = `<div class="mapbox">${D.map.replace(/<p class="small">.*?<\/p>/, "")}</div><p class="small">Zeichnet den Fluchtweg mit Pfeilen in die Karte ein. Budapest liegt etwa 450 km weiter östlich (Pfeil am rechten Rand).</p>`;
  else if (q.type === "check") inner = `<div class="opt"><span class="box"></span><span>${esc(q.label)}</span></div>`;
  return `<div class="q"><div class="qn">${label}</div><div class="qt">${esc(q.q)}</div>${inner}</div>`;
}

function akteHTML(a) {
  const cover = `<section class="page"><div class="cover">
    <div class="top"><span>Badische Kriminalpolizei</span><span>${esc(a.az)}</span></div>
    <div class="behoerde">Sonderkommission Griesbach · Staatsanwaltschaft Offenburg</div>
    <div class="no">Akte ${a.no}</div><h1>${esc(a.title)}</h1><div class="sub">${esc(a.sub)}</div>
    <div class="stamp">Vertraulich</div>
    <div class="auftrag"><b>Auftrag.</b> ${a.auftrag}</div>
    <table><tr><td>Federführung</td><td>${esc(a.role)}</td></tr><tr><td>Richtzeit</td><td>${a.min} Minuten</td></tr><tr><td>Beweismittel</td><td>${a.mats.map(m => "M " + m.no).join(", ")}</td></tr><tr><td>Funkcode nach Lösung</td><td>wird in der App angezeigt</td></tr><tr><td>Team</td><td>&nbsp;</td></tr></table>
  </div></section>`;
  const mats = `<section class="page"><h2 class="sec">Akte ${a.no} · Beweismittel</h2>${a.mats.map(matHTML).join("")}</section>`;
  const qs = `<section class="page"><h2 class="sec">Akte ${a.no} · Ermittlungsbogen</h2>
    ${a.qs.map((q, i) => qHTML(q, "Ermittlungsfrage " + (i + 1))).join("")}
    ${a.reveal ? `<p class="small">Nach Frage 2 geht das Originaltelegramm vom 24. Juni 1922 ein. Es liegt verschlossen bei (eigenes Blatt) und wird auch in der App angezeigt.</p>` : ""}
    <div class="bonus"><h4>${esc(a.bonus.title)}</h4><p>${a.bonus.intro}</p>${qHTML(a.bonus.q, "Zusatzfrage")}</div></section>`;
  const tele = a.reveal ? `<section class="page"><div class="sealed"><div class="cut">✂ ── Eigenes Blatt / Umschlag: erst öffnen, wenn eure Prognose (Frage 2) steht ──</div>
    <h2 class="sec">Akte ${a.no} · Eingang 24. Juni 1922</h2>
    <article class="mat"><header><div><span class="mno">M ${a.no === "V" ? "5.4" : a.no}</span> <h4>Telegramm aus Berlin an den badischen Staatspräsidenten</h4></div><span class="kind q">Originalquelle</span></header>${a.reveal.html}</article></div></section>` : "";
  return cover + mats + qs + tele;
}

function wrap(title, body) {
  return `<!doctype html><html lang="de"><head><meta charset="utf-8"><title>${title}</title><style>${CSS}</style></head><body>${body}</body></html>`;
}

const intro = `<section class="page"><div class="cover">
  <div class="top"><span>Badische Kriminalpolizei</span><span>Eingang 26. August 1921</span></div>
  <div class="behoerde">Sonderkommission Griesbach</div>
  <h1 style="font-size:44pt">Mord auf der Kniebisstraße</h1>
  <div class="telegram">Reichsfinanzminister a.D. Matthias Erzberger bei Bad Griesbach im Schwarzwald erschossen. Begleiter Abg. Diez schwer verletzt. Zwei Täter flüchtig. Soko Griesbach wird gebildet.</div>
  <div class="stamp" style="top:auto;bottom:118mm;right:10mm">Ermittlungsakten</div>
  <div class="auftrag">Ihr seid die Ermittlerinnen und Ermittler der Sonderkommission. Löst die Akten I bis V der Reihe nach. Antworten gebt ihr in der App ein, die euch Hinweise gibt und die nächste Akte freischaltet. Notizen macht ihr auf den Ermittlungsbögen. Den Bericht an den Staatsanwalt führt eure Aktenführung von Anfang an mit.</div>
  <div class="warnbox"><b>Hinweis zu den Materialien</b><p>Dieser Fall ist echt. Er handelt von Mord, Hass und Antisemitismus. Einige Quellen sind verletzend. Fotos des Toten sind nicht abgedruckt, sondern nur in der App zu sehen, unscharf gestellt und mit Warnhinweis. Wenn euch etwas belastet, sprecht eure Lehrkraft an.</p></div>
  <div class="qrbox">${QR[APP_URL]}<span><b>Zur App „Soko Griesbach“</b><br>QR-Code scannen oder den Link der Lehrkraft nutzen</span></div>
  <table><tr><td>Kennzeichnung</td><td><div style="display:flex;flex-wrap:wrap;gap:2mm"><span class="kind q">Originalquelle</span><span class="kind d">Darstellung</span><span class="kind r">Rekonstruktion · Spielmaterial</span></div></td></tr><tr><td>Team</td><td>&nbsp;</td></tr></table>
</div></section>`;

const akten = wrap("Soko Griesbach – Ermittlungsakten", intro + D.AKTEN.map(akteHTML).join(""));

const cards = D.AKTEN.flatMap(a => a.hints.map((h, k) => `<div class="card"><div class="h"><span>Akte ${a.no} · Hinweis ${k + 1}</span><span class="cost">−${PENALTY[k]} Min.</span></div><div class="t">${esc(h)}</div><div class="fold">Soko Griesbach · Anruf beim Präsidium${k === 2 ? " · enthält den Lösungsweg" : ""}</div></div>`));
const hinweise = wrap("Soko Griesbach – Hinweiskarten", `<section><div class="head"><h1>Hinweiskarten</h1><div class="meta">Für die Lehrkraft · ausschneiden, nach Akte sortieren<br>Nur nötig, wenn ohne App gespielt wird</div></div><div class="cards">${cards.join("")}</div></section>`);

const bericht = wrap("Soko Griesbach – Ermittlungsbericht", `<section><div class="head"><h1>Ermittlungsbericht</h1><div class="meta">An den Herrn Ersten Staatsanwalt, Offenburg<br>Az. St. 1921/26-08 · Soko Griesbach</div></div>
  <p style="margin-bottom:5mm"><b>Team:</b> ______________________________ &nbsp;&nbsp; <b>Aktenführung:</b> ______________________________</p>
  <p class="small" style="margin-bottom:5mm">Schreibt in ganzen Sätzen und nennt eure Beweismittel (z. B. „vgl. M 4.6“). Trennt, was belegt ist, von dem, was umstritten ist.</p>
  ${D.BERICHT.map(f => `<div class="field"><b>${esc(f.l)}</b><span>${esc(f.h)}</span>${lines(f.k === "urteil" ? 6 : 4)}</div>`).join("")}
  <p style="margin-top:6mm">Ort, Datum: ______________________ &nbsp;&nbsp;&nbsp; Unterschriften: ____________________________________________</p></section>`);

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const [name, html] of [["Soko-Griesbach_Ermittlungsakten", akten], ["Soko-Griesbach_Hinweiskarten", hinweise], ["Soko-Griesbach_Ermittlungsbericht", bericht]]) {
    await p.setContent(html, { waitUntil: "load" });
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ path: path.join(outDir, name + ".pdf"), format: "A4", printBackground: true, preferCSSPageSize: true });
    console.log("PDF", name);
  }
  await b.close();
})();
