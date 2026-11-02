#!/usr/bin/env python3
"""
Prodotti toscani DOP, IGP e vini a denominazione, con l'uso in cucina di mare e di terra.
Stessa grafica del menù d'autunno.

    sorgenti/prodotti-toscani.html  →  pdf/Prodotti-toscani-DOP-IGP.pdf

Uso: python3 genera_prodotti_toscani.py
"""
import html

from playwright.sync_api import sync_playwright

from genera_cloud import CHROME, QUI, scarica

# (titolo sezione, nota, colonne, righe)
SEZIONI = [
    ("Oli extravergine di oliva", "Vanno su tutto, mare e terra.", ("Prodotto", "In cucina"), [
        ("Toscano IGP", "L'olio di base per tutta la carta; ha anche menzioni geografiche (per esempio Colline di Firenze, Montalbano)"),
        ("Chianti Classico DOP", "Deciso e piccante: carni, zuppe, bruschette"),
        ("Terre di Siena DOP", "Fruttato medio: crudi di pesce e verdure"),
        ("Lucca DOP", "Più delicato: il più adatto al pesce"),
        ("Seggiano DOP", "Da olivastra seggianese, sull'Amiata; morbido, ottimo sui crudi"),
    ]),
    ("Formaggi", "", ("Prodotto", "Mare", "Terra"), [
        ("Pecorino Toscano DOP", "Nei paccheri cacio e pepe con gamberi, già in carta", "Taglieri, primi, «baccelli e pecorino» del Primo Maggio"),
        ("Pecorino delle Balze Volterrane DOP", "Grattugiato su crudi di gambero", "Stagionato, con miele e confetture"),
        ("Pecorino Romano DOP", "Si produce anche in provincia di Grosseto", "Cacio e pepe, amatriciana, carbonara"),
    ]),
    ("Salumi e carni", "", ("Prodotto", "Mare", "Terra"), [
        ("Prosciutto Toscano DOP", "Avvolto su capesante o gamberi", "Antipasto toscano, già in carta"),
        ("Lardo di Colonnata IGP", "Con gamberi e scampi scottati, o su crostone con alici", "Crostoni, sull'arrosto"),
        ("Finocchiona IGP", "—", "Taglieri, con fichi"),
        ("Cinta Senese DOP", "—", "Arista, salumi, ragù"),
        ("Mortadella di Prato IGP", "—", "Antipasti, con fichi o pane"),
        ("Mortadella Bologna IGP", "Prodotta anche in Toscana", "Antipasti"),
        ("Salamini italiani alla cacciatora DOP", "Prodotti anche in Toscana", "Aperitivi"),
        ("Vitellone Bianco dell'Appennino Centrale IGP", "Chianina, Maremmana", "Tagliata e fiorentina: per la tagliata toscana"),
        ("Agnello del Centro Italia IGP", "—", "Agnello di Pasqua, costolette"),
    ]),
    ("Legumi, cereali, castagne e funghi", "", ("Prodotto", "Mare", "Terra"), [
        ("Farro della Garfagnana IGP", "Insalata di farro con polpo o cozze; zuppa di farro e frutti di mare", "Zuppe e minestre"),
        ("Fagiolo di Sorana IGP", "Fagioli e calamari; zuppa di fagioli e cozze", "Fagioli all'olio, ribollita"),
        ("Farina di Neccio della Garfagnana DOP", "Gnocchi di castagne con baccalà", "Necci, castagnaccio"),
        ("Farina di castagne della Lunigiana DOP", "Pasta fresca con crostacei", "Testaroli, dolci"),
        ("Castagna del Monte Amiata IGP", "Crema di castagne, già nella perla di mazzancolle", "Contorni, dolci"),
        ("Marrone del Mugello IGP", "Vellutata con capesante", "Marron glacé, ripieni"),
        ("Marrone di Caprese Michelangelo DOP", "Con scampi e burro nocciola", "Dolci"),
        ("Fungo di Borgotaro IGP", "Prodotto anche a Pontremoli; porcini con mazzancolle, già nei tagliolini", "Tagliatelle, contorni"),
    ]),
    ("Spezie, pane e miele", "", ("Prodotto", "Mare", "Terra"), [
        ("Zafferano di San Gimignano DOP", "Risotti di mare, brodetti, cacciucco bianco", "Risotti, ragù bianchi"),
        ("Pane Toscano DOP", "Crostoni del cacciucco, panzanella di mare", "Fettunta, ribollita, pappa al pomodoro"),
        ("Miele della Lunigiana DOP", "Castagno e acacia; glassature per il tonno", "Con i pecorini"),
    ]),
    ("Dolci", "", ("Prodotto", "Uso"), [
        ("Cantuccini Toscani IGP", "Con il vin santo, nella carta dei dolci"),
        ("Panforte di Siena IGP", "Natale"),
        ("Ricciarelli di Siena IGP", "Piccola pasticceria"),
    ]),
]

