#!/usr/bin/env python3
"""
Mockup realistici dei supporti proposti per la carta dei dolci e dei distillati.

Il legno, l'ottone e le strisce vengono dalle foto vere delle cartelle (riferimenti/cartelle/),
raddrizzate in prospettiva; il cuoio è generato. I fogli sono le pagine vere di
pdf/Dolci-Distillati_Stampa.pdf, su carta avorio martellata simulata.

    mockup/A_cartella-cuoio-chiusa.jpg, A_cartella-cuoio-aperta.jpg
    mockup/B_trittico-cartelle.jpg
    mockup/C_leggio.jpg
    mockup/D_tavoletta-due-facce.jpg, D_tavoletta-fronte-dolci.jpg, D_tavoletta-retro-distillati.jpg   (versione scelta)
    pdf/Mockup-supporti-dolci-distillati.pdf   tutte le immagini, una per pagina

Uso: python3 genera_mockup.py
"""
import cv2
import numpy as np
import pymupdf
from playwright.sync_api import sync_playwright

from genera_cloud import CHROME, QUI, scarica

RNG = np.random.default_rng(7)
OUT = QUI / "mockup"
FOTO = QUI / "riferimenti" / "cartelle"
AVORIO = np.array([226, 237, 244], np.float32)        # BGR di #f4ede2
PX_MM = 4.0                                            # risoluzione delle texture: 4 px per mm


# ---------- utilità ----------
def rumore(h, w, sigma, seme=None):
    g = (np.random.default_rng(seme) if seme is not None else RNG).standard_normal((h, w)).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), sigma) if sigma > 0 else g
    return g / (g.std() + 1e-6)


def rilievo(altezza, forza, luce=(-1, -1.3)):
    """Ombreggiatura da una mappa di altezze: luce da in alto a sinistra."""
    gx = cv2.Sobel(altezza, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(altezza, cv2.CV_32F, 0, 1, ksize=3)
    lx, ly = luce
    n = np.hypot(lx, ly)
    return 1 + forza * (gx * lx + gy * ly) / n


def rgba(bgr, alpha=None):
    a = np.full(bgr.shape[:2], 255, np.uint8) if alpha is None else alpha
    return np.dstack([np.clip(bgr, 0, 255).astype(np.uint8), a])


def raddrizza(foto, quad, w, h):
    im = cv2.imread(str(FOTO / foto))
    M = cv2.getPerspectiveTransform(np.float32(quad), np.float32([[0, 0], [w, 0], [w, h], [0, h]]))
    return cv2.warpPerspective(im, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def angoli_arrotondati(a, r):
    m = np.zeros_like(a)
    h, w = a.shape
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1)
    cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r - 1, r), (r, h - r - 1), (w - r - 1, h - r - 1)):
        cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return np.minimum(a, m)


def posa(scena, obj, quad, ombra=(14, 22, 26, .45)):
    """Mette un oggetto RGBA nella scena dentro il quadrilatero quad (TL, TR, BR, BL), con l'ombra portata."""
    h, w = obj.shape[:2]
    H, W = scena.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(quad))
    o = cv2.warpPerspective(obj, M, (W, H), flags=cv2.INTER_AREA if w > 1500 else cv2.INTER_LINEAR)
    a = o[:, :, 3:4].astype(np.float32) / 255
    if ombra:
        dx, dy, sig, op = ombra
        s = cv2.warpAffine(o[:, :, 3], np.float32([[1, 0, dx], [0, 1, dy]]), (W, H))
        s = cv2.GaussianBlur(s.astype(np.float32) / 255, (0, 0), sig)
        contatto = cv2.GaussianBlur(o[:, :, 3].astype(np.float32) / 255, (0, 0), 3)
        scena[:] = scena * (1 - op * np.maximum(s, .6 * contatto))[:, :, None]
    scena[:] = scena * (1 - a) + o[:, :, :3].astype(np.float32) * a


