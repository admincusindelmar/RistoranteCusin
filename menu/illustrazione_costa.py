"""
Illustrazione di copertina: costa toscana disegnata come a penna e inchiostro.

Scogliera con due pini marittimi a ombrello, isola all'orizzonte, una vela lontana e il mare.
I tratti hanno spessore variabile (si assottigliano alle estremità come un pennino) e le ombre
sono rese con tratteggio e tratteggio incrociato, ritagliati sulle forme.
"""
import math
import random

from shapely.geometry import LineString, Polygon
from shapely import affinity

INCHIOSTRO = "#262626"
rnd = random.Random(7)  # seme fisso: il disegno è sempre identico


# --- strumenti di base -------------------------------------------------------

def bezier(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def catena(*curve):
    pts = []
    for c in curve:
        pts.extend(c if not pts else c[1:])
    return pts


def penna(pts, larg=0.9, punta=0.08, tremolio=0.0):
    """Tratto di pennino: nastro pieno che si assottiglia alle estremità."""
    if len(pts) < 2:
        return ""
    n = len(pts)
    sx, dx = [], []
    for i, (x, y) in enumerate(pts):
        x0, y0 = pts[max(i - 1, 0)]
        x1, y1 = pts[min(i + 1, n - 1)]
        tx, ty = x1 - x0, y1 - y0
        lun = math.hypot(tx, ty) or 1
        nx, ny = -ty / lun, tx / lun
        u = i / (n - 1)
        w = punta + (larg - punta) * (math.sin(math.pi * u) ** 0.55)
        if tremolio:
            w *= 1 + rnd.uniform(-tremolio, tremolio)
        sx.append((x + nx * w / 2, y + ny * w / 2))
        dx.append((x - nx * w / 2, y - ny * w / 2))
    poli = sx + dx[::-1]
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in poli) + "Z"


def linea_mossa(x0, y0, x1, y1, n=8, ondula=0.25):
    """Segmento leggermente irregolare, come tracciato a mano libera."""
    pts = []
    for i in range(n + 1):
        u = i / n
        pts.append((x0 + (x1 - x0) * u + rnd.uniform(-ondula, ondula) * .3,
                    y0 + (y1 - y0) * u + math.sin(u * math.pi) * rnd.uniform(-ondula, ondula)))
    return pts


def tratteggio(forma, angolo, passo, larg=0.35, accorcia=0.25, salto=0.0):
    """Linee parallele ritagliate sulla forma, con estremità irregolari come a mano."""
    minx, miny, maxx, maxy = forma.bounds
    diag = math.hypot(maxx - minx, maxy - miny)
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    out = []
    k = -diag
    while k < diag:
        k += passo * rnd.uniform(0.82, 1.18)
        if salto and rnd.random() < salto:
            continue
        riga = LineString([(cx - diag, cy + k), (cx + diag, cy + k)])
        riga = affinity.rotate(riga, angolo, origin=(cx, cy))
        pezzi = riga.intersection(forma)
        geoms = getattr(pezzi, "geoms", [pezzi])
        for g in geoms:
            if g.is_empty or g.geom_type != "LineString" or g.length < 0.8:
                continue
            (ax, ay), (bx, by) = g.coords[0], g.coords[-1]
            a = rnd.uniform(0, accorcia) * g.length
            b = rnd.uniform(0, accorcia) * g.length
            lun = g.length
            ux, uy = (bx - ax) / lun, (by - ay) / lun
            p0 = (ax + ux * a, ay + uy * a)
            p1 = (bx - ux * b, by - uy * b)
            if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) > 0.6:
                out.append(penna(linea_mossa(*p0, *p1, n=6, ondula=.18), larg, .06))
    return "".join(out)


# --- il disegno ----------------------------------------------------------------

def segmenti(linea, larg, punta=.06, ondula=.15):
    """Disegna una LineString (o MultiLineString) come tratti di pennino."""
    out = ""
    for g in getattr(linea, "geoms", [linea]):
        if g.is_empty or g.geom_type != "LineString" or g.length < .8:
            continue
        pts = list(g.coords)
        if len(pts) == 2:
            pts = linea_mossa(*pts[0], *pts[1], n=6, ondula=ondula)
        out += penna(pts, larg, punta)
    return out


def offset_curva(curva, dy, rumore=.6, x_min=None):
    pts = []
    for x, y in curva:
        if x_min is not None and x < x_min:
            continue
        pts.append((x, y + dy + rnd.uniform(-rumore, rumore)))
    return pts


def vignetta(cx=150, cy=84, rx=150, ry=72):
    pts = []
    for i in range(120):
        a = 2 * math.pi * i / 120
        r = 1 + .035 * math.sin(a * 5 + 1) + .02 * math.sin(a * 13)
        # più piatta sopra (cielo aperto), più ampia sotto
        ky = .92 if math.sin(a) > 0 else 1.2
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r * ky))
    return pts


