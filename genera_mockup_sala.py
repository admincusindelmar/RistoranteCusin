#!/usr/bin/env python3
"""
Mockup della tavoletta dei dolci e dei distillati sui tavoli veri di Cusin (foto in riferimenti/sala/).

La prospettiva del tavolo si ricava da ogni foto: due punti di fuga presi dalle linee del tavolo e
dell'orizzonte, la focale dalla loro ortogonalità, la scala da un oggetto di misura nota (il tovagliolo).
Il verso della tavoletta segue quello delle forchette (i rebbi verso il lato opposto a chi siede). La tavoletta è quella di genera_mockup.py, con la sua altezza (1 cm), l'ombra del sole
nella direzione delle ombre della foto e la luce della scena.

    mockup/Sala_tavolo-tramonto.jpg (+ _dettaglio)   due tavolette sul tavolo grande, al tramonto
    mockup/Sala_tavolo-sera.jpg (+ _dettaglio)       le stesse, nella foto della sera

Uso: python3 genera_mockup_sala.py
"""
import cv2
import numpy as np
from playwright.sync_api import sync_playwright

import genera_mockup as gm
from genera_cloud import CHROME, scarica

SALA = gm.QUI / "riferimenti" / "sala"
BW_CM, BH_CM = 23.0, 33.7          # tavoletta: foglio A4 più 1 cm ai lati, 2,6 cm sopra e 1 cm sotto


class Piano:
    """Il piano del tavolo visto dalla fotocamera: punti in cm sul tavolo → pixel nella foto."""

    def __init__(self, dim, vx, vy, origine, rif, verso_x=1):
        w, h = dim
        c = np.array([w / 2, h / 2])
        vx, vy = np.array(vx, float), np.array(vy, float)
        f = np.sqrt(-np.dot(vx - c, vy - c))
        self.K = np.array([[f, 0, c[0]], [0, f, c[1]], [0, 0, 1]])
        Ki = np.linalg.inv(self.K)
        def dir_(v, verso):
            d = Ki @ np.array([v[0], v[1], 1.0])
            return verso * d / np.linalg.norm(d)
        self.r1 = dir_(vx, verso_x)
        self.r2 = dir_(vy, 1)
        self.n = np.cross(self.r1, self.r2)
        self.n /= np.linalg.norm(self.n)
        if self.n[1] > 0:                      # la normale deve puntare verso l'alto della scena
            self.n = -self.n
        o = Ki @ np.array([origine[0], origine[1], 1.0])
        self.o_dir = o / np.linalg.norm(o)
        # scala: un segmento lungo L cm sull'asse X, centrato sull'origine, misura rif_px nella foto
        L, rif_px = rif
        self.d = 200.0
        for _ in range(40):                    # la misura in pixel è quasi inversa alla distanza: si converge in fretta
            a, b = self.px(-L / 2, 0), self.px(L / 2, 0)
            self.d *= np.linalg.norm(a - b) / rif_px
        self.f = f

    def px(self, X, Y, Z=0.0):
        P = self.d * self.o_dir + X * self.r1 + Y * self.r2 + Z * self.n
        p = self.K @ P
        return p[:2] / p[2]


def angoli(piano, cx, cy, gradi, z=0.0, w=BW_CM, h=BH_CM):
    """Quattro angoli (TL, TR, BR, BL dell'immagine della tavoletta) sul tavolo: in alto la molla, lontana."""
    a = np.radians(gradi)
    ux = np.array([np.cos(a), np.sin(a)])        # verso destra della tavoletta
    uy = np.array([-np.sin(a), np.cos(a)])       # verso la molla (lontano)
    c = np.array([cx, cy])
    pts = [c - ux * w / 2 + uy * h / 2, c + ux * w / 2 + uy * h / 2, c + ux * w / 2 - uy * h / 2, c - ux * w / 2 - uy * h / 2]
    return np.float32([piano.px(p[0], p[1], z) for p in pts])


