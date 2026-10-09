#!/usr/bin/env python3
"""
Genera i due PDF del menù da sorgenti/menu.html nell'ambiente cloud di Claude Code,
dove Chrome non raggiunge direttamente Google Fonts: i caratteri vengono scaricati
dal proxy e passati alla pagina. Sul Mac si usa invece ./genera.sh.

    pdf/Menu-Autunno-2026_Schermo.pdf   avorio simulato, per vederlo a video
    pdf/Menu-Autunno-2026_Stampa.pdf    senza fondo, per la carta avorio

Uso: python3 genera_cloud.py
"""
import os
import ssl
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

QUI = Path(__file__).resolve().parent
CA = "/root/.ccr/ca-bundle.crt"
SSL = ssl.create_default_context(cafile=CA if os.path.exists(CA) else None)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/141 Safari/537.36"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def scarica(route):
    req = urllib.request.Request(route.request.url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=SSL, timeout=30) as r:
        route.fulfill(status=r.status, body=r.read(),
                      headers={"content-type": r.headers.get("content-type", ""), "access-control-allow-origin": "*"})


def main():
    (QUI / "pdf").mkdir(exist_ok=True)
    url = (QUI / "sorgenti" / "menu.html").as_uri()
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        for query, nome in (("?schermo", "Menu-Autunno-2026_Schermo.pdf"), ("", "Menu-Autunno-2026_Stampa.pdf")):
            pg = b.new_page()
            pg.route("https://fonts.googleapis.com/**", scarica)
            pg.route("https://fonts.gstatic.com/**", scarica)
            pg.goto(url + query)
            pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready")
            caricati = pg.evaluate("[...document.fonts].filter(f => f.status == 'loaded').length")
            if not caricati:
                raise SystemExit("STOP: i caratteri di Google Fonts non si sono caricati")
            pg.pdf(path=str(QUI / "pdf" / nome), prefer_css_page_size=True, print_background=True)
            pg.close()
            print("creato pdf/" + nome)
        b.close()


if __name__ == "__main__":
    main()
