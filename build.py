"""Baut index.html: bettet Schrift und Logos als data-URIs in src/zeitleiste.html ein."""
import base64
from pathlib import Path

root = Path(__file__).parent
b64 = lambda p: base64.b64encode((root / p).read_bytes()).decode()
html = (root / "src/zeitleiste.html").read_text(encoding="utf-8")
html = (html.replace("{{FONT}}", b64("assets/BriLliant.ttf"))
            .replace("{{LOGO_NAVY}}", b64("assets/logo_navy.png"))
            .replace("{{LOGO_WEISS}}", b64("assets/logo_weiss.png")))
(root / "index.html").write_text(html, encoding="utf-8")
print(f"index.html: {len(html) // 1024} KB")
