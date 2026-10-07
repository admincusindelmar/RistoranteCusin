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

from genera_menu import (ANTIPASTI, CONTORNI, CRUDO_PEZZI, CRUDO_SALSE_EXTRA, CRUDO_SALSE_INCLUSE,
                         DEGUSTAZIONI, FINALE, PRIMI, QUI, SECONDI, SERVIZIO, t, prezzo)


def allergeni(a):
    return f'<span class="al">{" · ".join(map(str, a))}</span>' if a else ""


def voce(p):
    """Piatto della carta: nome, descrizione con allergeni, prezzo oltre il filetto."""
    seg = ""
    if p["chef"]:
        seg += '<span class="chef">il consiglio dello Chef</span>'
    if p["etichetta"]:
        seg += f'<span class="etichetta">{p["etichetta"][0]}</span>'
    cott = '<span class="cottura">18 minuti di cottura</span>' if p["cottura"] else ""
    desc = f'<p>{t(p["desc"])}{allergeni(p["allergeni"])}</p>' if p["desc"] else ""
    nota = ""
    if p["nota"]:
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
    portate = ""
    for nome_portata, _, piatti in d["portate"]:
        # nelle degustazioni basta la descrizione completa, che contiene già il nome del piatto
        voci = "".join(f'<li><p>{t(p["desc"] or p["nome"])}{allergeni(p["allergeni"])}</p></li>' for p in piatti)
        portate += f'<div class="portata"><h5>{nome_portata}</h5><ul>{voci}</ul></div>'
    return f"""<section class="deg">
  <p class="deg-tipo">Degustazione</p>
  <h3>{t(d['nome'])}</h3>
  <p class="deg-sotto">{t(d['sotto'])}</p>
  {portate}
  <div class="deg-prezzo"><span>{d['prezzo']}</span><em>a persona</em></div>
  <p class="deg-nota">Servito per l'intero tavolo</p>
</section>"""


def crudo():
    pezzi = "".join(riga(n, prezzo(pr), al, unita) for n, _, unita, _, pr, al in CRUDO_PEZZI)
    extra = "".join(riga("+ " + n, pr, al) for n, _, pr, al in CRUDO_SALSE_EXTRA)
    incluse = " e ".join(CRUDO_SALSE_INCLUSE)
    return f"""<p class="crudo-tit">Componi il tuo Crudo</p>
<p class="passo"><span>1</span> Scegli i tuoi pezzi</p>
<div class="elenco">{pezzi}</div>
<p class="passo"><span>2</span> Abbina le salse</p>
<p class="incluse">Incluse: {incluse.lower()}{allergeni((3,))}</p>
<div class="elenco">{extra}</div>
<p class="passo"><span>3</span> Brinda con le bollicine</p>
<div class="elenco">{riga("Calice di Franciacorta", "14")}{riga("Calice di Champagne", "23")}</div>"""


