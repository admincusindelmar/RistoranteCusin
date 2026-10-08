#!/usr/bin/env python3
"""
Menù A3 solo fronte (verticale, tre colonne) del Ristorante Cusin.

Stessi dati del menù A4 (genera_menu.py), senza copertina e senza pagina allergeni.
Solo in italiano: per le altre lingue c'è il riquadro del QR code in fondo all'ultima colonna.

Uso:
    python3 menu_a3.py            -> bozza (in giallo i punti da definire)
    python3 menu_a3.py --finale   -> versione pulita da stampa
"""
from playwright.sync_api import sync_playwright

from a_capo import SISTEMA_A_CAPO_JS
from genera_menu import (CRUDO_FUORI_MENU, ANTIPASTI, CONTORNI, CRUDO_PEZZI, CRUDO_SALSE_EXTRA, CRUDO_SALSE_INCLUSE,
                         DEGUSTAZIONI, FINALE, PRIMI, QUI, SECONDI, SERVIZIO, t, prezzo)


def allergeni(a, tracce=()):
    if not a and not tracce:
        return ""
    tr = f' · tracce {" · ".join(map(str, tracce))}' if tracce else ""
    return f' <span class="al">{" · ".join(map(str, a))}{tr}</span>'


def voce(p):
    """Piatto della carta: nome, descrizione con allergeni, prezzo oltre il filetto."""
    seg = ""
    if p["chef"]:
        seg += '<span class="chef">il consiglio dello Chef</span>'
    # etichette e "Vegetariano" sulla stessa riga del nome, per risparmiare spazio
    cott = '<span class="cottura">18 min</span>' if p["cottura"] else ""
    if p["etichetta"]:
        cott += f'<span class="etichetta">{p["etichetta"][0]}</span>'
    vegetariano = bool(p["nota"]) and p["nota"].startswith(("Vegetariano", "Senza lattosio"))
    if vegetariano:
        cott += f'<span class="etichetta veg">{p["nota"].split(" · ")[0]}</span>'
    desc = f'<p>{t(p["desc"])}{allergeni(p["allergeni"], p["tracce"])}</p>' if p["desc"] else ""
    nota = ""
    if p["nota"] and not vegetariano and not p["nota"].startswith("Provalo"):
        nota = f'<p class="nota">{t(p["nota"].split(" · ")[0])}</p>'
    extra = "".join(
        f'<div class="tx extra">{"<span class=extra-tit>Salse in aggiunta</span>" if i == 0 else ""}'
        f'+ {t(n)}{allergeni(al)}</div><div class="pr extra">{pr}</div>'
        for i, (n, _, pr, al) in enumerate(p["extra"]))
    return (f'<div class="v{" firma" if p["chef"] else ""}"><div class="tx">{seg}<h4>{t(p["nome"])}{cott}</h4>'
            f'{desc}{nota}</div><div class="pr">{prezzo(p["prezzo"])}</div>{extra}</div>')


def riga(nome, prezzo_txt, al=(), unita=""):
    u = f' <em>{unita}</em>' if unita else ""
    return (f'<div class="v corta"><div class="tx"><h4>{t(nome)}{u}{allergeni(al)}</h4></div>'
            f'<div class="pr">{prezzo_txt}</div></div>')


def sezione(titolo, corpo, classe=""):
    return f'<section class="sez {classe}"><h2>{titolo}</h2><div class="riga"></div>{corpo}</section>'


def degustazione(d):
    """Degustazione compatta per la fascia in alto: prezzo accanto al nome, portata a sinistra dei piatti."""
    portate = ""
    for nome_portata, _, piatti in d["portate"]:
        # basta la descrizione completa, che contiene già il nome del piatto
        voci = "".join(f'<li>{t(p["desc"] or p["nome"])}{allergeni(p["allergeni"], p["tracce"])}</li>' for p in piatti)
        portate += f'<div class="portata"><h5>{nome_portata}</h5><ul>{voci}</ul></div>'
    return f"""<section class="deg">
  <div class="deg-testa"><h3>{t(d['nome'])}</h3>
    <div class="deg-prezzo"><span>{d['prezzo']}</span><em>a persona</em></div></div>
  {portate}
</section>"""