def tovaglia(W, H):
    """Tovaglia di lino chiaro, con la trama e una luce morbida da sinistra."""
    base = np.array([214, 222, 226], np.float32)
    trama = .5 * rumore(H, W, .6) + .35 * cv2.GaussianBlur(rumore(H, W, 0), (0, 0), sigmaX=2.5, sigmaY=.4) \
        + .35 * cv2.GaussianBlur(rumore(H, W, 0), (0, 0), sigmaX=.4, sigmaY=2.5)
    macchie = rumore(H, W, 60)
    pieghe = rumore(H, W, 140)
    t = base * (1 + .02 * trama + .012 * macchie + .02 * pieghe)[:, :, None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    luce = 1.05 - .16 * (xx / W) - .06 * (yy / H)
    vign = 1 - .28 * (((xx - W * .45) / W) ** 2 + ((yy - H * .45) / H) ** 2) * 1.6
    return t * (luce * vign)[:, :, None]


def carta(pagina):
    """Pagina stampata su carta avorio martellata: il nero della stampa resta, il bianco diventa avorio."""
    h, w = pagina.shape[:2]
    p = pagina.astype(np.float32) / 255
    martellata = rilievo(rumore(h, w, 7, 3) + .4 * rumore(h, w, 3, 4), .011)
    fibre = 1 + .006 * rumore(h, w, 1, 5)
    return AVORIO * p * (martellata * fibre)[:, :, None]


def ottone(w, h, r=None):
    """Lastra d'ottone con riflesso orizzontale."""
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    lum = .62 + .38 * np.exp(-((yy - .3) / .18) ** 2) - .25 * yy
    base = np.array([90, 160, 205], np.float32)
    img = base * (lum * (1 + .03 * rumore(h, w, 1.2)))[:, :, None]
    a = np.full((h, w), 255, np.uint8)
    if r:
        a = angoli_arrotondati(a, r)
    return rgba(img, a)


def pagine(pg):
    """Le pagine vere della carta, senza i gialli dei punti da verificare."""
    pg.goto((QUI / "sorgenti" / "dolci-distillati.html").as_uri())
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    pg.add_style_tag(content=".tbd{background:none!important;box-shadow:none!important}")
    doc = pymupdf.open(stream=pg.pdf(prefer_css_page_size=True, print_background=True), filetype="pdf")
    out = []
    for p in doc:
        pix = p.get_pixmap(dpi=int(PX_MM * 25.4))
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3]
        out.append(cv2.cvtColor(a, cv2.COLOR_RGB2BGR))
    return out


def testo_png(pg, html, larghezza_px):
    """Testo in Cormorant renderizzato da Chrome, con fondo trasparente (per incisioni e impressioni)."""
    pg.set_content(f"""<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&display=swap">
      <style>body{{margin:0;background:transparent}} div{{font-family:'Cormorant Garamond';color:#fff;width:{larghezza_px}px;text-align:center}}</style></head>
      <body><div id="t">{html}</div></body></html>""")
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    png = pg.locator("#t").screenshot(omit_background=True)
    im = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)
    return im[:, :, 3]


def monogramma(altezza_px):
    m = cv2.imread(str(QUI / "riferimenti" / "logo" / "monogramma-champagne.png"), cv2.IMREAD_UNCHANGED)[:, :, 3]
    ys, xs = np.where(m > 10)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return cv2.resize(m, (round(m.shape[1] * altezza_px / m.shape[0]), altezza_px), interpolation=cv2.INTER_AREA)


def incolla_maschera(fondo, maschera, x, y):
    h, w = maschera.shape
    f = np.zeros(fondo.shape[:2], np.float32)
    f[y:y + h, x:x + w] = maschera.astype(np.float32) / 255
    return f


# ---------- legno vero dalle foto ----------
def tavola_menu():
    """La cartella del menù raddrizzata (legno scuro, striscia oro, viti in ottone)."""
    return raddrizza("cartella-menu.jpg", [(60, 156), (1035, 200), (1056, 1598), (64, 1650)], 1000, 1480)


def tavola_vini():
    return raddrizza("cartella-carta-dei-vini.jpg", [(36, 166), (1050, 166), (1050, 1604), (32, 1602)], 1014, 1440)