def documento():
    font = (QUI / "fonts.css").read_text()
    deg = "".join(degustazione(d) for d in DEGUSTAZIONI)
    nota_pasta = ('<p class="nota-pasta">Usiamo la pasta Benedetto Cavalieri – artigianale, trafilata al bronzo, '
                  'essiccata per 30 ore con il “Metodo delicato” dal 1918. Il lungo tempo di cottura è la misura '
                  'della sua qualità.</p>')
    qr = """<section class="qr">
  <div class="qr-box"><span>spazio per il<br>QR code</span></div>
  <div class="qr-testo">
    <p class="qr-it">Il menù nella tua lingua</p>
    <p>Menu in English · Deutsch · Français · Español</p>
    <p class="qr-em">Inquadra il codice con la fotocamera · Scan the code with your camera</p>
  </div>
</section>"""
    # tre colonne composte a mano per bilanciare le altezze (le colonne automatiche lasciavano buchi)
    col1 = sezione("Degustazioni", deg, "degustazioni")
    col2 = (sezione("Antipasti", f'<div class="elenco">{"".join(voce(p) for p in ANTIPASTI)}</div>') +
            sezione("Primi Piatti", f'<div class="elenco">{"".join(voce(p) for p in PRIMI)}</div>{nota_pasta}') +
            sezione("Servizio", f'<div class="elenco">{"".join(riga(a, c) for a, _, c in SERVIZIO)}</div>'))
    col3 = (sezione("Il Crudo", crudo()) +
            sezione("Secondi Piatti", f'<div class="elenco">{"".join(voce(p) for p in SECONDI)}</div>') +
            sezione("Contorni", f'<div class="elenco">{"".join(riga(c["nome"], prezzo(c["prezzo"])) for c in CONTORNI)}</div>') +
            qr)
    colonne = "".join(f'<div class="col">{c}</div>' for c in (col1, col2, col3))
    bozza = "" if FINALE else '<div class="bozza">BOZZA · in giallo i punti da definire</div>'
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Menu Ristorante Cusin A3</title>
<style>{font}{CSS}</style></head><body>{bozza}
<main class="foglio">
  <header class="testa"><h1>Ristorante Cusin</h1><div class="filo"></div><p>La Carta · Stagione 2026</p></header>
  <div class="colonne">{colonne}</div>
  <footer class="piede">I numeri accanto ai piatti indicano gli allergeni (Reg. UE 1169/2011): legenda e informazioni
  complete sono disponibili presso il nostro personale. Il pesce servito crudo è sottoposto ad abbattimento
  (Reg. CE 853/2004).</footer>