VINI = [
    ("Le 11 DOCG toscane", "Brunello di Montalcino · Vino Nobile di Montepulciano · Chianti · Chianti Classico · Carmignano · "
     "Vernaccia di San Gimignano · Morellino di Scansano · Montecucco Sangiovese · Elba Aleatico Passito · Suvereto · Val di Cornia Rosso"),
    ("Per il pesce: bianchi e rosati della costa", "Bolgheri DOC (Vermentino e rosato) · Elba DOC (Ansonica, Vermentino) · "
     "Ansonica Costa dell'Argentario DOC · Val di Cornia DOC · Terratico di Bibbona DOC · Montescudaio DOC · "
     "Maremma Toscana DOC (Vermentino) · Capalbio DOC · Parrina DOC · Candia dei Colli Apuani DOC · "
     "Colli di Luni DOC (Vermentino, area in comune con la Liguria) · Vernaccia di San Gimignano DOCG"),
    ("Per la carne", "Bolgheri Rosso e Bolgheri Sassicaia DOC · Brunello e Rosso di Montalcino · Nobile e Rosso di Montepulciano · "
     "Chianti Classico · Morellino di Scansano · Suvereto DOCG"),
    ("Dolci e fine pasto", "Elba Aleatico Passito DOCG · Vin Santo del Chianti DOC · Vin Santo del Chianti Classico DOC · Moscadello di Montalcino DOC"),
    ("IGT", "Toscana IGT e Costa Toscana IGT: molto usate dalle cantine della costa per i vini fuori disciplinare "
     "(per esempio i vini de La Fralluca della serata «L'uva nel piatto»)"),
]

IDEE = [
    ("Gamberi rossi crudi, lardo di Colonnata IGP e olio di Seggiano DOP", "Un abbinamento classico del Tirreno."),
    ("Zuppa di farro della Garfagnana IGP e fagioli di Sorana IGP con cozze e calamari", "Il mare e terra più toscano."),
    ("Risotto allo zafferano di San Gimignano DOP con scampi", "Un primo da serata a tema."),
]

FONTI = [
    ("Regione Toscana, oli DOP e IGP", "regione.toscana.it/-/selezione-oli-extravergine-di-oliva-dop-e-igp-della-toscana"),
    ("Regione Toscana, prodotti IGP", "prodtrad.regione.toscana.it/mod_qtp_igp"),
    ("Terra e Vita, Dop economy Toscana", "terraevita.edagricole.it"),
    ("GoNews, BuyFood Toscana 2026", "gonews.it/2026/10/29/buyfood-toscana-2026"),
]


def e(t):
    return html.escape(t)


def tabella(colonne, righe):
    cls = "t3" if len(colonne) == 3 else "t2"
    testa = "".join(f"<th>{e(c)}</th>" for c in colonne)
    corpo = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in righe)
    return f'<table class="{cls}"><thead><tr>{testa}</tr></thead><tbody>{corpo}</tbody></table>'


