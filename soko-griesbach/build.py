"""Baut soko-griesbach.html: setzt die Bilder (Base64) in die Vorlage src/app.html ein."""
import json, pathlib
root = pathlib.Path(__file__).parent
html = (root / "src" / "app.html").read_text(encoding="utf-8")
imgs = json.loads((root / "src" / "imgs.json").read_text())
for k, v in imgs.items():
    html = html.replace(f"__IMG_{k}__", v)
(root / "soko-griesbach.html").write_text(html, encoding="utf-8")
print("ok", len(html) // 1024, "KB")