def crudo():
    """Il crudo in blocchi brevi, così può continuare nella colonna successiva.
    Nell'A3 non ci sono i calici di bollicine."""
    righe = [riga(n, prezzo(pr), al, unita) for n, _, unita, _, pr, al in CRUDO_PEZZI]
    meta = len(righe) // 2
    extra = "".join(riga("+ " + n, pr, al) for n, _, pr, al in CRUDO_SALSE_EXTRA)
    incluse = " e ".join(CRUDO_SALSE_INCLUSE)
    passo1a = (f'<section class="sez apre"><p class="crudo-tit">Componi il tuo Crudo</p>'
               f'<p class="passo"><span>1</span> Scegli i tuoi pezzi</p><div class="elenco">{"".join(righe[:meta])}</div></section>')
    passo1b = (f'<div><div class="elenco">{"".join(righe[meta:])}</div>'
               f'<p class="fuori-menu">{CRUDO_FUORI_MENU[0]}</p></div>')
    passo2 = (f'<div class="chiude"><p class="passo"><span>2</span> Abbina le salse</p>'
              f'<p class="incluse">Incluse: {incluse.lower()}{allergeni((3,))}</p><div class="elenco">{extra}</div></div>')
    return [(passo1a, "Il Crudo", False), (passo1b, "Il Crudo", True), (passo2, "Il Crudo", True)]


def sezione_divisibile(titolo, voci, coda=""):
    """Sezione che può continuare nella colonna successiva, ma solo tra un piatto e l'altro."""
    out = [(f'<section class="sez apre"><h2>{titolo}</h2><div class="riga"></div>'
            f'<div class="elenco">{voci[0]}</div></section>', titolo, False)]
    for v in voci[1:]:
        out.append((f'<div class="elenco segue-voce">{v}</div>', titolo, True))
    if coda:
        out.append((coda, titolo, True))
    out[-1] = (out[-1][0].replace('class="elenco segue-voce"', 'class="elenco segue-voce chiude"', 1)
               if 'segue-voce' in out[-1][0] else f'<div class="chiude">{out[-1][0]}</div>', titolo, out[-1][2])
    return out


QR = """<section class="qr">
  <div class="qr-box">{qr_img}</div>
  <div class="qr-testo">
    <p class="qr-it">Il menù nella tua lingua</p>
    <p>Menu in English · Deutsch · Français · Español</p>
    <p class="qr-em">Inquadra il codice con la fotocamera · Scan the code with your camera</p>
  </div>
</section>"""


def blocchi():
    """Le sezioni della carta, nell'ordine di lettura: (html, sezione, è_continuazione).
    Le degustazioni stanno a parte, nella fascia in alto."""
    return (sezione_divisibile("Antipasti", [voce(p) for p in ANTIPASTI]) +
            crudo() +
            sezione_divisibile("Primi Piatti", [voce(p) for p in PRIMI]) +
            sezione_divisibile("Secondi Piatti", [voce(p) for p in SECONDI]) +
            sezione_divisibile("Contorni", [riga(c["nome"], prezzo(c["prezzo"])) for c in CONTORNI]))


def qr_code():
    """QR del menù nelle altre lingue (https://menu.cooperto.it/3db5ce48-20f6-4875-925b-bf8afc0415e9)."""
    import base64
    f = QUI / "qr" / "qr_menu_lingue.png"
    if not f.exists():
        return "<span>spazio per il<br>QR code</span>"
    return f'<img alt="QR code menù" src="data:image/png;base64,{base64.b64encode(f.read_bytes()).decode()}">'


def logo():
    """Il sigillo del ristorante (estratto dal file vettoriale con estrai_logo.py)."""
    f = QUI / "logo" / "logo_cusin_sigillo_champagne.svg"           # colore originale del logo
    return f.read_text() if f.exists() else "<span>logo</span>"


