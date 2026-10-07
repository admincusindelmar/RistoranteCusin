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


def vignetta(cx=150, cy=82, rx=158, ry=80):
    pts = []
    for i in range(120):
        a = 2 * math.pi * i / 120
        r = 1 + .035 * math.sin(a * 5 + 1) + .02 * math.sin(a * 13)
        # più piatta sopra (cielo aperto), più ampia sotto
        ky = .8 if math.sin(a) > 0 else 1.0
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r * ky))
    return pts


def dentro(px, py, cx=150, cy=82, rx=158, ry=80):
    """0 al centro, 1 sul bordo della vignetta."""
    ky = .8 if py > cy else 1.0
    return math.hypot((px - cx) / rx, (py - cy) / (ry * ky))


def quota(x):
    """Altezza del terreno in cima alla scogliera."""
    return 93 - (x - 203) * .041


def rett(x0, y0, x1, y1):
    return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def ristorante(tratti, ombre):
    L = lambda pts, w=.7, p=.15: tratti.append(penna(pts, w, p))
    dritta = lambda x0, y0, x1, y1, w=.6: L(linea_mossa(x0, y0, x1, y1, 6, .06), w, .2)

    # --- casa dietro: due piani, tetto a coppi, persiane
    cx0, cx1, gronda, colmo = 236, 276, 63.5, 55.5
    base_casa = quota(cx1)
    for x in (cx0, cx1):
        dritta(x, gronda, x, quota(x), .85)
    dritta(cx0 - 2.2, gronda, cx1 + 2.2, gronda, .9)
    tetto = [(cx0 - 2.2, gronda), ((cx0 + cx1) / 2, colmo), (cx1 + 2.2, gronda)]
    L(tetto, 1.0, .3)
    ombre.append(tratteggio(Polygon(tetto), 102, .75, .28, .05))          # coppi
    for k in range(4):                                                     # file di coppi
        y = gronda - 1.6 - k * 1.8
        dx = (y - colmo) / (gronda - colmo) * ((cx1 - cx0) / 2 + 2.2)
        dritta((cx0 + cx1) / 2 - dx + .6, y, (cx0 + cx1) / 2 + dx - .6, y, .3)
    ombre.append(tratteggio(rett(cx0, gronda, cx1, gronda + 2.2), 0, .55, .26, .05))  # ombra di gronda
    # comignolo
    L([(266, 59.6), (266, 54.5), (269.5, 54.5), (269.5, 61.2)], .7)
    dritta(265.3, 54.5, 270.2, 54.5, .8)
    ombre.append(tratteggio(rett(267.8, 54.8, 269.4, 60.5), 90, .5, .22, .05))
    # parete in ombra sul lato destro
    ombre.append(tratteggio(rett(268, gronda + 2.2, cx1, base_casa), 75, 1.1, .24, .25))
    # finestre con persiane (piano alto e piano terra) e porta
    def finestra(x, y, w=4.2, h=6.2):
        L([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], .55, .2)
        for k in range(1, 7):
            dritta(x + .3, y + k * h / 7, x + w - .3, y + k * h / 7, .22)
        dritta(x - .6, y + h + .3, x + w + .6, y + h + .3, .5)                 # davanzale
    for x in (240.5, 251.5, 262.5):
        finestra(x, 67.5)
    for x in (240.5, 262.5):
        finestra(x, 78.5)
    L([(251.6, quota(251.6)), (251.6, 79), (256.6, 79), (256.6, quota(256.6))], .6, .2)  # porta
    ombre.append(tratteggio(rett(251.8, 79.3, 256.4, quota(256)), 90, .55, .25, .05))
    L(bezier((250.8, 79), (252, 76.6), (256.2, 76.6), (257.4, 79), 10), .5)   # arco sopra la porta

    # --- verandata vetrata sul mare
    vx0, vx1, vtop, vbase = 207, 236, 74.5, 89.6
    dritta(vx0 - 2, vtop - 2.2, vx1 + 1.2, vtop - 2.2, .9)                  # tetto della veranda
    dritta(vx0 - 2, vtop, vx1 + 1.2, vtop, .7)
    dritta(vx0 - 2, vtop - 2.2, vx0 - 2, vtop, .6)
    ombre.append(tratteggio(rett(vx0 - 2, vtop - 2.2, vx1 + 1.2, vtop), 0, .5, .24, .05))
    for i in range(14):                                                   # mantovana smerlata
        x = vx0 - 2 + i * 2.4
        L(bezier((x, vtop), (x + .4, vtop + 1.3), (x + 2, vtop + 1.3), (x + 2.4, vtop), 6), .4, .1)
    montanti = [vx0 + i * (vx1 - vx0) / 5 for i in range(6)]
    for x in montanti:
        dritta(x, vtop + .2, x, vbase, .55 if x in (vx0, vx1) else .42)
    dritta(vx0, 79.5, vx1, 79.5, .35)                                       # traverso
    dritta(vx0, 86.3, vx1, 86.3, .45)                                       # zoccolo
    ombre.append(tratteggio(rett(vx0, 86.4, vx1, vbase), 90, .9, .24, .05))
    for i, x in enumerate(montanti[:-1]):                                    # riflessi sui vetri
        if i % 2 == 0:
            L([(x + 1.2, 85.5), (x + 3.4, 81)], .22, .05)
            L([(x + 2.2, 85.5), (x + 4.4, 81)], .22, .05)
    for x in (211, 222.5):                                                  # tavoli e sedie dentro
        dritta(x, 83.6, x + 4, 83.6, .45)
        dritta(x + 2, 83.6, x + 2, 86.2, .35)
        L([(x - 1.2, 86.2), (x - 1.2, 82.6), (x - .4, 84.4), (x - .4, 86.2)], .3, .1)
        L([(x + 5.2, 86.2), (x + 5.2, 82.6), (x + 4.4, 84.4), (x + 4.4, 86.2)], .3, .1)
    # ombra della veranda sul terreno
    ombre.append(tratteggio(rett(vx0, vbase + .6, vx1 + 3, vbase + 2.4), 0, .6, .24, .1))

    # --- terrazza a sbalzo con ringhiera, tavolino e ombrellone
    tx0 = 192.5
    dritta(tx0, vbase, vx0, vbase, .9)
    dritta(tx0, vbase + 1.5, vx0, vbase + 1.5, .6)
    ombre.append(tratteggio(rett(tx0, vbase, vx0, vbase + 1.5), 0, .45, .24, .05))
    for (x0, x1, y1) in ((195, 197.2, 99.5), (201, 201.6, quota(201.6) + .4)):
        dritta(x0, vbase + 1.5, x1, y1, .7)                                  # sostegni
    dritta(tx0, 85.6, vx0, 85.6, .55)                                       # corrimano
    x = tx0
    while x <= vx0:
        dritta(x, 85.6, x, vbase, .3)
        x += 1.5
    dritta(197.3, 86.2, 202.3, 86.2, .55)                                   # tavolino
    dritta(199.8, 86.2, 199.8, vbase, .4)
    dritta(199.8, 86.2, 199.8, 77, .45)                                      # palo dell'ombrellone
    tenda = catena(bezier((191.5, 79), (194, 76.2), (197, 74.6), (199.8, 74.2)),
                   bezier((199.8, 74.2), (202.6, 74.6), (205.6, 76.2), (208.1, 79)))
    L(tenda, .8, .2)
    for i in range(7):
        x = 191.5 + i * 2.37
        L(bezier((x, 79), (x + .4, 80.1), (x + 2, 80.1), (x + 2.37, 79), 6), .35, .1)
    lato = Polygon(tenda[len(tenda) // 2:] + [(199.8, 79)])
    ombre.append(tratteggio(lato, 70, .65, .24, .1))
    for x in (195.7, 203.9):
        L(bezier((199.8, 74.4), (x - (x - 199.8) * .4, 75.4), (x, 77), (x, 79), 8), .3, .05)


def disegna():
    W, H, ORIZ = 300, 150, 92
    tratti, ombre = [], []

    # ---------------- SCOGLIERA ----------------
    # ciglio: pianoro con macchia che sale verso destra
    ciglio = catena(bezier((203, 93), (222, 91.6), (250, 91.2), (272, 90.6)),
                    bezier((272, 90.6), (284, 90.2), (292, 89.6), (300, 89)))
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

    for x in (281, 292, 298):
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

    pino(284, 90.4, 279, 51, 38, 12.5)
    ristorante(tratti, ombre)

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



# =============================================================================
# ANTIGNANO: la baia del Cusin del Mar, dalle foto del locale
# =============================================================================

def _d(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


class Strato:
    """Un livello del disegno: sagoma bianca (copre ciò che sta dietro) + inchiostro."""
    def __init__(self):
        self.bianco, self.inchiostro = [], []

    def copri(self, pts):
        self.bianco.append(_d(pts))

    def tratto(self, pts, larg=.7, punta=.12):
        self.inchiostro.append(penna(pts, larg, punta))

    def retta(self, x0, y0, x1, y1, larg=.5):
        self.inchiostro.append(penna(linea_mossa(x0, y0, x1, y1, 6, .05), larg, .18))

    def ombra(self, forma, angolo, passo, larg=.26, accorcia=.2, salto=0.0):
        if not forma.is_empty:
            self.inchiostro.append(tratteggio(forma, angolo, passo, larg, accorcia, salto))

    def svg(self):
        b = "".join(self.bianco)
        return ((f'<path d="{b}" fill="#fff"/>' if b else "") +
                f'<path d="{"".join(self.inchiostro)}" fill="{INCHIOSTRO}"/>')


def ciuffo(cx, cy, r, lobi=None, schiaccia=.75):
    """Sagoma di un cespuglio di macchia: contorno a lobi."""
    lobi = lobi or rnd.randint(5, 8)
    pts = []
    for i in range(lobi * 10):
        a = 2 * math.pi * i / (lobi * 10)
        rr = r * (1 + .16 * abs(math.sin(a * lobi / 2 + rnd.uniform(0, .3))))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * schiaccia))
    return pts


def macchia(st, cx, cy, r):
    pts = ciuffo(cx, cy, r)
    st.copri(pts)
    poly = Polygon(pts).buffer(0)
    # contorno a volute solo nella metà alta, ombra fitta in basso
    for i in range(0, len(pts) - 4, 5):
        arco = pts[i:i + 7]
        if sum(q[1] for q in arco) / len(arco) < cy + r * .2:
            st.tratto(arco, .55, .1)
    basso = poly.intersection(rett(cx - 2 * r, cy - r * .1, cx + 2 * r, cy + 2 * r))
    st.ombra(basso, 75, .7, .26, .15)
    st.ombra(basso, 20, 1.1, .22, .25)
    for k in range(int(r * 1.5)):
        x = cx + rnd.uniform(-.6, .6) * r
        y = cy + rnd.uniform(-.6, .1) * r * .75
        if poly.contains(Polygon([(x - 1, y), (x + 1, y), (x, y - .8)])):
            st.tratto(bezier((x - 1.1, y + .4), (x - .4, y - .6), (x + .4, y - .6), (x + 1.1, y + .4), 5), .3, .05)


def ombrellone(st, x, y, w=3.2):
    """Piccolo ombrellone da spiaggia a spicchi (come quelli del pontile)."""
    cupola = bezier((x - w / 2, y), (x - w / 2.4, y - w * .42), (x + w / 2.4, y - w * .42), (x + w / 2, y), 8)
    st.copri(cupola + [(x + w / 2, y + .2), (x - w / 2, y + .2)])
    st.tratto(cupola, .4, .1)
    st.retta(x - w / 2, y, x + w / 2, y, .3)
    st.ombra(Polygon(cupola[:5] + [(x, y)]), 90, .45, .2, .05)       # spicchio in ombra
    st.retta(x, y, x, y + w * .45, .3)


def barca(st, x, y, l=7):
    scafo = [(x - l / 2, y), (x + l / 2, y), (x + l * .38, y + l * .16), (x - l * .42, y + l * .16)]
    st.copri(scafo)
    st.tratto(scafo + [scafo[0]], .5, .15)
    st.retta(x - l * .15, y, x - l * .15, y - l * .14, .35)
    st.retta(x - l * .15, y - l * .14, x + l * .12, y - l * .14, .35)
    st.retta(x + l * .12, y - l * .14, x + l * .12, y, .35)
    for k in range(3):
        st.retta(x - l * .45 + k * 1.2, y + l * .24 + k * .9, x + l * .25 - k * 1.1, y + l * .24 + k * .9, .22)


def disegna_antignano():
    W, H, ORIZ = 300, 150, 66
    cielo, mare, sfondo, collina, cotto, bianco, pergola, riva, primo = (Strato() for _ in range(9))

    # ---------- CIELO
    for (x, y, s) in ((60, 30, 1.0), (72, 36, .75), (118, 22, .6)):
        for verso in (-1, 1):
            ala = bezier((x, y + .6 * s), (x + verso * 1.5 * s, y - 2 * s), (x + verso * 4 * s, y - 2.6 * s),
                         (x + verso * 6.2 * s, y + 1 * s), 10)
            cielo.tratto(ala, .7 * s + .2, .08)
    for (x0, y0, l) in ((14, 40, 40), (28, 44, 22), (150, 30, 34), (166, 34, 18)):
        cielo.tratto(linea_mossa(x0, y0, x0 + l, y0, 10, .3), .3, .05)

    # ---------- MARE (fa da fondo a tutto ciò che sta sotto l'orizzonte)
    for x0, x1 in ((2, 40), (46, 112)):
        mare.tratto(linea_mossa(x0, ORIZ, x1, ORIZ, 10, .05), .45, .06)
    y = ORIZ + 2
    while y < 149.5:
        prof = (y - ORIZ) / (150 - ORIZ)
        x = rnd.uniform(-4, 10)
        while x < 300:
            lun = rnd.uniform(2.5, 8) * (0.5 + prof * 1.4)
            vuoto = rnd.uniform(7, 20) * (1.3 - prof * .5)
            d = dentro(x + lun / 2, y)
            if d < .8 or rnd.random() > (d - .8) * 5:
                mare.tratto(linea_mossa(x, y, x + lun, y + rnd.uniform(-.12, .12), 5, .2),
                            (.2 + prof * .36) * (1 - max(0, d - .75) * 1.6), .04)
            x += lun + vuoto
        y += (1.5 + prof * 3.0) * rnd.uniform(.85, 1.15)

    # diga di scogli a sinistra (in diagonale verso il largo)
    for i in range(15):
        u = i / 14
        cx, cy = 6 + u * 62, 104 - u * 18 + rnd.uniform(-.6, .6)
        r = 3.4 - u * 1.3 + rnd.uniform(-.4, .4)
        sasso = [(cx + math.cos(a) * r * rnd.uniform(.85, 1.1), cy + math.sin(a) * r * .62 * rnd.uniform(.85, 1.1))
                 for a in [2 * math.pi * k / 9 for k in range(9)]]
        mare.copri(sasso)
        mare.tratto(sasso[5:] + sasso[:2], .55, .12)
        mare.ombra(Polygon(sasso).buffer(0).intersection(rett(cx - r, cy, cx + r, cy + r)), 60, .55, .22, .1)
    for (x, y, l) in ((88, 104, 7.5), (104, 112, 6.5), (120, 96, 6), (76, 94, 5.5)):
        barca(mare, x, y, l)

    # ---------- PROMONTORIO CON LE CASE sullo sfondo
    prom = catena(bezier((108, ORIZ), (120, 62.5), (136, 60), (150, 58.8)),
                  bezier((150, 58.8), (164, 57.6), (180, 58.6), (196, 63)))
    sfondo.copri(prom + [(196, ORIZ + .5), (108, ORIZ + .5)])
    sfondo.tratto(prom, .6, .1)
    sfondo.ombra(Polygon(prom + [(196, ORIZ)]), 0, 1.0, .2, .35)
    for (x, w, h) in ((140, 4, 2.6), (146, 3, 2), (157, 5, 3), (164, 3.5, 2.4), (171, 4.5, 2.8)):
        yb = 59.6 - (x - 140) * .02
        casa = [(x, yb), (x, yb - h), (x + w, yb - h), (x + w, yb)]
        sfondo.copri(casa)
        sfondo.tratto(casa, .35, .1)
        sfondo.retta(x + w * .3, yb - h * .55, x + w * .5, yb - h * .55, .25)

    # ---------- COLLINA DI MACCHIA a destra: il pendio verde che scende alla spiaggia
    profilo = catena(bezier((214, 70), (234, 62), (254, 55), (270, 51)),
                     bezier((270, 51), (282, 48.5), (292, 47), (300, 46.5)))
    pendio = profilo + [(300, 128), (236, 131), (224, 112), (214, 72)]
    collina.copri(pendio)
    collina.tratto(profilo, .7, .15)
    punti = []
    for gy in range(50, 126, 7):
        for gx in range(242, 306, 8):
            x, y = gx + rnd.uniform(-2.5, 2.5) + (gy % 12) * .3, gy + rnd.uniform(-2, 2)
            if Polygon(pendio).contains(Polygon([(x - 1, y), (x + 1, y), (x, y - 1)])):
                punti.append((x, y))
    for (x, y) in sorted(punti, key=lambda q: q[1]):
        macchia(collina, x, y, rnd.uniform(3, 4.6))
    # ---------- EDIFICIO COLOR TERRACOTTA a gradoni (dietro)
    gradoni = [(232, 72), (232, 64), (238, 64), (238, 57), (246, 57), (246, 50), (290, 50), (290, 72)]
    cotto.copri(gradoni)
    cotto.tratto(gradoni + [gradoni[0]], .65, .2)
    forma = Polygon(gradoni)
    finestre = []
    for (y0, xs) in ((52, range(252, 288, 7)), (59, range(242, 288, 8)), (66, range(236, 288, 8))):
        for x in xs:
            finestre.append(rett(x, y0, x + 3.4, y0 + 2.6))
    tono = forma
    for f in finestre:
        tono = tono.difference(f)
    cotto.ombra(tono, 58, .7, .24, .08)                                  # tono scuro del cotto
    for f in finestre:
        cotto.tratto(list(f.exterior.coords), .3, .1)
    for (x0, y0, x1) in ((230.5, 64, 291), (236.5, 57, 291), (244.5, 50, 291.5)):  # solette sporgenti
        cotto.copri([(x0, y0 - .9), (x1, y0 - .9), (x1, y0 + .4), (x0, y0 + .4)])
        cotto.retta(x0, y0 - .9, x1, y0 - .9, .5)
        cotto.retta(x0, y0 + .4, x1, y0 + .4, .5)
    cotto.retta(278, 50, 278, 46.5, .3)                                   # antenna

    # ---------- EDIFICIO BIANCO con balconi e VERANDATA VETRATA in cima
    gx0, gx1, terra, cima = 194, 258, 102, 73
    piani = [cima + i * (terra - cima) / 4 for i in range(5)]
    sagoma = [(180, terra), (180, 80), (gx0, 80), (gx0, cima), (gx1, cima), (gx1, terra)]
    bianco.copri(sagoma)
    bianco.tratto(sagoma + [sagoma[0]], .7, .2)
    for i, y in enumerate(piani[1:-1] + [terra]):
        x0 = 180 if y > 80 else gx0
        bianco.copri([(x0 - .8, y - 1.1), (gx1 + .8, y - 1.1), (gx1 + .8, y + .2), (x0 - .8, y + .2)])
        bianco.retta(x0 - .8, y - 1.1, gx1 + .8, y - 1.1, .5)              # soletta del balcone
        bianco.retta(x0 - .8, y + .2, gx1 + .8, y + .2, .35)
        bianco.ombra(rett(x0, y + .3, gx1, y + 1.5), 0, .4, .2, .05)        # ombra sotto la soletta
        x = x0 + .6
        while x < gx1:                                                       # parapetti in vetro
            bianco.retta(x, y - 3.6, x, y - 1.2, .18)
            x += 1.7
        bianco.retta(x0, y - 3.6, gx1, y - 3.6, .3)
    for y0, y1 in zip(piani[:-1], piani[1:]):                               # finestre tra i piani
        x0 = 182 if y0 >= 80 else gx0 + 2
        for x in [v for v in range(int(x0), gx1 - 4, 7)]:
            bianco.tratto([(x, y0 + 1.6), (x + 3.4, y0 + 1.6), (x + 3.4, y1 - 4.2), (x, y1 - 4.2), (x, y0 + 1.6)], .25, .08)
    bianco.ombra(rett(180, 80, gx0, terra), 90, 1.4, .2, .3)               # corpo arretrato più in ombra
    # verandata vetrata sul tetto (la terrazza del ristorante)
    vx0, vx1, vtop = 224, 258, 65
    bianco.copri([(vx0, cima), (vx0, vtop), (vx1, vtop), (vx1, cima)])
    bianco.retta(vx0 - .8, vtop, vx1 + .8, vtop, .7)
    bianco.retta(vx0 - .8, vtop + 1, vx1 + .8, vtop + 1, .4)
    x = vx0
    while x <= vx1 + .1:
        bianco.retta(x, vtop + 1, x, cima, .3 if vx0 < x < vx1 else .5)
        x += (vx1 - vx0) / 8
    bianco.retta(vx0, cima - 3, vx1, cima - 3, .25)
    for i in range(0, 8, 2):                                                # riflessi sui vetri
        xr = vx0 + i * (vx1 - vx0) / 8
        bianco.tratto([(xr + .8, cima - .6), (xr + 2.6, vtop + 2.2)], .2, .05)
        bianco.tratto([(xr + 1.8, cima - .6), (xr + 3.6, vtop + 2.2)], .2, .05)
    x = gx0 + .5                                                            # parapetto della terrazza
    while x < vx0:
        bianco.retta(x, cima - 2.6, x, cima, .18)
        x += 1.7
    bianco.retta(gx0, cima - 2.6, vx0, cima - 2.6, .35)
    for xo in (204, 211):                                                   # ombrelloni chiusi in terrazza
        bianco.tratto([(xo, cima), (xo, cima - 6.5)], .3, .1)
        bianco.tratto([(xo - .9, cima - 2.2), (xo, cima - 6.2), (xo + .9, cima - 2.2)], .45, .1)

    # ---------- PERGOLA con tende bianche alla base dell'edificio
    px0, px1, ptop = 190, 252, 98
    pergola.copri([(px0, ptop - 1.6), (px1, ptop - 1.6), (px1, terra + 1.5), (px0, terra + 1.5)])
    for i in range(10):
        x = px0 + i * (px1 - px0) / 10
        pergola.tratto([(x, ptop), (x + (px1 - px0) / 20, ptop - 1.5), (x + (px1 - px0) / 10, ptop)], .45, .15)
    pergola.retta(px0, ptop, px1, ptop, .4)
    x = px0
    while x <= px1 + .1:
        pergola.retta(x, ptop, x, terra + 1.5, .35)
        x += (px1 - px0) / 5
    for x in range(px0 + 3, px1 - 3, 6):                                    # tavolini sotto la pergola
        pergola.retta(x, terra - 1, x + 2.6, terra - 1, .3)
    pergola.ombra(rett(px0, ptop + .3, px1, ptop + 2.2), 0, .5, .2, .1)

    # ---------- SPIAGGIA di ciottoli e PONTILE con gli ombrelloni
    sp = [(146, 106), (176, 103.5), (194, 103.5), (240, 104.5), (252, 108), (251, 124), (214, 128),
          (182, 125), (158, 117)]
    riva.copri(sp)
    riva.tratto(sp[4:] + sp[:1], .55, .1)                                    # bordo dell'acqua
    spiaggia = Polygon(sp)
    for k in range(260):                                                    # ciottoli
        x, y = rnd.uniform(146, 252), rnd.uniform(103.5, 128)
        if spiaggia.contains(Polygon([(x - .4, y), (x + .4, y), (x, y + .3)])):
            r = rnd.uniform(.25, .55)
            riva.tratto([(x + math.cos(a) * r, y + math.sin(a) * r * .7) for a in
                         [2 * math.pi * j / 6 for j in range(7)]], .18, .1)
    for (x, y) in ((150, 112), (160, 120), (176, 126.5), (198, 129.5), (226, 128)):  # schiuma
        riva.tratto(bezier((x - 3, y + 1), (x - 1, y - .2), (x + 1, y - .2), (x + 3, y + 1), 8), .3, .05)
    pontile = [(96, 96.5), (150, 99), (154, 104.5), (100, 101.6)]
    riva.copri(pontile)
    riva.tratto(pontile + [pontile[0]], .6, .15)
    riva.ombra(Polygon([(100, 101.6), (154, 104.5), (154, 105.8), (100, 102.9)]), 0, .45, .22, .05)
    riva.retta(100, 101.6, 100, 103, .4)
    riva.retta(154, 104.5, 154, 105.9, .4)
    for fila, (dy, passo) in enumerate(((0, 5.2), (2.4, 5.2))):            # due file di ombrelloni
        x = 101 + fila * 2.6
        while x < 150:
            yb = 97.8 + (x - 96) * .046 + dy
            ombrellone(riva, x, yb, 3.4)
            x += passo
    molo = [(62, 92.5), (96, 96.5), (96, 97.6), (62, 93.6)]                 # passerella per le barche
    riva.copri(molo)
    riva.tratto(molo + [molo[0]], .45, .1)
    for x in range(64, 96, 4):
        riva.retta(x, 93 + (x - 62) * .118, x, 95 + (x - 62) * .118, .25)

    # ---------- PRIMO PIANO: macchia che incornicia la vista (come nelle foto)
    for (cx, cy, r) in ((236, 130, 6.5), (250, 125, 7.5), (264, 120, 8), (279, 114, 8), (293, 107, 7.5),
                        (272, 128, 6), (26, 124, 6.5), (14, 118, 6), (40, 128, 5.5)):
        macchia(primo, cx, cy, r)
    for (x, y) in ((226, 126), (246, 116), (32, 116), (6, 110)):           # fili d'erba
        for k in range(4):
            primo.tratto(bezier((x + k * 1.4, y + 6), (x + k * 1.4 + .3, y + 3), (x + k * 1.6 - .4, y + 1),
                                (x + k * 1.8 - 1.2, y - 1 - k * .6), 8), .35, .05)

    sposta = lambda st: f'<g transform="translate(-18 0)">{st.svg()}</g>'
    corpo = (cielo.svg() + mare.svg() + sfondo.svg() + collina.svg() +
             "".join(sposta(st) for st in (cotto, bianco, pergola, riva)) + primo.svg())
    ovale = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in vignetta()) + "Z"
    return (f'<svg viewBox="0 0 {W} {H}" class="ill" aria-hidden="true">'
            f'<defs><clipPath id="vignetta"><path d="{ovale}"/></clipPath></defs>'
            f'<g stroke="none" clip-path="url(#vignetta)">{corpo}</g></svg>')


COSTA_INCHIOSTRO = disegna_antignano()

if __name__ == "__main__":
    import sys
    from pathlib import Path
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("costa.html")
    svg = COSTA_INCHIOSTRO.replace('class="ill"', 'width="1500"')
    out.write_text('<html><body style="margin:0;background:#fff">' + svg + '</body></html>')
