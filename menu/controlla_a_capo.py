#!/usr/bin/env python3
"""
Controlla i menù generati: segnala le righe che contengono una sola parola
(parole rimaste "orfane" a capo) in descrizioni, traduzioni e nomi dei piatti.

Uso: python3 controlla_a_capo.py file.html [file.html ...]
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from a_capo import SISTEMA_A_CAPO_JS

JS = r"""() => {
  const risultati = [];
  const blocchi = document.querySelectorAll('h3, h4, p, li');
  blocchi.forEach(el => {
    if (el.closest('.cop-ill, .qr, .biglietto, .piede')) return;
    if (el.querySelector('p, h3, h4, div, mark')) return;          // contenitori ed evidenziati: si controllano i figli
    // righe del testo (esclusi gli allergeni, che vanno a capo per conto loro)
    const righe = new Map();
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) {
      const n = w.currentNode;
      if (n.parentElement.closest('.all-riga, .al, .chef, .etichetta, .cottura, mark')) continue;
      const parole = n.textContent.split(/(\s+)/);
      let pos = 0;
      for (const p of parole) {
        if (p.trim()) {
          const r = document.createRange(); r.setStart(n, pos); r.setEnd(n, pos + p.length);
          const rect = r.getClientRects()[0];
          if (rect) {
            let y = [...righe.keys()].find(k => Math.abs(k - rect.bottom) < 5);
            if (y === undefined) { y = rect.bottom; righe.set(y, []); }
            righe.get(y).push(p);
          }
        }
        pos += p.length;
      }
    }
    const lista = [...righe.values()];
    if (lista.length > 1) {
      lista.forEach((parole, i) => {
        if (parole.length === 1 && parole[0].length > 1 && !/^[\d,]+$/.test(parole[0]))
          risultati.push(`"${parole[0]}" da sola sulla riga ${i + 1} di: ${el.textContent.trim().slice(0, 70)}…`);
      });
    }
  });
  return risultati;
}"""


def main(files):
    tot = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = b.new_page()
        for f in files:
            pg.goto(Path(f).resolve().as_uri())
            pg.evaluate("document.fonts.ready")
            pg.evaluate(SISTEMA_A_CAPO_JS)          # come nella generazione dei PDF
            res = pg.evaluate(JS)
            print(f"{f}: {len(res)} righe con una parola sola")
            for r in res:
                print("  -", r)
            tot += len(res)
        b.close()
    return tot


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