def documento(colonne):
    """colonne: liste di blocchi, una per colonna."""
    font = (QUI / "fonts.css").read_text()
    def colonna(c):
        html_c = "".join(h for h, _, _ in c)
        if c and c[0][2]:                                          # la sezione continua da sinistra
            html_c = f'<p class="segue">{c[0][1]} <em>segue</em></p>' + html_c
        return f'<div class="col">{html_c}</div>'
    html_col = "".join(colonna(c) for c in colonne)
    bozza = "" if FINALE else '<div class="bozza">BOZZA · in giallo i punti da definire</div>'
    servizio = "".join(f'<span>{a}<i>{c}</i></span>' for a, _, c in SERVIZIO)
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Menu Ristorante Cusin A3</title>
<style>{font}{CSS}</style></head><body>{bozza}
<main class="foglio">
  <header class="testa"><div></div><div class="nome"><div class="logo">{logo()}</div><div><h1>Ristorante Cusin</h1><p>La Carta · Stagione 2026</p></div></div>{QR.replace("{qr_img}", qr_code())}</header>
  <section class="fascia-deg"><h2>Le Degustazioni</h2>
    <div class="tre">{"".join(degustazione(d) for d in DEGUSTAZIONI)}</div>
    <p class="nota-deg">I menù degustazione sono serviti per l'intero tavolo</p></section>
  <h2 class="tit-carta">La Carta</h2>
  <div class="colonne" style="grid-template-columns: repeat({len(colonne)}, 1fr)">{html_col}</div>
  <footer class="piede"><p class="servizio"><b>Servizio</b>{servizio}</p><p>I numeri accanto ai piatti indicano gli allergeni (Reg. UE 1169/2011): «tracce»: può contenerne tracce. Legenda e
  informazioni complete presso il nostro personale. Il pesce servito crudo è sottoposto ad abbattimento
  (Reg. CE 853/2004).</p></footer>