</main></body></html>"""


CSS = """
@page { size: A3; margin: 0; }
:root { --inchiostro:#191919; --tenue:#6d6d74; --filo:#afafb2; --filo-testa:#3d3d3b; --oro:#a88a4a; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: none; color: var(--inchiostro); font-family: 'Cormorant Garamond', Georgia, serif;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
mark { background: #fff1a8; color: #6b5200; padding: 0 2px; border-radius: 2px; font-style: normal; }
.bozza { position: fixed; top: 4mm; left: 6mm; font-size: 8pt; letter-spacing: .2em; color: #a08400; }
.foglio { width: 297mm; height: 420mm; padding: 14mm 14mm 11mm; position: relative; display: flex; flex-direction: column; }

.testa { text-align: center; margin-bottom: 5mm; }
.testa h1 { font-size: 30pt; font-weight: 700; letter-spacing: .32em; text-transform: uppercase; padding-left: .32em; }
.testa .filo { width: 80mm; height: .53mm; background: var(--filo-testa); margin: 2.5mm auto 2mm; }
.testa p { font-size: 15pt; font-weight: 300; letter-spacing: .14em; }

.colonne { flex: 1; min-height: 0; display: grid; grid-template-columns: repeat(3, 1fr); column-gap: 9mm; }
.col { min-height: 0; display: flex; flex-direction: column; justify-content: space-between; }
.col + .col { border-left: .3mm solid #d6d6da; margin-left: -4.5mm; padding-left: 4.5mm; }
.sez { break-inside: avoid-column; margin-bottom: 4.5mm; }
.sez.degustazioni { break-inside: auto; }
.sez h2 { font-size: 15pt; font-weight: 700; letter-spacing: .26em; text-transform: uppercase; }
.sez .riga { height: .4mm; background: var(--filo-testa); margin: 1.2mm 0 3mm; width: 100%; }

/* voci della carta: prezzo dopo un filetto verticale continuo, senza simbolo dell'euro */
.elenco { display: flex; flex-direction: column; }
.elenco.due { display: grid; grid-template-columns: 1fr 1fr; column-gap: 4mm; }
.elenco.due h4 { font-size: 11pt; }
.v { display: grid; grid-template-columns: 1fr 12mm; break-inside: avoid; }
.v .tx { padding: 0 3mm 1.8mm 0; }
.v .pr { border-left: .45mm solid var(--filo); padding-left: 2.6mm; font-size: 12pt; font-weight: 700; padding-top: .4mm; }
.v.corta .tx { padding-bottom: .5mm; }
.v h4 { font-size: 12pt; font-weight: 700; line-height: 1.2; }
.v h4 em { font-weight: 400; font-size: 11pt; color: var(--tenue); }
.v p { font-size: 10.5pt; line-height: 1.2; }
.v p.nota { font-style: italic; color: var(--oro); font-size: 10.5pt; }
.al { font-size: 8.5pt; letter-spacing: .04em; color: var(--tenue); margin-left: 1.6mm; white-space: nowrap; font-weight: 400; }
.al::before { content: "·"; margin-right: 1.2mm; }
.chef { display: block; font-family: 'Caveat', cursive; font-weight: 600; font-size: 13pt; color: var(--oro); line-height: 1; margin-bottom: .6mm; }
.etichetta { display: block; font-size: 8.5pt; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--oro); line-height: 1; margin-bottom: .8mm; }
.etichetta::before { content: "✦"; margin-right: 1.4mm; letter-spacing: 0; }
.cottura { font-family: 'Caveat', cursive; font-weight: 600; font-size: 12pt; color: var(--oro); margin-left: 2mm; white-space: nowrap; }
.v.firma .tx { border: .3mm solid #c9bb95; padding: 1.6mm 2.4mm; margin: 0 2.4mm 2.6mm -2.4mm; }
.tx.extra { font-size: 11pt; padding-bottom: .6mm; }
.extra-tit { display: block; font-size: 8.5pt; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--oro); margin-top: -1.4mm; }
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
.deg-prezzo { display: inline-flex; align-items: center; gap: 2.4mm; margin-top: 1mm; padding: 0 5mm;
  border-left: .45mm solid var(--filo); border-right: .45mm solid var(--filo); }
.deg-prezzo span { font-size: 19pt; font-weight: 600; }
.deg-prezzo em { font-size: 10pt; color: var(--tenue); }
.deg-nota { font-size: 10.5pt; font-weight: 600; margin-top: 1.2mm; }

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

.piede { margin-top: 4mm; padding-top: 2.4mm; border-top: .3mm solid #d6d6da; font-size: 9pt; color: var(--tenue);
  text-align: center; line-height: 1.3; }
"""


def main():
    nome = "Menu_RistoranteCusin_2026_A3" + ("" if FINALE else "_BOZZA")
    f_html = QUI / f"{nome}.html"
    f_html.write_text(documento(), encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = browser.new_page()
        pg.goto(f_html.resolve().as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        # controllo: tutto deve stare nelle tre colonne, senza una quarta colonna fuori dal foglio
        esito = pg.evaluate("""() => {
            const MM = 96 / 25.4, c = document.querySelector('.colonne').getBoundingClientRect();
            const cols = [...document.querySelectorAll('.col')].map(col => {
                const fine = Math.max(...[...col.children].map(e => e.getBoundingClientRect().bottom));
                const tot = [...col.children].reduce((a, e) => a + e.getBoundingClientRect().height, 0);
                return {altezza_mm: Math.round(tot / MM), libero_mm: Math.round((c.bottom - fine) / MM)};
            });
            return {colonne: cols, fuori: cols.filter(x => x.libero_mm < 0).length};
        }""")
        print("  controllo A3:", esito)
        if esito["fuori"]:
            raise SystemExit("STOP: il contenuto non sta nell'A3")
        pg.pdf(path=str(QUI / f"{nome}.pdf"), format="A3", print_background=True, prefer_css_page_size=True)
        import pymupdf
        pagine = len(pymupdf.open(QUI / f"{nome}.pdf"))
        if pagine != 1:
            raise SystemExit(f"STOP: il menù A3 occupa {pagine} pagine invece di una")
        print("creato", nome + ".pdf")
        browser.close()


if __name__ == "__main__":
    main()