def metti(foto, tav, piano, cx, cy, gradi, luce, sole, ombra_forza, ombra_morbida):
    """Posa la tavoletta sul tavolo: ombra portata, spessore di 1 cm, faccia con la luce della scena."""
    H, W = foto.shape[:2]
    # prima si rimpicciolisce la tavoletta vicino alla misura finale (come una mipmap): evita i bordi seghettati
    q = angoli(piano, cx, cy, gradi)
    lato_px = max(np.linalg.norm(q[0] - q[1]), np.linalg.norm(q[1] - q[2]), np.linalg.norm(q[2] - q[3]), np.linalg.norm(q[3] - q[0]))
    k = min(1.0, 2 * lato_px / max(tav.shape[:2]))
    tav = cv2.resize(tav, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    h, w = tav.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    def warp(img, quad, interp=cv2.INTER_LINEAR):
        M = cv2.getPerspectiveTransform(src, quad)
        return cv2.warpPerspective(img, M, (W, H), flags=interp)
    alfa = tav[:, :, 3]
    # ombra: la sagoma spostata sul tavolo nella direzione delle ombre della foto
    sx, sy = sole
    q_ombra = angoli(piano, cx + sx, cy + sy, gradi)
    om = warp(alfa, q_ombra).astype(np.float32) / 255
    base = warp(alfa, angoli(piano, cx, cy, gradi)).astype(np.float32) / 255
    om = np.maximum(cv2.GaussianBlur(om, (0, 0), ombra_morbida), cv2.GaussianBlur(base, (0, 0), 2) * .8)
    foto *= (1 - ombra_forza * om)[:, :, None]
    # spessore: dal tavolo (z=0) alla faccia (z=1 cm), legno in ombra
    lato = tav.copy()
    lato[:, :, :3] = (lato[:, :, :3].astype(np.float32) * .5).astype(np.uint8)
    for z in np.linspace(0, .95, 14):
        o = warp(lato, angoli(piano, cx, cy, gradi, z), cv2.INTER_LINEAR).astype(np.float32)
        a = o[:, :, 3:4] / 255
        foto[:] = foto * (1 - a) + o[:, :, :3] * a
    faccia = tav.astype(np.float32)
    faccia[:, :, :3] = np.clip(faccia[:, :, :3] * np.array(luce, np.float32), 0, 255)
    o = warp(np.clip(faccia, 0, 255).astype(np.uint8), angoli(piano, cx, cy, gradi, 1.0))
    a = o[:, :, 3:4].astype(np.float32) / 255
    foto[:] = foto * (1 - a) + o[:, :, :3].astype(np.float32) * a


def grana(foto, forza=2.2):
    """Un filo di rumore uguale su tutta la foto, così la parte aggiunta ha la stessa grana."""
    return foto + forza * gm.rumore(foto.shape[0], foto.shape[1], .6)[:, :, None]


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.route("https://fonts.googleapis.com/**", scarica)
        pg.route("https://fonts.gstatic.com/**", scarica)
        pag = gm.pagine(pg)
        b.close()
    menu = gm.tavola_menu()
    legno = gm.pulisci_incisioni(menu.copy(), 170, 990, chiare=True)[60:-40, 240:-40]
    fronte = gm.tavoletta(pag[0], legno)
    retro = gm.tavoletta(pag[1], cv2.flip(legno, 1))

    scene = [
        # foto, punti di fuga (dai bordi del tavolo, sull'orizzonte del mare), origine e misura nota
        # (un tovagliolo piegato, 20 cm), zona di tovaglia da cui prendere la luce, tavolette, ritaglio
        ("sala-5.jpg", "Sala_tavolo-tramonto", dict(vx=(3303, 603), vy=(-936, 603), origine=(740, 946), rif=(20, 157)),
         (940, 960, 860, 900), [(-2, -11, 0, fronte), (52, -11, 0, retro)], (760, 1140, 420, 1380)),
        ("sala-1.jpg", "Sala_tavolo-sera", dict(vx=(1649, 430), vy=(-272, 430), origine=(530, 668), rif=(20, 122)),
         (690, 705, 560, 620), [(-2, -11, 0, fronte), (53, -11, 0, retro)], (540, 780, 330, 980)),
    ]
    for nome_foto, nome, geo, zona, tavolette, ritaglio in scene:
        foto = cv2.imread(str(SALA / nome_foto)).astype(np.float32)
        H, W = foto.shape[:2]
        piano = Piano((W, H), **geo)
        y0, y1, x0, x1 = zona
        luce = tuple(foto[y0:y1, x0:x1].reshape(-1, 3).mean(0) / 235)
        for cx, cy, gradi, tav in tavolette:
            metti(foto, tav, piano, cx, cy, gradi, luce, sole=(0, -2.5), ombra_forza=.3, ombra_morbida=6)
        foto = np.clip(grana(foto, 1.5), 0, 255).astype(np.uint8)
        cv2.imwrite(str(gm.OUT / f"{nome}.jpg"), foto, [cv2.IMWRITE_JPEG_QUALITY, 92])
        a, b, c, d = ritaglio
        zoom = cv2.resize(foto[a:b, c:d], None, fx=1.6, fy=1.6, interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(str(gm.OUT / f"{nome}_dettaglio.jpg"), zoom, [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"creato mockup/{nome}.jpg e {nome}_dettaglio.jpg")

if __name__ == "__main__":
    main()