def pulisci_incisioni(img, x0, x1, chiare):
    """Toglie monogramma e scritta incisi dal pannello (zona x0–x1), per riusare il legno pulito."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2].astype(np.float32)
    loc = cv2.GaussianBlur(v, (0, 0), 25)
    m = ((v - loc) > 22) if chiare else ((loc - v) > 22)
    m = m.astype(np.uint8) * 255
    m[:, :x0] = 0
    m[:, x1:] = 0
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    return cv2.inpaint(img, m, 9, cv2.INPAINT_TELEA)


# ---------- A · cartella in cuoio ----------
def cuoio(w, h, colore=(84, 40, 22), seme=11):
    """Cuoio blu Cusin a grana fine."""
    grana = rumore(h, w, 1.1, seme) + .5 * rumore(h, w, 3, seme + 1)
    luce = rilievo(grana, .022)
    nuvole = 1 + .06 * rumore(h, w, 90, seme + 2)
    return np.array(colore, np.float32) * (luce * nuvole)[:, :, None]


def cucitura(img, margine, passo=18, lungo=11, colore=(150, 120, 92)):
    h, w = img.shape[:2]
    for x in range(margine + 6, w - margine - 6, passo):
        for y in (margine, h - margine):
            cv2.line(img, (x, y), (x + lungo, y), colore, 2, cv2.LINE_AA)
    for y in range(margine + 6, h - margine - 6, passo):
        for x in (margine, w - margine):
            cv2.line(img, (x, y), (x, y + lungo), colore, 2, cv2.LINE_AA)


def impressione(img, maschera, profondita=1.0):
    """Impressione a secco: il disegno scende nel cuoio, più scuro e con il bordo in luce."""
    alt = cv2.GaussianBlur(maschera, (0, 0), 2.2)
    sh = rilievo(-alt * 8 * profondita, .09)
    scuro = 1 - .3 * profondita * cv2.GaussianBlur(maschera, (0, 0), .8)
    return img * (sh * scuro)[:, :, None]


def mockup_a(pg, pag):
    mm = PX_MM
    pw, ph = int(210 * mm), int(297 * mm)
    bordo = int(14 * mm)
    W, H = pw + 2 * bordo, ph + 2 * bordo
    # copertina chiusa
    cop = cuoio(W, H)
    mono = monogramma(int(70 * mm))
    x = (W - mono.shape[1]) // 2
    cop = impressione(cop, incolla_maschera(cop, mono, x, int(95 * mm)))
    scr = testo_png(pg, "<span style='font-size:90px;letter-spacing:.22em;font-weight:600'>DOLCI · DISTILLATI</span>", 1400)
    ys, xs = np.where(scr > 10)
    scr = scr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = W * .66 / scr.shape[1]
    scr = cv2.resize(scr, (int(scr.shape[1] * k), int(scr.shape[0] * k)), interpolation=cv2.INTER_AREA)
    cop = impressione(cop, incolla_maschera(cop, scr, (W - scr.shape[1]) // 2, int(200 * mm)), 1.0)
    cucitura(cop, int(6 * mm))
    a = angoli_arrotondati(np.full((H, W), 255, np.uint8), int(4 * mm))
    chiusa = rgba(cop * (1 - .08 * (np.arange(W)[None, :] < 8 * mm))[:, :, None], a)

    # aperta: due pannelli, fogli negli angolini
    aperta = np.zeros((H, 2 * W + int(4 * mm), 3), np.float32)
    dentro = cuoio(aperta.shape[1], H, (76, 36, 20), 21)
    aperta[:] = dentro
    for i, foglio in enumerate(pag):
        x0 = i * (W + int(4 * mm)) + bordo
        f = carta(cv2.resize(foglio, (pw, ph), interpolation=cv2.INTER_AREA))
        sotto = np.zeros(aperta.shape[:2], np.float32)
        sotto[bordo:bordo + ph, x0:x0 + pw] = 1
        aperta *= (1 - .35 * cv2.GaussianBlur(sotto, (0, 0), 6))[:, :, None]
        aperta[bordo:bordo + ph, x0:x0 + pw] = f
        # angolini in cuoio
        l = int(19 * mm)
        for cx, cy, sx, sy in ((x0, bordo, 1, 1), (x0 + pw, bordo, -1, 1), (x0, bordo + ph, 1, -1), (x0 + pw, bordo + ph, -1, -1)):
            tri = np.array([[cx - sx * 3 * mm, cy - sy * 3 * mm], [cx + sx * l, cy - sy * 3 * mm], [cx - sx * 3 * mm, cy + sy * l]], np.int32)
            m = np.zeros(aperta.shape[:2], np.uint8)
            cv2.fillConvexPoly(m, tri, 255, cv2.LINE_AA)
            mf = m.astype(np.float32) / 255
            ombra = cv2.GaussianBlur(mf, (0, 0), 5)
            aperta *= (1 - .35 * np.clip(ombra - mf, 0, 1))[:, :, None]
            aperta = aperta * (1 - mf[:, :, None]) + dentro * 1.08 * mf[:, :, None]
            cv2.line(aperta, (int(cx + sx * l), int(cy - sy * 3 * mm)), (int(cx - sx * 3 * mm), int(cy + sy * l)), (120, 80, 56), 2, cv2.LINE_AA)
    cucitura(aperta, int(6 * mm))
    g = aperta.shape[1] // 2
    piega = np.exp(-((np.arange(aperta.shape[1]) - g) / (6 * mm)) ** 2)
    aperta *= (1 - .45 * piega)[None, :, None]
    aperta_rgba = rgba(aperta, angoli_arrotondati(np.full(aperta.shape[:2], 255, np.uint8), int(4 * mm)))
    return chiusa, aperta_rgba


# ---------- scene ----------
def scena_a(chiusa, aperta):
    out = []
    W, H = 2600, 1800
    s = tovaglia(W, H)
    h, w = chiusa.shape[:2]
    k = 1350 / h
    cx, cy = 1300, 900
    q = np.float32([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]]) * k
    a = np.radians(-6)
    R = np.float32([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    q = q @ R.T
    q[:, 1] = q[:, 1] * .93 + (q[:, 1] < 0) * 18          # un filo di prospettiva: il lato alto più lontano
    q[:, 0] = q[:, 0] * (1 - .03 * (q[:, 1] < 0))
    posa(s, chiusa, q + [cx, cy], (18, 26, 28, .5))
    out.append(("A_cartella-cuoio-chiusa.jpg", s))

    W, H = 3000, 2150
    s = tovaglia(W, H)
    h, w = aperta.shape[:2]
    k = 2700 / w
    x0, y0 = 150, (H - h * k) / 2
    q = np.float32([[x0, y0], [x0 + w * k, y0 + 20], [x0 + w * k - 8, y0 + h * k], [x0 + 8, y0 + h * k - 10]])
    posa(s, aperta, q, (16, 24, 26, .5))
    out.append(("A_cartella-cuoio-aperta.jpg", s))
    return out


def scena_b(pg):
    vini = tavola_vini()
    menu = tavola_menu()
    # la terza: legno del menù senza incisioni, più piccola (foglio A5), striscia color champagne
    nuova = pulisci_incisioni(menu.copy(), 170, 990, chiare=True)
    strisce = nuova[:, 92:146].astype(np.float32)
    grigio = strisce.mean(axis=2, keepdims=True)
    nuova[:, 92:146] = np.clip(grigio * .35 + np.array([150, 190, 214], np.float32) * (grigio / 170) * .75, 0, 255)
    h0, w0 = nuova.shape[:2]
    # monogramma e scritta incisi in oro, come sulla cartella del menù
    oro = np.array([70, 150, 196], np.float32)
    def incidi(img, mask, x, y):
        f = incolla_maschera(img, mask, x, y)[:, :, None]
        tex = 1 + .08 * rumore(img.shape[0], img.shape[1], 1)[:, :, None]
        return img * (1 - f) + oro * tex * f
    nuova = nuova.astype(np.float32)
    mono = monogramma(330)
    nuova = incidi(nuova, mono, 580 - mono.shape[1] // 2, 330)
    scr = testo_png(pg, "<span style='font-size:92px;font-weight:500'>Dolci · Distillati</span>", 900)
    scr = cv2.resize(scr, (int(scr.shape[1] * .78), int(scr.shape[0] * .78)))
    nuova = incidi(nuova, scr, 580 - scr.shape[1] // 2, 820)
    nuova = cv2.resize(nuova, (int(w0 * .72), int(h0 * .72)), interpolation=cv2.INTER_AREA)

    W, H = 3200, 2000
    s = tovaglia(W, H)
    def pz(img, x, y, altezza, rot):
        h, w = img.shape[:2]
        k = altezza / h
        q = np.float32([[0, 0], [w, 0], [w, h], [0, h]]) * k
        c = q.mean(axis=0)
        a = np.radians(rot)
        R = np.float32([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        q = (q - c) @ R.T + [x, y]
        o = rgba(img.astype(np.float32), angoli_arrotondati(np.full((h, w), 255, np.uint8), 14))
        posa(s, o, q, (18, 28, 30, .5))
    vini, menu = vini[6:-6, 4:-6], menu[10:-6, 4:-10]
    pz(vini, 760, 1000, 1500, -4)
    pz(menu, 1720, 960, 1540, 2)
    pz(nuova, 2620, 1150, 1540 * .72 * 1480 / 1480, -3)
    return [("B_trittico-cartelle.jpg", s)]


def scena_c(pag):
    """Leggio da tavolo in legno con il foglio dei dolci e una mensola d'ottone."""
    mm = PX_MM
    vini = tavola_vini()
    legno = pulisci_incisioni(vini.copy(), 170, 1000, chiare=False)[40:-40, 260:-30]
    pw, ph = int(210 * mm), int(297 * mm)
    bw, bh = pw + int(24 * mm), ph + int(40 * mm)
    tav = cv2.resize(legno, (bw, bh)).astype(np.float32)
    f = carta(cv2.resize(pag[0], (pw, ph), interpolation=cv2.INTER_AREA))
    x0, y0 = int(12 * mm), int(12 * mm)
    ombra = np.zeros((bh, bw), np.float32)
    ombra[y0:y0 + ph, x0:x0 + pw] = 1
    tav *= (1 - .4 * cv2.GaussianBlur(ombra, (0, 0), 8))[:, :, None]
    tav[y0:y0 + ph, x0:x0 + pw] = f
    mens = ottone(bw, int(16 * mm))
    tav[bh - mens.shape[0]:, :] = mens[:, :, :3]
    tav[bh - mens.shape[0] - 6:bh - mens.shape[0], :] *= .55
    leggio = rgba(tav, angoli_arrotondati(np.full((bh, bw), 255, np.uint8), 10))

    W, H = 2400, 2000
    s = tovaglia(W, H)
    k = 1650 / bh
    w, h = bw * k, bh * k
    cx, base = 1200, 1850
    # inclinato all'indietro: la parte alta è più stretta e più corta
    q = np.float32([[cx - w * .45, base - h * .93], [cx + w * .45, base - h * .93], [cx + w / 2, base], [cx - w / 2, base]])
    # ombra lunga sul tavolo, verso destra e indietro
    posa(s, leggio, q, (90, -40, 40, .32))
    return [("C_leggio.jpg", s)]