</main></body></html>"""


def dividi(altezze, n, extra_inizio=()):
    """Divide i blocchi (in ordine) in n colonne contigue riducendo al minimo la colonna più alta.
    extra_inizio[i] = altezza aggiunta se la colonna comincia dal blocco i (la scritta "segue")."""
    extra_inizio = extra_inizio or [0] * len(altezze)
    from functools import lru_cache
    pref = [0]
    for h in altezze:
        pref.append(pref[-1] + h)

    @lru_cache(None)
    def migliore(i, k):
        if k == 1:
            return pref[-1] - pref[i] + extra_inizio[i], (len(altezze),)
        best = (float("inf"), ())
        for j in range(i + 1, len(altezze) - k + 2):
            resto, tagli = migliore(j, k - 1)
            alto = max(pref[j] - pref[i] + extra_inizio[i], resto)
            if alto < best[0]:
                best = (alto, (j,) + tagli)
        return best

    alto, tagli = migliore(0, n)
    inizio, gruppi = 0, []
    for fine in tagli:
        gruppi.append(list(range(inizio, fine)))
        inizio = fine
    return alto, gruppi


CSS = """
@page { size: A3 landscape; margin: 0; }
:root { --inchiostro:#191919; --tenue:#6d6d74; --filo:#afafb2; --filo-testa:#3d3d3b; --oro:#a88a4a; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: none; color: var(--inchiostro); font-family: 'Cormorant Garamond', Georgia, serif;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
mark { background: #fff1a8; color: #6b5200; padding: 0 2px; border-radius: 2px; font-style: normal; }
.segue { font-size: 9.5pt; font-weight: 700; letter-spacing: .24em; text-transform: uppercase; color: var(--tenue); margin-bottom: .8mm; line-height: 1.1; }
.segue em { font-weight: 400; font-style: italic; letter-spacing: .06em; text-transform: none; }
.sez.apre { margin-bottom: 0; }
.chiude { margin-bottom: 3.5mm; }
/* fascia delle degustazioni in alto, una accanto all'altra */
.fascia-deg h2, .tit-carta { text-align: center; font-size: 14pt; font-weight: 700; letter-spacing: .3em; text-transform: uppercase; }
.fascia-deg h2 { margin-bottom: 2mm; }
.fascia-deg .tre { display: grid; grid-template-columns: 1.42fr 1fr 1fr; column-gap: 8mm; }
.fascia-deg .qr { margin: 2mm 0 1mm 0; padding: 2.4mm; }
.fascia-deg .qr-box { width: 26mm; height: 26mm; }
.fascia-deg .deg { border-bottom: 0; margin-bottom: 0; padding: 0 2mm 2mm; }
.fascia-deg .tre > * + * { border-left: .3mm solid #d6d6da; margin-left: -4mm; padding-left: 6mm; }
.fascia-deg .deg { text-align: left; }
.deg-testa { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.6mm;
  padding-bottom: 1mm; border-bottom: .3mm solid #d6d6da; }
.deg-testa h3 { font-size: 18pt; margin: 0; }
.deg-testa .deg-prezzo span { font-size: 17pt; }
.fascia-deg .portata { display: grid; grid-template-columns: 21mm 1fr; column-gap: 2mm; margin-bottom: 1mm; }
.fascia-deg .portata h5 { margin: .5mm 0 0; font-size: 8.5pt; letter-spacing: .18em; }
.fascia-deg .portata li { font-size: 11pt; line-height: 1.2; margin-bottom: .6mm; }
.nota-deg { text-align: center; font-size: 10.5pt; font-weight: 600; margin-top: 1mm; }
.testa h1 { color: #DEC38D; }
.testa .nome { display: flex; align-items: center; gap: 6mm; text-align: center; }
.testa .nome p { margin-top: .6mm; }
.logo svg { height: 16mm; width: auto; display: block; }
.logo:has(span) { width: 18mm; height: 18mm; border: .4mm dashed var(--tenue); }
.logo { display: flex; align-items: center; justify-content: center;
  font-size: 8pt; letter-spacing: .2em; text-transform: uppercase; color: var(--tenue); }
.testa .qr { justify-self: end; margin: 0; padding: 0; border: 0; gap: 3mm; }
.testa .qr-box { width: 19mm; height: 19mm; font-size: 7.5pt; }
.qr-box:has(img) { border: 0; }
.qr-box img { width: 100%; height: 100%; image-rendering: pixelated; display: block; }
.testa .qr-testo p { font-size: 9.5pt; line-height: 1.2; }
.testa .qr-testo .qr-it { font-size: 14pt; }
.testa .qr-testo .qr-em { display: none; }
.tit-carta { margin: 1.5mm 0 2mm; padding-top: 2.2mm; border-top: .53mm solid var(--filo-testa); }
p, h3, h4, li { text-wrap: pretty; }
.fuori-menu { font-size: 10.5pt; font-style: italic; color: var(--oro); margin: .6mm 0 1.4mm; line-height: 1.2; }
.bozza { position: fixed; top: 4mm; left: 6mm; font-size: 8pt; letter-spacing: .2em; color: #a08400; }
.foglio { width: 420mm; height: 297mm; padding: 11mm 14mm 9mm; position: relative; display: flex; flex-direction: column; }

.testa { display: grid; grid-template-columns: 1fr auto 1fr; column-gap: 8mm; align-items: center; margin-bottom: 4mm;
  padding-bottom: 2mm; border-bottom: .53mm solid var(--filo-testa); }
.testa h1 { font-size: 26pt; font-weight: 700; letter-spacing: .32em; text-transform: uppercase; padding-left: .32em; }
.testa .filo { width: 80mm; height: .53mm; background: var(--filo-testa); margin: 1.6mm auto 1.4mm; }
.testa p { font-size: 13pt; font-weight: 300; letter-spacing: .14em; }

.colonne { flex: 1; min-height: 0; display: grid; column-gap: 8mm; }
.col { min-height: 0; display: flex; flex-direction: column; }
.col + .col { border-left: .3mm solid #d6d6da; margin-left: -4mm; padding-left: 4mm; }
.sez { margin-bottom: 3.5mm; }
.sez.degustazioni { break-inside: auto; }
.sez h2 { font-size: 15pt; font-weight: 700; letter-spacing: .26em; text-transform: uppercase; }
.sez .riga { height: .4mm; background: var(--filo-testa); margin: 1.2mm 0 3mm; width: 100%; }

/* voci della carta: prezzo dopo un filetto verticale continuo, senza simbolo dell'euro */
.elenco { display: flex; flex-direction: column; }
.elenco.due { display: grid; grid-template-columns: 1fr 1fr; column-gap: 4mm; }
.elenco.due h4 { font-size: 11pt; }
.v { display: grid; grid-template-columns: 1fr 12mm; break-inside: avoid; }
.v .tx { padding: 0 3mm .8mm 0; }
.v .pr { border-left: .45mm solid var(--filo); padding-left: 2.6mm; font-size: 12pt; font-weight: 700; padding-top: .4mm; }
.v.corta .tx { padding-bottom: .5mm; }
.v h4 { font-size: 12pt; font-weight: 700; line-height: 1.2; }
.v h4 em { font-weight: 400; font-size: 11pt; color: var(--tenue); }
.v p { font-size: 10.5pt; line-height: 1.2; }
.v p.nota { font-style: italic; color: var(--oro); font-size: 10.5pt; }
.al { font-size: 8.5pt; letter-spacing: .04em; color: var(--tenue); margin-left: 1.6mm; white-space: nowrap; font-weight: 400; }
.al::before { content: "·"; margin-right: 1.2mm; }
.al.a-capo::before { content: none; }
.chef { display: block; font-family: 'Caveat', cursive; font-weight: 600; font-size: 13pt; color: var(--oro); line-height: 1; margin-bottom: .6mm; }
.etichetta { display: inline-block; font-size: 8pt; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: var(--oro); line-height: 1; margin-left: 2mm; white-space: nowrap; }
.etichetta::before { content: "✦"; margin-right: 1.4mm; letter-spacing: 0; }
.cottura { font-family: 'Caveat', cursive; font-weight: 600; font-size: 12pt; color: var(--oro); margin-left: 2mm; white-space: nowrap; }
.v.firma .tx { border: .3mm solid #c9bb95; padding: 1.6mm 2.4mm; margin: 0 2.4mm 2.6mm -2.4mm; }
.tx.extra { font-size: 11pt; padding-bottom: .6mm; }
.extra-tit { display: block; font-size: 8.5pt; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--oro); margin-top: 1.8mm; }
.pr.extra { font-size: 11pt; font-weight: 600; display: flex; align-items: flex-end; padding-bottom: .6mm; }
.nota-pasta { font-size: 10.5pt; font-weight: 700; line-height: 1.3; margin-top: 2mm; }

/* degustazioni */
.deg { break-inside: avoid; text-align: center; padding: 1.5mm 2mm 3mm; margin-bottom: 3mm; border-bottom: .3mm solid #d6d6da; }
.deg:last-child { border-bottom: 0; }
.deg-tipo { font-size: 9pt; letter-spacing: .3em; text-transform: uppercase; color: var(--oro); font-weight: 600; }
.deg h3 { font-size: 19pt; font-weight: 400; letter-spacing: .05em; line-height: 1.1; margin-top: .6mm; }
.deg-sotto { font-size: 10.5pt; font-style: italic; color: var(--tenue); margin-bottom: 1.6mm; }
.portata { margin-bottom: 1.2mm; }
.portata h5 { font-size: 9pt; font-weight: 600; letter-spacing: .26em; text-transform: uppercase; color: var(--oro); margin-bottom: .6mm; }
.portata ul { list-style: none; }
.portata li { margin-bottom: .8mm; }
.portata h4 { font-size: 11.5pt; font-weight: 700; line-height: 1.15; }
.portata p { font-size: 11pt; line-height: 1.2; }
.deg-prezzo { display: inline-flex; align-items: center; gap: 2.4mm; padding: 0 5mm;
  border-left: .45mm solid var(--filo); border-right: .45mm solid var(--filo); }
.deg-prezzo span { font-size: 19pt; font-weight: 600; }
.deg-prezzo em { font-size: 10pt; color: var(--tenue); }
.deg-piede { display: flex; justify-content: center; align-items: center; gap: 4mm; margin-top: 1mm; }
.deg-nota { font-size: 10.5pt; font-weight: 600; text-align: left; line-height: 1.15; }

/* crudo */
.crudo-tit { font-family: 'Caveat', cursive; font-weight: 600; font-size: 21pt; color: var(--oro); line-height: 1; margin-bottom: 1.6mm; }
.passo { font-size: 10pt; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; margin: 1.6mm 0 1.2mm; }
.passo span { display: inline-block; width: 5.4mm; height: 5.4mm; border: .3mm solid var(--oro); border-radius: 50%;
  text-align: center; line-height: 5mm; font-family: 'Caveat', cursive; font-size: 12pt; color: var(--oro); letter-spacing: 0; margin-right: 1.2mm; }
.incluse { font-size: 11pt; margin-bottom: 1.2mm; }

/* QR code */
.qr { display: flex; gap: 4mm; align-items: center; border: .3mm solid #c9bb95; padding: 3.5mm; margin-top: 2mm; }
.qr-box { flex: none; width: 32mm; height: 32mm; border: .4mm dashed var(--tenue); display: flex; align-items: center;
  justify-content: center; text-align: center; font-size: 9pt; color: var(--tenue); letter-spacing: .08em; }
.qr-testo p { font-size: 10.5pt; line-height: 1.3; }
.qr-testo .qr-it { font-family: 'Caveat', cursive; font-weight: 600; font-size: 17pt; color: var(--oro); line-height: 1; margin-bottom: 1mm; }
.qr-testo .qr-em { font-style: italic; color: var(--tenue); font-size: 10pt; margin-top: 1mm; }

.piede p { white-space: nowrap; font-size: 8.5pt; }
.piede .servizio { font-size: 12pt; color: var(--inchiostro); margin-bottom: 1.4mm; }
.servizio b { letter-spacing: .24em; text-transform: uppercase; font-size: 11pt; margin-right: 5mm; }
.servizio span { margin-right: 9mm; }
.servizio i { font-style: normal; font-weight: 700; border-left: .45mm solid var(--filo); padding-left: 2.4mm; margin-left: 2.4mm; }
.piede { margin-top: 2.5mm; padding-top: 1.6mm; border-top: .3mm solid #d6d6da; font-size: 9pt; color: var(--tenue);
  text-align: center; line-height: 1.3; }
"""


MISURA_JS = """() => {
    const MM = 96 / 25.4, col = document.querySelector('.col');
    const disponibile = document.querySelector('.colonne').getBoundingClientRect().height / MM;
    const altezze = [...col.children].map(e => {
        const st = getComputedStyle(e);
        return (e.getBoundingClientRect().height + parseFloat(st.marginTop) + parseFloat(st.marginBottom)) / MM;
    });
    return {altezze, disponibile};
}"""


def main(n_colonne=4):
    # file semi-definitivo: mancano solo i prezzi e il logo
    nome = "A3_DEFINITIVO_Menu_Cusin_2026" if FINALE else "A3_SEMIDEFINITIVO_Menu_Cusin_2026"
    f_html = QUI / f"{nome}.html"
    tutti = blocchi()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = browser.new_page()
        # 1) misura ogni blocco alla larghezza di una colonna
        prova = [tutti] + [[] for _ in range(n_colonne - 1)]
        segue_mm = 5                                                        # la scritta "segue" in cima alla colonna
        extra = [segue_mm if cont else 0 for _, sez, cont in tutti]
        f_html.write_text(documento(prova), encoding="utf-8")
        pg.goto(f_html.resolve().as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.evaluate(SISTEMA_A_CAPO_JS)
        misure = pg.evaluate(MISURA_JS)
        print("  altezze blocchi (mm):", [round(h) for h in misure["altezze"]], "totale", round(sum(misure["altezze"])))
        alto, gruppi = dividi(misure["altezze"], n_colonne, extra)
        print(f"  colonna più alta {alto:.0f} mm su {misure['disponibile']:.0f} mm disponibili")
        if alto > misure["disponibile"]:
            raise SystemExit("STOP: il contenuto non sta nell'A3")
        # 2) impagina le colonne bilanciate
        f_html.write_text(documento([[tutti[i] for i in g] for g in gruppi]), encoding="utf-8")
        pg.goto(f_html.resolve().as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.evaluate(SISTEMA_A_CAPO_JS)
        pg.pdf(path=str(QUI / f"{nome}.pdf"), format="A3", landscape=True, print_background=True,
               prefer_css_page_size=True)
        browser.close()
    import pymupdf
    pagine = len(pymupdf.open(QUI / f"{nome}.pdf"))
    if pagine != 1:
        raise SystemExit(f"STOP: il menù A3 occupa {pagine} pagine invece di una")
    print("creato", nome + ".pdf")


if __name__ == "__main__":
    main()
