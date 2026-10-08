#!/usr/bin/env python3
"""
Estrae dal file Illustrator (.ai, compatibile PDF) solo il logo: sigillo + "RISTORANTE CUSIN",
senza i riquadri dei colori, le note e il motto. Scrive SVG, PDF e PNG trasparente
nel colore originale (champagne) e in versione monocromatica scura.

Uso: python3 -I estrai_logo.py <file.ai> <cartella_uscita>
"""
import sys
from pathlib import Path

import pymupdf

COLORI = {"champagne": "#DEC38D", "scuro": "#191919"}
CHAMPAGNE = (0.868, 0.766, 0.554)   # colore dei tracciati del logo nel file


def e_logo(dr):
    """I tracciati del logo sono quelli color champagne con molti segmenti (i riquadri colore ne hanno uno)."""
    f = dr.get("fill")
    return f is not None and len(dr["items"]) > 3 and all(abs(a - b) < .03 for a, b in zip(f, CHAMPAGNE))


def percorso(dr):
    d, ultimo = [], None
    for it in dr["items"]:
        tipo = it[0]
        if tipo == "re":
            r = it[1]
            d.append(f"M{r.x0:.3f} {r.y0:.3f}H{r.x1:.3f}V{r.y1:.3f}H{r.x0:.3f}Z")
            ultimo = None
            continue
        if tipo == "qu":
            q = it[1]
            d.append("M" + " L".join(f"{p.x:.3f} {p.y:.3f}" for p in (q.ul, q.ur, q.lr, q.ll)) + "Z")
            ultimo = None
            continue
        inizio = it[1]
        if ultimo is None or abs(inizio.x - ultimo.x) > 1e-3 or abs(inizio.y - ultimo.y) > 1e-3:
            if d and ultimo is not None:
                d.append("Z")
            d.append(f"M{inizio.x:.3f} {inizio.y:.3f}")
        if tipo == "l":
            p = it[2]
            d.append(f"L{p.x:.3f} {p.y:.3f}")
        elif tipo == "c":
            c1, c2, p = it[2], it[3], it[4]
            d.append(f"C{c1.x:.3f} {c1.y:.3f} {c2.x:.3f} {c2.y:.3f} {p.x:.3f} {p.y:.3f}")
        ultimo = p
    d.append("Z")
    return "".join(d)


def main(sorgente, uscita):
    uscita.mkdir(parents=True, exist_ok=True)
    pagina = pymupdf.open(sorgente)[0]
    disegni = [dr for dr in pagina.get_drawings() if e_logo(dr)]
    box = disegni[0]["rect"]
    for dr in disegni[1:]:
        box |= dr["rect"]
    m = 4
    x0, y0, w, h = box.x0 - m, box.y0 - m, box.width + 2 * m, box.height + 2 * m
    sigillo = [dr for dr in disegni if dr["rect"].y1 < 400]          # il monogramma sta sopra il nome
    for nome, colore in COLORI.items():
        for parte, gruppo in (("completo", disegni), ("sigillo", sigillo)):
            b = gruppo[0]["rect"]
            for dr in gruppo[1:]:
                b |= dr["rect"]
            bx, by, bw, bh = b.x0 - m, b.y0 - m, b.width + 2 * m, b.height + 2 * m
            paths = "".join(
                f'<path d="{percorso(dr)}" fill-rule="{"evenodd" if dr.get("even_odd") else "nonzero"}"/>'
                for dr in gruppo)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bx:.2f} {by:.2f} {bw:.2f} {bh:.2f}" '
                   f'width="{bw:.2f}" height="{bh:.2f}"><g fill="{colore}">{paths}</g></svg>')
            base = uscita / f"logo_cusin_{parte}_{nome}"
            base.with_suffix(".svg").write_text(svg)
            # PDF vettoriale e PNG trasparente ad alta risoluzione
            doc = pymupdf.open("svg", svg.encode())
            pdf = pymupdf.open("pdf", doc.convert_to_pdf())
            pdf.save(base.with_suffix(".pdf"))
            pdf[0].get_pixmap(dpi=600, alpha=True).save(base.with_suffix(".png"))
            print("creato", base.name, f"({bw:.0f}×{bh:.0f} pt)")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