def tavoletta(foglio, legno):
    """Tavoletta in legno scuro con molla d'ottone in alto e il foglio sotto la molla (una faccia)."""
    mm = PX_MM
    pw, ph = int(210 * mm), int(297 * mm)
    bw, bh = pw + int(20 * mm), ph + int(36 * mm)
    tav = cv2.resize(legno, (bw, bh)).astype(np.float32)
    f = carta(cv2.resize(foglio, (pw, ph), interpolation=cv2.INTER_AREA))
    x0, y0 = int(10 * mm), int(26 * mm)
    ombra = np.zeros((bh, bw), np.float32)
    ombra[y0:y0 + ph, x0:x0 + pw] = 1
    tav *= (1 - .45 * cv2.GaussianBlur(ombra, (0, 0), 8))[:, :, None]
    tav[y0:y0 + ph, x0:x0 + pw] = f
    # molla
    mw, mh = int(110 * mm), int(30 * mm)
    molla = ottone(mw, mh, int(5 * mm))
    mx, my = (bw - mw) // 2, int(10 * mm)
    sotto = np.zeros((bh, bw), np.float32)
    sotto[my + 10:my + mh + 14, mx + 6:mx + mw + 6] = 1
    tav *= (1 - .5 * cv2.GaussianBlur(sotto, (0, 0), 7))[:, :, None]
    a = molla[:, :, 3:4].astype(np.float32) / 255
    tav[my:my + mh, mx:mx + mw] = tav[my:my + mh, mx:mx + mw] * (1 - a) + molla[:, :, :3] * a
    # rivetti e leva
    for rx in (mx + int(14 * mm), mx + mw - int(14 * mm)):
        cv2.circle(tav, (rx, my + mh // 2), int(3 * mm), (60, 110, 150), -1, cv2.LINE_AA)
        cv2.circle(tav, (rx - 3, my + mh // 2 - 3), int(1.4 * mm), (150, 210, 240), -1, cv2.LINE_AA)
    leva = ottone(int(50 * mm), int(9 * mm), int(4 * mm))
    lx, ly = (bw - leva.shape[1]) // 2, my - int(4 * mm)
    a = leva[:, :, 3:4].astype(np.float32) / 255
    tav[ly:ly + leva.shape[0], lx:lx + leva.shape[1]] = tav[ly:ly + leva.shape[0], lx:lx + leva.shape[1]] * (1 - a) + leva[:, :, :3] * a
    # bordo smussato: un filo di luce in alto a sinistra e di ombra in basso a destra
    alfa = angoli_arrotondati(np.full((bh, bw), 255, np.uint8), int(6 * mm))
    d = cv2.distanceTransform((alfa > 0).astype(np.uint8), cv2.DIST_L2, 5)
    smusso = np.clip(1 - d / (2.2 * mm), 0, 1)
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    lato = np.where((xx < bw * .5) & (yy < bh * .5), 1.18, .78)
    tav *= (1 + smusso * (lato - 1))[:, :, None]
    return rgba(tav, alfa)


def posa_tavoletta(s, tav, centro, altezza, gradi):
    """Posa la tavoletta con il suo spessore (10 mm di legno visti di sbieco) e l'ombra."""
    bh, bw = tav.shape[:2]
    k = altezza / bh
    w, h = bw * k, bh * k
    q = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    a = np.radians(gradi)
    R = np.float32([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    q = (q - [w / 2, h / 2]) @ R.T + centro
    spessore = tav.copy()
    spessore[:, :, :3] = (spessore[:, :, :3].astype(np.float32) * .42).astype(np.uint8)
    for t in (9, 6, 3):
        posa(s, spessore, q + [t * .6, t], (22, 30, 28, .5) if t == 9 else None)
    posa(s, tav, q, None)


def scena_d(pag):
    """Versione scelta: la tavoletta a due facce, dolci davanti e distillati dietro."""
    menu = tavola_menu()
    legno = pulisci_incisioni(menu.copy(), 170, 990, chiare=True)[60:-40, 240:-40]
    fronte = tavoletta(pag[0], legno)
    retro = tavoletta(pag[1], cv2.flip(legno, 1))      # l'altra faccia: lo stesso legno visto dall'altro lato
    out = []
    W, H = 3400, 2200
    s = tovaglia(W, H)
    posa_tavoletta(s, fronte, [960, 1100], 1950, -4)
    posa_tavoletta(s, retro, [2440, 1100], 1950, 3)
    out.append(("D_tavoletta-due-facce.jpg", s))
    for nome, tav, g in (("D_tavoletta-fronte-dolci.jpg", fronte, 5), ("D_tavoletta-retro-distillati.jpg", retro, -4)):
        s = tovaglia(2400, 2100)
        posa_tavoletta(s, tav, [1200, 1040], 1850, g)
        out.append((nome, s))
    return out


def main():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.route("https://fonts.googleapis.com/**", scarica)
        pg.route("https://fonts.gstatic.com/**", scarica)
        pag = pagine(pg)
        chiusa, aperta = mockup_a(pg, pag)
        immagini = scena_a(chiusa, aperta) + scena_b(pg) + scena_c(pag) + scena_d(pag)
        b.close()
    pdf = pymupdf.open()
    for nome, img in immagini:
        img = np.clip(img, 0, 255).astype(np.uint8)
        cv2.imwrite(str(OUT / nome), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        h, w = img.shape[:2]
        p = pdf.new_page(width=842, height=842 * h / w)
        p.insert_image(p.rect, filename=str(OUT / nome))
        print("creato mockup/" + nome)
    pdf.save(QUI / "pdf" / "Mockup-supporti-dolci-distillati.pdf")
    print("creato pdf/Mockup-supporti-dolci-distillati.pdf")


if __name__ == "__main__":
    main()