def documento():
    sez = ""
    for titolo, nota, colonne, righe in SEZIONI:
        n = f'<p class="nota">{e(nota)}</p>' if nota else ""
        intero = " intero" if len(righe) <= 5 else ""          # le sezioni corte non si spezzano fra due pagine
        sez += f'<section class="blocco{intero}"><h2>{e(titolo)}</h2>{n}{tabella(colonne, righe)}</section>'
    vini = "".join(f'<div class="vino"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in VINI)
    idee = "".join(f'<div class="idea"><p class="i-t">{e(t)}</p><p class="i-n">{e(n)}</p></div>' for t, n in IDEE)
    fonti = "".join(f"<li>{e(t)} · <i>{e(u)}</i></li>" for t, u in FONTI)
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><title>Cusin · Prodotti toscani DOP e IGP</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&display=swap">
<style>{CSS}</style></head><body>
<section class="copertina">
  <img class="mono" src="cusin-monogramma-blu.png" alt="Cusin">
  <p class="eti">Per la cucina di Cusin</p>
  <h1>I prodotti toscani<br>a denominazione</h1>
  <p class="sotto">DOP, IGP e vini, per il mare e per la terra</p>
  <div class="filetto"></div>
  <div class="numeri">
    <div><b>32</b><span>prodotti alimentari<br>16 DOP · 16 IGP</span></div>
    <div><b>58</b><span>denominazioni<br>del vino</span></div>
    <div><b>2</b><span>distillati<br>IG</span></div>
  </div>
  <p class="intro">Dati Ismea presentati a BuyFood Toscana 2026. Qui sono raccolti i 31 prodotti alimentari verificati, con l'uso
  in una cucina di mare e di terra; per l'elenco ufficiale completo fa fede la banca dati del Ministero dell'Agricoltura (MASAF).</p>
  <p class="avviso"><b>Il pesce.</b> In Toscana non ci sono pesci o frutti di mare DOP o IGP: per il mare le denominazioni entrano
  come condimento e accompagnamento. Fuori dalle denominazioni c'è la bottarga di Orbetello, Presidio Slow Food.</p>
</section>
{sez}
<section class="blocco"><h2>Vini a denominazione</h2>{vini}</section>
<section class="blocco"><h2>Tre idee per la carta</h2>{idee}</section>
<section class="blocco fonti"><h2>Fonti</h2><ul>{fonti}</ul></section>
</body></html>"""


CSS = """
:root { --blu:#152b61; --champagne:#d6c6a5; --avorio:#f4ede2; --secondario:#675e53; --filetto:rgba(21,43,97,.22); }
@page { size: A4; margin: 16mm 18mm 18mm; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Cormorant Garamond", Garamond, serif; font-weight: 500; font-variant-numeric: lining-nums; color: var(--blu);
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.eti { font-size: 12.5px; font-weight: 600; letter-spacing: .28em; text-transform: uppercase; }
.copertina { height: 260mm; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; break-after: page; }
.copertina .mono { height: 30mm; margin-bottom: 10mm; }
.copertina h1 { font-weight: 500; font-size: 46px; line-height: 1.08; margin-top: 4mm; }
.copertina .sotto { font-style: italic; font-size: 20px; margin-top: 4mm; }
.filetto { width: 60px; height: 1px; background: var(--champagne); margin: 9mm auto; }
.numeri { display: flex; gap: 14mm; }
.numeri div { display: flex; flex-direction: column; align-items: center; }
.numeri b { font-size: 44px; font-weight: 500; line-height: 1; }
.numeri span { font-size: 11px; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; margin-top: 2mm; line-height: 1.4; }
.intro { font-size: 15.5px; line-height: 1.45; max-width: 140mm; margin-top: 10mm; }
.avviso { font-size: 15.5px; line-height: 1.45; max-width: 140mm; margin-top: 5mm; background: #ebe2d3; padding: 3mm 4mm; text-align: left; }
.blocco { margin-bottom: 9mm; }
.blocco.intero { break-inside: avoid; }
h2 { font-weight: 500; font-size: 26px; display: flex; align-items: baseline; gap: 4mm; margin-bottom: 2.5mm; break-after: avoid; }
h2::after { content: ""; flex: 1; height: 1px; background: var(--champagne); align-self: center; }
.nota { font-style: italic; font-size: 15px; color: var(--secondario); margin-bottom: 2mm; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: 10.5px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; padding: 1.5mm 2mm 1.5mm 0; border-bottom: 1px solid var(--champagne); }
td { font-size: 14.5px; line-height: 1.3; padding: 1.8mm 3mm 1.8mm 0; border-bottom: 1px solid var(--filetto); vertical-align: top; }
td:first-child { font-weight: 600; font-size: 15.5px; }
tr { break-inside: avoid; }
.t3 td:first-child { width: 33%; } .t3 td:nth-child(2) { width: 36%; }
.t2 td:first-child { width: 36%; }
.vino { margin-bottom: 4mm; break-inside: avoid; }
.vino h3 { font-size: 11.5px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; margin-bottom: 1mm; }
.vino p { font-size: 15px; line-height: 1.45; }
.idea { border-left: 1px solid var(--champagne); padding-left: 4mm; margin-bottom: 4mm; break-inside: avoid; }
.i-t { font-size: 17px; font-weight: 600; }
.i-n { font-size: 15px; font-style: italic; color: var(--secondario); }
.fonti ul { list-style: none; font-size: 13.5px; line-height: 1.6; color: var(--secondario); }
"""

PIEDE = """<div style="width:100%;font-family:Georgia,serif;font-size:7px;letter-spacing:2px;text-transform:uppercase;color:#675e53;
padding:0 18mm;display:flex;justify-content:space-between;-webkit-print-color-adjust:exact;">
<span>Cusin · Prodotti toscani DOP e IGP</span><span><span class="pageNumber"></span></span></div>"""


def main():
    f = QUI / "sorgenti" / "prodotti-toscani.html"
    f.write_text(documento(), encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.route("https://fonts.googleapis.com/**", scarica)
        pg.route("https://fonts.gstatic.com/**", scarica)
        pg.goto(f.as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=str(QUI / "pdf" / "Prodotti-toscani-DOP-IGP.pdf"), print_background=True, prefer_css_page_size=True,
               display_header_footer=True, header_template="<div></div>", footer_template=PIEDE)
        b.close()
    print("creato pdf/Prodotti-toscani-DOP-IGP.pdf")


if __name__ == "__main__":
    main()