def dentro(px, py, cx=150, cy=84, rx=150, ry=72):
    """0 al centro, 1 sul bordo della vignetta."""
    ky = .92 if py > cy else 1.2
    return math.hypot((px - cx) / rx, (py - cy) / (ry * ky))


def disegna():
    W, H, ORIZ = 300, 150, 92
    tratti, ombre = [], []

    # ---------------- SCOGLIERA ----------------
    # ciglio: pianoro con macchia che sale verso destra
    ciglio = catena(bezier((203, 93), (214, 88), (226, 86), (238, 85)),
                    bezier((238, 85), (252, 84), (262, 80), (274, 78)),
                    bezier((274, 78), (284, 76), (292, 74), (300, 73)))
    # parete a picco con sporgenze, dal ciglio fino al mare
    parete = [(203, 93), (199, 95.5), (196.5, 100), (197.5, 104), (193.5, 108), (192, 114),
              (194, 118), (189.5, 123), (187, 129), (188.5, 133), (183.5, 138), (181, 143),
              (178, 150)]
    roccia = Polygon(parete[::-1] + ciglio + [(300, 150)])
    tratti.append(penna(ciglio, 1.5, .3, .08))
    tratti.append(penna(parete, 1.6, .3, .1))

    # stratificazioni: linee che seguono il ciglio, ognuna con la sua fascia d'ombra sotto
    strati = []
    for dy, amp, per, fase in ((8, 2.2, 23, 0), (19, 3.0, 31, 1.7), (33, 3.6, 27, 3.1), (49, 2.8, 37, 4.4)):
        curva = [(x, y + dy + amp * math.sin(x / per + fase) + rnd.uniform(-.35, .35)) for x, y in ciglio]
        bordo_x = max(px for px, py in parete if py <= 93 + dy + 3) if dy < 55 else 178
        curva = [(bordo_x + 1.5, curva[0][1] + 1)] + [q for q in curva if q[0] > bordo_x + 2]
        strati.append(curva)
        linea = LineString(curva).intersection(roccia)
        # lo strato è tracciato a tratti spezzati, come a mano
        for g in getattr(linea, "geoms", [linea]):
            if g.geom_type != "LineString":
                continue
            lun, pos = g.length, 0
            while pos < lun:
                pezzo = rnd.uniform(6, 16)
                seg = g.interpolate(pos), g.interpolate(min(pos + pezzo, lun))
                tratti.append(segmenti(LineString([(seg[0].x, seg[0].y), (seg[1].x, seg[1].y)]),
                                       .45 + dy / 160, .05))
                pos += pezzo + rnd.uniform(3, 11)
    # ombre: metà inferiore di ogni fascia tratteggiata, più fitta verso il basso e sulla parete
    sopra = ciglio
    for i, sotto in enumerate(strati):
        fascia = Polygon(sopra + sotto[::-1]).buffer(0).intersection(roccia)
        meta = Polygon([(170, sotto[0][1] - (sotto[0][1] - sopra[0][1]) * .55),
                        (300, sotto[-1][1] - (sotto[-1][1] - sopra[-1][1]) * .55),
                        (300, 160), (170, 160)])
        zona = fascia.intersection(meta)
        passo = max(.8, 1.6 - i * .2)
        vicino = zona.intersection(Polygon([(170, 0), (262, 0), (250, 160), (170, 160)]))
        lontano = zona.difference(vicino)
        ang = rnd.uniform(62, 74)
        ombre.append(tratteggio(vicino, ang, passo, .3, .3))
        ombre.append(tratteggio(lontano, ang, passo * 1.9, .26, .45, .25))
        if i >= 2:
            ombre.append(tratteggio(vicino, -18, passo * 1.5, .24, .35))
        sopra = sotto
    # base nell'ombra (sotto l'ultimo strato) e parete esposta al mare
    base = Polygon(sopra + [(300, 150), (178, 150)]).buffer(0).intersection(roccia)
    ombre.append(tratteggio(base, 66, .85, .32, .2))
    ombre.append(tratteggio(base.intersection(Polygon([(170, 0), (255, 0), (240, 160), (170, 160)])), -22, 1.1, .28, .25))
    # crepe verticali nella roccia
    for (x0, y0, h) in ((216, 96, 12), (231, 104, 15), (209, 118, 10), (248, 112, 11), (225, 130, 9)):
        crepa = [(x0 + rnd.uniform(-.6, .6) + k * .25, y0 + k * h / 6) for k in range(7)]
        tratti.append(penna(crepa, .55, .1))
    faccia = Polygon(parete + [(206, 150), (210, 96)]).buffer(0).intersection(roccia)
    ombre.append(tratteggio(faccia, 80, .85, .3, .12))

    # macchia mediterranea sul ciglio: piccoli cespugli a volute
    def cespuglio(x, y, r):
        pts = []
        lobi = rnd.randint(3, 5)
        for i in range(lobi * 8 + 1):
            u = i / (lobi * 8)
            a = math.pi + u * math.pi
            rr = r * (1 + .25 * abs(math.sin(u * lobi * math.pi)))
            pts.append((x + math.cos(a) * rr * 1.6, y + math.sin(a) * rr))
        tratti.append(penna(pts, .65, .1))
        ombre.append(tratteggio(Polygon(pts).buffer(0), 75, .7, .22, .2))

    for x in (207, 214, 221, 229, 247, 258, 266, 280, 287, 295):
        y = min((abs(px - x), py) for px, py in ciglio)[1]
        cespuglio(x, y + .3, rnd.uniform(1.4, 2.4))

    # scogli in acqua e schiuma
    for (x, y, l, h) in ((168, 142, 9, 4.5), (160, 146.5, 5, 2.6), (174, 135.5, 4, 2.2)):
        sc = [(x - l / 2, y), (x - l / 3, y - h * .8), (x, y - h), (x + l / 3, y - h * .7), (x + l / 2, y)]
        tratti.append(penna(sc, .9, .2))
        ombre.append(tratteggio(Polygon(sc + [(x - l / 2, y)]), 60, .7, .25, .1))
        for k in range(3):
            xs = x - l / 2 - 2 + k * (l / 2 + 1.5)
            tratti.append(penna(bezier((xs, y + .8), (xs + 1, y - .2), (xs + 2.2, y - .2), (xs + 3.2, y + .8), 8), .35, .05))

    # ---------------- PINI MARITTIMI ----------------
    def pino(xb, yb, xc, yc, larghezza, altezza):
        tronco = bezier((xb, yb), (xb - 1.5, yb - 10), (xc + 5, yc + 12), (xc + .5, yc + 3), 30)
        tratti.append(penna(tronco, 2.1, 1.0))
        ombre.append(segmenti(LineString(offset_curva(tronco, 0, 0)).parallel_offset(.6, "right"), .3))
        for (dx1, dy1, dx2, dy2) in ((1.5, 7, 13, 2), (1, 5.5, -12, 1.5), (2, 9.5, 8, 4)):
            ramo = bezier((xc + dx1, yc + dy1), (xc + dx1 + dx2 * .3, yc + dy1 - 2),
                          (xc + dx2 * .7, yc + dy2 + 1), (xc + dx2, yc + dy2), 12)
            tratti.append(penna(ramo, .85, .15))
        # chioma a ciuffi: unione di nuvole appiattite
        ciuffi = []
        for (fx, fy, fl, fh) in ((-.32, .15, .42, .55), (-.05, -.05, .5, .75), (.27, .1, .44, .6),
                                 (.08, .25, .55, .45)):
            cx, cy = xc + fx * larghezza, yc + fy * altezza
            pts = []
            n = 40
            for i in range(n):
                a = 2 * math.pi * i / n
                rr = 1 + .12 * math.sin(a * 7 + rnd.uniform(0, 3)) * (1 if math.sin(a) < 0 else .3)
                pts.append((cx + math.cos(a) * fl * larghezza / 2 * rr,
                            cy + math.sin(a) * fh * altezza / 2 * rr * (1 if math.sin(a) < 0 else .6)))
            ciuffi.append(Polygon(pts).buffer(0))
        chioma = ciuffi[0]
        for c in ciuffi[1:]:
            chioma = chioma.union(c)
        bordo = list(chioma.exterior.coords)
        # contorno a volute: tratto spezzato in archi, più marcato in basso
        for i in range(0, len(bordo) - 6, 6):
            arco = bordo[i:i + 8]
            y_medio = sum(q[1] for q in arco) / len(arco)
            tratti.append(penna(arco, .95 if y_medio > yc else .7, .15))
        # ombra sotto la chioma (fitta) e piccoli segni di fogliame sopra
        sotto = chioma.intersection(Polygon([(xc - larghezza, yc + altezza * .05), (xc + larghezza, yc + altezza * .05),
                                             (xc + larghezza, yc + altezza), (xc - larghezza, yc + altezza)]))
        ombre.append(tratteggio(sotto, 82, .7, .3, .1))
        ombre.append(tratteggio(sotto, 20, 1.0, .25, .15))
        for c in ciuffi:
            mx, my = c.centroid.x, c.centroid.y
            for k in range(7):
                x = mx + rnd.uniform(-.35, .35) * larghezza * .4
                y = my + rnd.uniform(-.4, .1) * altezza * .4
                tratti.append(penna(bezier((x - 1.6, y + .6), (x - .6, y - .7), (x + .6, y - .7), (x + 1.6, y + .6), 6), .35, .05))

    pino(244, 84.6, 232, 46, 52, 17)
    pino(272, 78.2, 278, 55, 36, 12.5)

    # ---------------- ORIZZONTE, ISOLA, VELA ----------------
    isola = catena(bezier((16, ORIZ), (26, ORIZ - 7), (38, ORIZ - 11), (50, ORIZ - 10)),
                   bezier((50, ORIZ - 10), (60, ORIZ - 9), (68, ORIZ - 6), (76, ORIZ - 6.5)),
                   bezier((76, ORIZ - 6.5), (84, ORIZ - 7), (92, ORIZ - 3), (102, ORIZ)))
    tratti.append(penna(isola, .75, .1))
    ombre.append(tratteggio(Polygon(isola), 0, 1.3, .2, .35))
    for x0, x1 in ((3, 15), (104, 119), (131, 160), (166, 192)):
        tratti.append(penna(linea_mossa(x0, ORIZ, x1, ORIZ, 10, .08), .45, .06))
    vela = Polygon([(121.5, ORIZ - 1.4), (127, ORIZ - 14), (128, ORIZ - 1.4)])
    tratti.append(penna([(127, ORIZ - 14.6), (127.1, ORIZ + .2)], .55, .2))
    tratti.append(penna([(121.5, ORIZ - 1.4), (126.9, ORIZ - 13.8)], .5, .1))
    ombre.append(tratteggio(vela, 90, .75, .2, .1))
    tratti.append(penna([(120, ORIZ + .4), (129.6, ORIZ + .4)], .65, .2))

    # ---------------- MARE ----------------
    mare = Polygon([(0, ORIZ + 1.5), (300, ORIZ + 1.5), (300, 150), (0, 150)]).difference(roccia.buffer(1.2))
    y = ORIZ + 2.6
    while y < 149.5:
        prof = (y - ORIZ) / (150 - ORIZ)
        x = rnd.uniform(-4, 10)
        while x < 300:
            vicino = max(0, 1 - abs(x - 185) / 60)      # vicino alla scogliera: acqua più scura
            lun = rnd.uniform(2.5, 8) * (0.55 + prof * 1.5) * (1 + vicino * .8)
            vuoto = rnd.uniform(7, 22) * (1.3 - prof * .45) * (1 - vicino * .55)
            d = dentro(x + lun / 2, y)
            if d < .8 or rnd.random() > (d - .8) * 5:
                seg = LineString(linea_mossa(x, y, x + lun, y + rnd.uniform(-.12, .12), 5, .2)).intersection(mare)
                tratti.append(segmenti(seg, (.22 + prof * .34 + vicino * .14) * (1 - max(0, d - .75) * 1.6), .04))
            x += lun + vuoto
        y += (1.5 + prof * 2.9) * rnd.uniform(.85, 1.15)
    # riflesso scuro della scogliera sull'acqua
    riflesso = Polygon([(150, 141), (178, 128), (184, 150), (140, 150)]).intersection(mare)
    ombre.append(tratteggio(riflesso, 0, 1.1, .3, .45, .2))

    # ---------------- CIELO ----------------
    for (x, y, s) in ((92, 50, 1.0), (104, 57, .75), (148, 40, .6)):
        for verso in (-1, 1):
            ala = bezier((x, y + .6 * s), (x + verso * 1.5 * s, y - 2 * s), (x + verso * 4 * s, y - 2.6 * s),
                         (x + verso * 6.2 * s, y + 1 * s), 10)
            tratti.append(penna(ala, .75 * s + .2, .08))
    for (x0, y0, l) in ((26, 44, 42), (40, 48.5, 24), (146, 60, 30), (160, 64, 16)):
        tratti.append(penna(linea_mossa(x0, y0, x0 + l, y0, 10, .3), .32, .05))

    corpo_svg = f'<path d="{"".join(ombre)}"/><path d="{"".join(tratti)}"/>'
    ovale = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in vignetta()) + "Z"
    # bordo ovale irregolare, come in un'incisione: l'inchiostro resta sempre pieno
    return (f'<svg viewBox="0 0 {W} {H}" class="ill" aria-hidden="true">'
            f'<defs><clipPath id="vignetta"><path d="{ovale}"/></clipPath></defs>'
            f'<g fill="{INCHIOSTRO}" stroke="none" clip-path="url(#vignetta)">{corpo_svg}</g></svg>')


COSTA_INCHIOSTRO = disegna()

if __name__ == "__main__":
    import sys
    from pathlib import Path
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("costa.html")
    svg = COSTA_INCHIOSTRO.replace('class="ill"', 'width="1500"')
    out.write_text('<html><body style="margin:0;background:#fff">' + svg + '</body></html>')
