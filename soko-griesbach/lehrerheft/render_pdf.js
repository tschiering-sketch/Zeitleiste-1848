// Rendert das Lehrerheft mit Kopf- und Fußzeile im Leopoldinum-Hausstil.
// Aufruf: node render_pdf.js <lehrerheft.html> <logo_navy.png> <ausgabe.pdf>
const fs = require("fs");
const { chromium } = require("playwright");
const [src, logo, out] = process.argv.slice(2);
const logoUri = "data:image/png;base64," + fs.readFileSync(logo).toString("base64");
const header = `<div style="width:100%;margin:0 2cm;font-family:Arial,sans-serif;font-size:9pt;color:#1F3553;display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1pt solid #E87722;padding-bottom:4px;-webkit-print-color-adjust:exact">
  <span>Geschichte · Jahrgangsstufe 9 · Soko Griesbach (Lehrerheft)</span><img src="${logoUri}" style="height:1.2cm"></div>`;
const footer = `<div style="width:100%;margin:0 2cm;font-family:Arial,sans-serif;font-size:8pt;color:#666;display:flex;justify-content:space-between;border-top:.5pt solid #1F3553;padding-top:3px">
  <span>Gymnasium Leopoldinum Passau</span><span>Seite <span class="pageNumber"></span> von <span class="totalPages"></span></span></div>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto("file://" + require("path").resolve(src)); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: out, format: "A4", printBackground: true, displayHeaderFooter: true, headerTemplate: header, footerTemplate: footer,
    margin: { top: "2.5cm", bottom: "2cm", left: "2cm", right: "2cm" } });
  await b.close(); console.log("PDF", out);
})();
