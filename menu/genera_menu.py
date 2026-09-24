#!/usr/bin/env python3
"""
Genera il menù food di Cusin del Mar nello stile della Carta Vini 2026.

Uso:
    python3 genera_menu.py            -> bozza (evidenzia in giallo ciò che è ancora da definire)
    python3 genera_menu.py --finale   -> versione pulita da stampa

Per modificare piatti, prezzi o allergeni basta cambiare i dati qui sotto.
Il testo tra [[doppie quadre]] è un punto ancora da decidere in cucina.
"""
import html
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

QUI = Path(__file__).parent
FINALE = "--finale" in sys.argv

# ---------------------------------------------------------------------------
# ALLERGENI (Reg. UE 1169/2011, Allegato II)
# ---------------------------------------------------------------------------
ALLERGENI = {
    1: ("Glutine", "Gluten"),
    2: ("Crostacei", "Crustaceans"),
    3: ("Uova", "Eggs"),
    4: ("Pesce", "Fish"),
    5: ("Arachidi", "Peanuts"),
    6: ("Soia", "Soy"),
    7: ("Latte e lattosio", "Milk"),
    8: ("Frutta a guscio", "Tree nuts"),
    9: ("Sedano", "Celery"),
    10: ("Senape", "Mustard"),
    11: ("Sesamo", "Sesame"),
    12: ("Solfiti", "Sulphites"),
    13: ("Lupini", "Lupin"),
    14: ("Molluschi", "Molluscs"),
}


def piatto(nome, desc, en, allergeni=(), prezzo=None, chef=False, nota=None):
    return dict(nome=nome, desc=desc, en=en, allergeni=allergeni,
                prezzo=prezzo, chef=chef, nota=nota)


# ---------------------------------------------------------------------------
# DEGUSTAZIONI
# ---------------------------------------------------------------------------
DEGUSTAZIONI = [
    dict(
        id="stella",
        nome="Stella di Mare",
        sotto="Il nostro viaggio nel mare, in sette tempi",
        sotto_en="Our journey through the sea, in seven moments",
        prezzo=65,
        portate=[
            ("Antipasti", "Starters", [
                piatto("Scampo e pera",
                       "Scampo con brunoise di pera, sedano croccante e colatura di fico",
                       "Langoustine, pear brunoise, crunchy celery and fig glaze", (2, 9)),
                piatto("Sfera di gambero",
                       "Sfera di gambero ripiena di crema di patata al timo limonato",
                       "Prawn sphere filled with lemon-thyme potato cream", (2,)),
                piatto("Seppia al nero",
                       "Seppia su crema di cipolla dorata dolce e colatura di nero",
                       "Cuttlefish on sweet golden onion cream with squid-ink drizzle", (14,)),
            ]),
            ("Primi", "First courses", [
                piatto("Paccheri ripieni",
                       "Paccheri ripieni di ricotta senza lattosio, mazzancolle e colatura di cachi",
                       "Paccheri filled with lactose-free ricotta, king prawns and persimmon glaze",
                       (1, 2, 7)),
                piatto("Gnocco di riso al tartufo",
                       "Gnocco di riso con calamari e totani al tartufo",
                       "Rice gnocco with squid, flying squid and truffle", (14,)),
            ]),
            ("Secondo", "Main course", [
                piatto("Dentice e carciofo",
                       "Trancio di dentice, carpaccio di carciofo sfumato al vino bianco e olio al caffè",
                       "Dentex fillet, artichoke carpaccio with white wine and coffee oil", (4, 12)),
            ]),
            ("Pre-dessert", "Pre-dessert", [
                piatto("Cucchiaio di marmellata di vino", "",
                       "A spoonful of wine jam", (12,)),
            ]),
        ],
    ),
    dict(
        id="vegetariana",
        nome="Vegetariana di Mare",
        sotto="Il profumo del mare, senza pesce",
        sotto_en="The scent of the sea, without fish",
        prezzo=48,
        portate=[
            ("Antipasti", "Starters", [
                piatto("Cialda di ceci",
                       "Cialda di ceci, lattuga di mare, oliva taggiasca e scorza di limone",
                       "Chickpea wafer, sea lettuce, Taggiasca olive and lemon zest", ()),
                piatto("Sfera di verza",
                       "Sfera di cavolo verza ripiena di robiola e pera, senape e olio al finocchio di mare",
                       "Savoy cabbage sphere filled with robiola and pear, mustard and sea fennel oil",
                       (7, 10)),
            ]),
            ("Primo", "First course", [
                piatto("Raviolo di zucca",
                       "Raviolo di zucca e burro chiarificato alla salicornia",
                       "Pumpkin raviolo, clarified butter with samphire", (1, 3, 7)),
            ]),
            ("Secondo", "Main course", [
                piatto("Cacciucco vegetale",
                       "Brodo di alga kombu e funghi, pomodoro e cialda di pane croccante, "
                       "con cipollotto, [[sedano rapa o melone invernale]] e cavolo nero",
                       "Kombu seaweed and mushroom broth, tomato and crispy bread wafer, "
                       "with spring onion, [[celeriac or winter melon]] and black cabbage",
                       (1, 9)),
            ]),
        ],
    ),
    dict(
        id="primofiore",
        nome="Primo Fiore",
        sotto="Il primo assaggio della nostra cucina",
        sotto_en="A first taste of our kitchen",
        prezzo=45,
        portate=[
            ("Antipasti", "Starters", [
                piatto("Nuvole di baccalà",
                       "Nuvole di baccalà su crema di [[da definire]] e croccante di prosciutto senese",
                       "Salt cod clouds on [[to be defined]] cream, crispy Sienese prosciutto", (4,)),
                piatto("Calamaro e tarassaco",
                       "Calamaro grigliato su erbette di tarassaco in salsa di acciughe",
                       "Grilled squid on dandelion greens with anchovy sauce", (4, 14)),
            ]),
            ("Primo", "First course", [
                piatto("Tagliolini pepe e limone",
                       "Tagliolini artigianali pepe e limone, mazzancolle e funghi porcini",
                       "Handmade pepper and lemon tagliolini, king prawns and porcini mushrooms",
                       (1, 2, 3)),
            ]),
            ("Secondo", "Main course", [
                piatto("Spigola in crosta",
                       "Spigola con carapace di patata americana e pomodorini confit",
                       "Sea bass in a sweet-potato crust with confit cherry tomatoes", (4,)),
            ]),
        ],
    ),
]

ULTIMO = dict(
    id="ultimo",
    nome="Ultimo dell'Anno",
    sotto="Cenone di San Silvestro · 31 dicembre 2026",
    sotto_en="New Year's Eve Dinner · 31st December 2026",
    prezzo=100,
    portate=[
        ("Antipasti", "Starters", [
            piatto("Scampo e mandarino",
                   "Scampo, crema di mandorle salate, julienne croccante di sedano rapa e gel al mandarino",
                   "Langoustine, salted almond cream, crunchy celeriac julienne and mandarin gel",
                   (2, 8, 9)),
            piatto("Gambero rosso e carciofo",
                   "Gambero rosso, bisque di crostacei e carciofo",
                   "Red prawn, shellfish bisque and artichoke", (2,)),
            piatto("Polpette di cicala",
                   "Polpette di cicala di mare",
                   "Mantis shrimp croquettes", (2,)),
        ]),
        ("Primi", "First courses", [
            piatto("Risotto allo Champagne",
                   "Risotto al gambero rosso, Champagne, finocchi e scorza di limone",
                   "Red prawn risotto, Champagne, fennel and lemon zest", (2, 12)),
            piatto("Linguine ai batti batti",
                   "Linguine con batti batti",
                   "Linguine with slipper lobster", (1, 2)),
        ]),
        ("Secondo", "Main course", [
            piatto("Catalana", "Catalana di crostacei [[composizione da definire]]",
                   "Catalan-style shellfish [[to be defined]]", (2,)),
        ]),
        ("Dolce", "Dessert", [
            piatto("[[Dolce da definire]]", "", "", ()),
        ]),
    ],
)

# ---------------------------------------------------------------------------
# ALLA CARTA  (prezzo=None -> ancora da inserire)
# ---------------------------------------------------------------------------
ANTIPASTI = [
    piatto("Mare caldo",
           "Mare caldo con cristalli di pomodoro, crema alle ostriche, citronette di limone e olio EVO",
           "Warm seafood with tomato crystals, oyster cream, lemon citronette and extra virgin olive oil",
           (2, 4, 14)),
    piatto("Cappuccino di mazzancolle",
           "Mazzancolle con crema di ceci e semi di lino e spuma di mascarpone",
           "King prawns with chickpea and flaxseed cream, mascarpone foam",
           (2, 7), chef=True),
    piatto("Sfera di verza",
           "Sfera di cavolo verza ripiena di robiola e pera, senape e olio al finocchio di mare",
           "Savoy cabbage sphere filled with robiola and pear, mustard and sea fennel oil",
           (7, 10), nota="Vegetariano · Vegetarian"),
    piatto("Calamaro e tarassaco",
           "Calamaro grigliato su erbette di tarassaco in salsa di acciughe",
           "Grilled squid on dandelion greens with anchovy sauce", (4, 14)),
]

CRUDO = dict(
    nome="Componi il tuo Crudo",
    en="Build your own raw platter",
    desc="Scegli il pescato crudo del giorno e abbinalo alle nostre salse",
    desc_en="Choose from today's raw catch and pair it with our house sauces",
    salse=["[[Salsa 1]]", "[[Salsa 2]]", "[[Salsa 3]]", "[[Salsa 4]]", "[[Salsa 5]]"],
    allergeni=(2, 4, 14),
    prezzo=None,
)

PRIMI = [
    piatto("Paccheri cacio e pepe e gambero rosso",
           "Paccheri cacio e pepe con gambero rosso e la sua bisque",
           "Paccheri cacio e pepe with red prawn and its bisque",
           (1, 2, 7), chef=True,
           nota="Provalo con una spolverata di pepe del Madagascar · Try it with a dusting of Madagascar pepper"),
    piatto("Spaghetto alle vongole",
           "Spaghetto alle vongole veraci, fiocchi di pomodoro e olio al lime",
           "Spaghetti with clams, tomato flakes and lime oil", (1, 14)),
    piatto("Tagliolini pepe e limone",
           "Tagliolini artigianali pepe e limone, mazzancolle e funghi porcini",
           "Handmade pepper and lemon tagliolini, king prawns and porcini mushrooms", (1, 2, 3)),
    piatto("Risotto calamari e totani",
           "Risotto con calamari e totani al tartufo",
           "Risotto with squid, flying squid and truffle", (14,)),
    piatto("Risotto al dentice",
           "Risotto al dentice [[con cosa?]]",
           "Dentex risotto [[with...?]]", (4,)),
    piatto("Ravioli di zucca",
           "Ravioli di zucca e burro chiarificato alla salicornia",
           "Pumpkin ravioli, clarified butter with samphire", (1, 3, 7),
           nota="Vegetariano · Vegetarian"),
]

SECONDI = [
    piatto("Grigliata di mare",
           "Mazzancolle, gambero rosso, scampi, tonno e spiedino [[di cosa?]], "
           "servita con [[salse da definire]]",
           "King prawns, red prawn, langoustines, tuna and [[skewer]], served with [[sauces]]",
           (2, 4, 14)),
    piatto("Scaloppata di tonno al sesamo",
           "Tonno in crosta di sesamo bianco e nero, verdure scottate e baffo di carota",
           "Tuna in black and white sesame crust, seared vegetables and carrot ribbon",
           (4, 11)),
    piatto("Il fritto mare della zia",
           "Frittura di mare e verdure in farina di riso, leggera e croccante",
           "Light, crispy fried seafood and vegetables in rice flour",
           (2, 4, 14), chef=True),
    piatto("Spigola alla griglia",
           "Spigola alla griglia con verdure spicchiate",
           "Grilled sea bass with roasted vegetable wedges", (4,)),
    piatto("Tagliata toscana",
           "Tagliata di manzo con patate arrosto",
           "Sliced Tuscan beef steak with roast potatoes", ()),
]

CONTORNI = [
    piatto("Verdure al forno spicchiate", "", "Roasted vegetable wedges", ()),
    piatto("Patate arrosto", "", "Roast potatoes", ()),
    piatto("Patate fritte", "", "French fries", ()),
    piatto("Insalata verde", "", "Green salad", ()),
    piatto("Insalata mista", "", "Mixed salad", ()),
]

# ---------------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------------


def t(s):
    """Escape + evidenzia i [[punti da definire]] (solo in bozza)."""
    s = html.escape(s)
    if FINALE:
        return re.sub(r"\[\[(.*?)\]\]", r"\1", s)
    return re.sub(r"\[\[(.*?)\]\]", r'<mark>\1</mark>', s)


def prezzo(p):
    if p is not None:
        return str(p)
    return "" if FINALE else "<mark>—</mark>"


def allerg(a):
    if not a:
        return ""
    return f'<span class="all">Allergeni · Allergens&nbsp; {" · ".join(str(x) for x in a)}</span>'


# Illustrazioni a tratto, nello spirito dei disegni della carta vini
PESCE = """<svg viewBox="0 0 120 50" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
<path d="M8 25c14-16 44-22 70-10 8 4 14 8 18 10-4 2-10 6-18 10-26 12-56 6-70-10z"/>
<path d="M96 25l18-13c-3 8-3 18 0 26z"/><circle cx="24" cy="21" r="2.2"/>
<path d="M36 13c4 7 4 17 0 24M52 11c5 8 5 20 0 28M68 13c4 7 4 17 0 24" opacity=".6"/>
<path d="M44 12c6-6 16-8 24-4M46 38c6 5 14 6 20 3" opacity=".6"/></g></svg>"""

CONCHIGLIA = """<svg viewBox="0 0 70 60" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
<path d="M35 52C14 50 4 34 8 20 14 8 26 4 35 4s21 4 27 16c4 14-6 30-27 32z"/>
<path d="M35 52V6M35 52L16 10M35 52L54 10M35 52L9 24M35 52L61 24"/>
<path d="M27 52h16l-3 5H30z"/></g></svg>"""

FORCHETTA = """<svg viewBox="0 0 60 60" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round">
<path d="M18 6v16c0 5 3 8 6 8s6-3 6-8V6M24 6v14M24 30v24"/>
<path d="M42 6c-5 4-7 12-7 20 0 3 3 5 7 5v23"/></g></svg>"""

SPIGA = """<svg viewBox="0 0 60 60" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
<path d="M30 56V14"/><path d="M30 18c-6-2-9-8-8-14 6 2 9 8 8 14zM30 18c6-2 9-8 8-14-6 2-9 8-8 14z"/>
<path d="M30 30c-7-2-11-8-10-14 7 2 11 8 10 14zM30 30c7-2 11-8 10-14-7 2-11 8-10 14z"/>
<path d="M30 42c-7-2-11-8-10-14 7 2 11 8 10 14zM30 42c7-2 11-8 10-14-7 2-11 8-10 14z"/></g></svg>"""

FOGLIA = """<svg viewBox="0 0 60 60" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
<path d="M10 50C8 26 24 8 52 8c0 28-18 44-42 42z"/><path d="M10 50L40 20M22 38h12M30 30V18"/></g></svg>"""


def testata(titolo, sotto, icona=""):
    return f"""<header class="testata">
  <div><h1>{t(titolo)}</h1><p class="sottotitolo">{t(sotto)}</p></div>
  <div class="icona">{icona}</div>
</header>"""


def riga_piatto(p):
    chef = ('<span class="chef">il consiglio dello Chef</span>' if p["chef"] else "")
    desc = f'<p class="desc">{t(p["desc"])}</p>' if p["desc"] else ""
    en = f'<p class="en">{t(p["en"])}</p>' if p["en"] else ""
    nota = f'<p class="nota">{t(p["nota"])}</p>' if p["nota"] else ""
    return f"""<div class="voce{' firma' if p['chef'] else ''}">
  <div class="testo"><h3>{t(p['nome'])}{chef}</h3>{desc}{en}{nota}{allerg(p['allergeni'])}</div>
  <div class="filetto"></div><div class="prezzo">{prezzo(p['prezzo'])}</div>
</div>"""


def pagina(corpo, n=None, classe=""):
    num = f'<footer class="num">{n}</footer>' if n else ""
    return f'<section class="pagina {classe}">{corpo}{num}</section>'


def pagina_degustazione(d, n):
    blocchi = []
    for it, en, piatti in d["portate"]:
        voci = "".join(
            f"""<li><h3>{t(p['nome'])}</h3>
            {f'<p class="desc">{t(p["desc"])}</p>' if p['desc'] else ''}
            {f'<p class="en">{t(p["en"])}</p>' if p['en'] else ''}{allerg(p['allergeni'])}</li>"""
            for p in piatti)
        blocchi.append(f'<div class="portata"><h2>{it} <span>{en}</span></h2><ul>{voci}</ul></div>')
    corpo = f"""
{testata('Degustazione', 'Tasting Menu', CONCHIGLIA)}
<div class="deg">
  <h1 class="deg-nome">{t(d['nome'])}</h1>
  <p class="deg-sotto">{t(d['sotto'])}<br><em>{t(d['sotto_en'])}</em></p>
  {''.join(blocchi)}
  <div class="deg-prezzo"><span class="cifra">{d['prezzo']}</span>
    <span class="pp">a persona<br><em>per person</em></span></div>
  <p class="abbina">Chiedi al nostro personale l'abbinamento al calice dalla Carta dei Vini<br>
  <em>Ask our staff for a wine-by-the-glass pairing from our Wine List</em></p>
</div>"""
    return pagina(corpo, n, "p-deg")


def pagina_indice():
    voci = [
        ("Degustazioni", "Tasting Menus", "2 - 4"),
        ("Antipasti", "Starters", "5"),
        ("Primi Piatti", "First Courses", "6"),
        ("Secondi Piatti", "Main Courses", "7"),
        ("Contorni", "Side Dishes", "8"),
        ("Allergeni", "Allergens", "8"),
    ]
    righe = "".join(f'<div class="r"><span>{a}<em>{b}</em></span><span class="pg">{c}</span></div>'
                    for a, b, c in voci)
    corpo = f"""
<div class="biglietto">
  <p>Scampo</p><p>Gambero rosso</p><p>Dentice</p><p>Vongole veraci</p><p>Calamaro</p>
</div>
<div class="indice">
  <h1>INDICE</h1>
  <div class="lista">{righe}</div>
</div>
<p class="firma-rist">Cusin del Mar · La Cucina 2026</p>"""
    return pagina(corpo, None, "p-indice")


def pagina_carta(titolo, sotto, icona, intro, voci, n, extra=""):
    corpo = f"""{testata(titolo, sotto, icona)}
<p class="intro">{intro}</p>
<div class="elenco">{''.join(riga_piatto(v) for v in voci)}</div>{extra}"""
    return pagina(corpo, n)


def box_crudo():
    c = CRUDO
    salse = "".join(f"<li>{t(s)}</li>" for s in c["salse"])
    return f"""<div class="voce crudo">
  <div class="testo">
    <h3>{t(c['nome'])}<span class="chef">da condividere</span></h3>
    <p class="desc">{t(c['desc'])}</p><p class="en">{t(c['en'])} — {t(c['desc_en'])}</p>
    <p class="salse-tit">Le nostre cinque salse · <em>Our five sauces</em></p>
    <ul class="salse">{salse}</ul>
    {allerg(c['allergeni'])}
  </div>
  <div class="filetto"></div><div class="prezzo">{prezzo(c['prezzo'])}</div>
</div>"""


def pagina_contorni_allergeni(n):
    contorni = "".join(riga_piatto(v) for v in CONTORNI)
    leg = "".join(f"<li><b>{k}</b> {a} <em>{b}</em></li>" for k, (a, b) in ALLERGENI.items())
    corpo = f"""{testata('Contorni', 'Side Dishes', FOGLIA)}
<div class="elenco compatto">{contorni}</div>
<div class="allergeni">
  <h2>Allergeni <span>Allergens</span></h2>
  <ul class="legenda">{leg}</ul>
  <p>Il numero accanto a ogni piatto indica le sostanze che possono causare allergie o intolleranze
  (Reg. UE 1169/2011). Per qualsiasi esigenza alimentare rivolgetevi al nostro personale:
  la documentazione completa è disponibile su richiesta.</p>
  <p class="en">The numbers next to each dish refer to the allergens listed above (EU Reg. 1169/2011).
  Please inform our staff of any food allergy or intolerance; full documentation is available on request.</p>
  <p>Il pesce destinato al consumo crudo o praticamente crudo è sottoposto a trattamento di bonifica
  preventiva mediante abbattimento, come previsto dal Reg. CE 853/2004.</p>
  <p class="en">Fish served raw or nearly raw has been blast-frozen in accordance with EC Reg. 853/2004.</p>
</div>"""
    return pagina(corpo, n)


CSS = """
@page { size: A4; margin: 0; }
:root { --carta:#e9e9ee; --inchiostro:#3b3b40; --tenue:#77777f; --filo:#8a8a92; --oro:#b59a5b; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: var(--carta); color: var(--inchiostro);
  font-family: 'Cormorant Garamond', Georgia, serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
mark { background: #fff1a8; color: #6b5200; padding: 0 3px; border-radius: 2px; font-style: normal; }
.pagina { width: 210mm; height: 297mm; padding: 16mm 20mm 14mm; position: relative; overflow: hidden;
  page-break-after: always; background: var(--carta); }
.num { position: absolute; bottom: 9mm; left: 0; right: 0; text-align: center; font-size: 10pt; color: var(--tenue); }
.ill { width: 100%; height: 100%; color: #9a9aa3; }

/* testata come nella carta vini: MAIUSCOLO spaziato + sottotitolo + filetto */
.testata { display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 1px solid var(--filo); padding-bottom: 3mm; margin-bottom: 7mm; width: 78%; }
.testata h1 { font-size: 20pt; font-weight: 600; letter-spacing: .32em; text-transform: uppercase; }
.testata .sottotitolo { font-size: 11pt; letter-spacing: .18em; color: var(--tenue); margin-top: 1mm; }
.testata .icona { width: 26mm; height: 14mm; margin-bottom: -1mm; transform: translateX(34mm); }
.intro { font-size: 11.5pt; font-style: italic; color: var(--tenue); margin: -2mm 0 7mm; max-width: 150mm; }

/* voci con filetto verticale e prezzo a destra, senza simbolo € */
.elenco { display: flex; flex-direction: column; gap: 4.6mm; }
.voce { display: grid; grid-template-columns: 1fr 1px 14mm; column-gap: 5mm; }
.voce .filetto { background: var(--filo); }
.voce .prezzo { font-size: 13pt; font-weight: 500; align-self: center; text-align: right; }
.voce h3 { font-size: 13.5pt; font-weight: 700; line-height: 1.2; }
.voce .desc { font-size: 11.5pt; line-height: 1.3; }
.voce .en { font-size: 10.5pt; font-style: italic; color: var(--tenue); line-height: 1.3; }
.voce .nota { font-size: 10.5pt; font-style: italic; color: var(--oro); margin-top: .6mm; }
.all { display: block; font-size: 8.5pt; letter-spacing: .06em; color: var(--tenue); margin-top: .8mm; }
.chef { font-family: 'Caveat', cursive; font-weight: 600; font-size: 13pt; color: var(--oro);
  margin-left: 3mm; letter-spacing: 0; white-space: nowrap; }
.voce.firma .testo, .voce.crudo .testo { border: 1px solid #c9bb95; padding: 3mm 4mm; background: #efeee9; }
.salse-tit { font-size: 10.5pt; margin-top: 1.8mm; letter-spacing: .04em; }
.salse { list-style: none; display: flex; flex-wrap: wrap; gap: 1mm 4mm; font-size: 11pt; margin-top: .5mm; }
.salse li::before { content: "· "; color: var(--oro); }
.compatto { gap: 3mm; }

/* indice */
.p-indice .biglietto { position: absolute; top: 10mm; right: 14mm; width: 70mm; padding: 6mm 8mm 8mm;
  border: 1.2px solid #9a9aa3; border-radius: 1mm 3mm 2mm 4mm; transform: rotate(-14deg);
  font-family: 'Caveat', cursive; font-size: 21pt; line-height: 1.12; color: #85858d; }
.p-indice .biglietto::after { content:""; position:absolute; inset: 3mm -3mm -3mm 3mm; border: 1px solid #b5b5bc;
  border-radius: 3mm 1mm 4mm 2mm; z-index: -1; }
.indice { position: absolute; top: 118mm; left: 0; right: 0; }
.indice h1 { font-weight: 400; font-size: 44pt; letter-spacing: .02em; text-align: center; width: 120mm; margin-left: 16mm; }
.indice .lista { margin: 6mm auto 0; width: 150mm; position: relative; }
.indice .lista::before { content:""; position:absolute; left: 110mm; top: -30mm; bottom: -4mm; width: 1px; background: var(--filo); }
.indice .r { display: grid; grid-template-columns: 110mm 40mm; padding: 3mm 0; font-size: 12pt;
  letter-spacing: .12em; text-transform: uppercase; }
.indice .r span:first-child { text-align: center; }
.indice .r em { display: block; font-size: 9.5pt; text-transform: none; letter-spacing: .08em; color: var(--tenue); }
.indice .pg { text-align: center; align-self: center; }
.firma-rist { position: absolute; bottom: 14mm; left: 0; right: 0; text-align: center; font-size: 11pt;
  letter-spacing: .35em; text-transform: uppercase; color: var(--tenue); }

/* degustazioni */
.p-deg { display: flex; flex-direction: column; }
.deg { text-align: center; flex: 1; display: flex; flex-direction: column; justify-content: center; padding-bottom: 8mm; }
.deg > * { flex: none; }
.deg-prezzo { align-self: center; }
.deg-nome { font-size: 34pt; font-weight: 400; letter-spacing: .06em; line-height: 1.05; }
.deg-sotto { font-size: 12pt; color: var(--tenue); margin: 2mm 0 5mm; }
.portata { margin: 0 auto 3.6mm; max-width: 150mm; }
.portata h2 { font-size: 10.5pt; font-weight: 600; letter-spacing: .3em; text-transform: uppercase; color: var(--oro);
  margin-bottom: 1.6mm; }
.portata h2 span { font-weight: 400; font-style: italic; letter-spacing: .08em; text-transform: none; color: var(--tenue); }
.portata ul { list-style: none; }
.portata li { margin-bottom: 2.2mm; }
.portata li h3 { font-size: 13pt; font-weight: 700; }
.portata .desc { font-size: 11.5pt; line-height: 1.25; }
.portata .en { font-size: 10.3pt; font-style: italic; color: var(--tenue); line-height: 1.25; }
.portata .all { margin-top: .3mm; }
.deg-prezzo { display: inline-flex; align-items: center; gap: 4mm; margin-top: 2mm; padding: 1mm 7mm;
  border-left: 1px solid var(--filo); border-right: 1px solid var(--filo); }
.deg-prezzo .cifra { font-size: 30pt; font-weight: 500; }
.deg-prezzo .pp { font-size: 10pt; text-align: left; line-height: 1.2; color: var(--tenue); }
.abbina { font-size: 10.5pt; color: var(--tenue); margin-top: 3mm; }

/* allergeni */
.allergeni { margin-top: 10mm; border-top: 1px solid var(--filo); padding-top: 5mm; }
.allergeni h2 { font-size: 13pt; font-weight: 600; letter-spacing: .3em; text-transform: uppercase; margin-bottom: 3mm; }
.allergeni h2 span { font-weight: 400; font-style: italic; letter-spacing: .08em; text-transform: none; color: var(--tenue); }
.legenda { list-style: none; columns: 2; column-gap: 10mm; font-size: 11pt; margin-bottom: 4mm; }
.legenda li { padding: .6mm 0; }
.legenda b { display: inline-block; width: 7mm; }
.legenda em { color: var(--tenue); }
.allergeni p { font-size: 9.8pt; line-height: 1.3; margin-bottom: 1.2mm; }
.allergeni p.en { font-style: italic; color: var(--tenue); margin-bottom: 2.6mm; }
.bozza { position: fixed; top: 5mm; left: 6mm; font-size: 8pt; letter-spacing: .2em; color: #a08400; }
"""


def documento(pagine, titolo):
    font = (QUI / "fonts.css").read_text()
    bozza = "" if FINALE else '<div class="bozza">BOZZA · in giallo i punti da definire</div>'
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>{titolo}</title>
<style>{font}{CSS}</style></head><body>{bozza}{''.join(pagine)}</body></html>"""


def main():
    carta = [
        pagina_indice(),
        *[pagina_degustazione(d, i + 2) for i, d in enumerate(DEGUSTAZIONI)],
        pagina_carta("Antipasti", "Starters", PESCE,
                     "Per iniziare, il mare in piccoli assaggi · <em>To begin, the sea in small bites</em>",
                     ANTIPASTI, 5, extra='<div class="elenco" style="margin-top:4.6mm">' + box_crudo() + "</div>"),
        pagina_carta("Primi Piatti", "First Courses", SPIGA,
                     "Pasta artigianale e risotti mantecati al momento · <em>Handmade pasta and freshly made risotti</em>",
                     PRIMI, 6),
        pagina_carta("Secondi Piatti", "Main Courses", PESCE,
                     "Il pescato alla griglia, in crosta e fritto leggero · <em>Grilled, crusted and lightly fried catch</em>",
                     SECONDI, 7),
        pagina_contorni_allergeni(8),
    ]
    suffisso = "" if FINALE else "_BOZZA"
    lavori = [
        (carta, f"Menu_CusinDelMar_2026{suffisso}", "Menu Cusin del Mar 2026"),
        ([pagina_degustazione(ULTIMO, None)], f"Menu_UltimoDellAnno_2026{suffisso}", "Ultimo dell'Anno 2026"),
    ]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pagina_web = browser.new_page()
        for pagine, nome, titolo in lavori:
            f_html = QUI / f"{nome}.html"
            f_html.write_text(documento(pagine, titolo), encoding="utf-8")
            pagina_web.goto(f_html.resolve().as_uri())
            pagina_web.wait_for_load_state("networkidle")
            pagina_web.evaluate("document.fonts.ready")
            pagina_web.pdf(path=str(QUI / f"{nome}.pdf"), format="A4", print_background=True,
                           prefer_css_page_size=True)
            print("creato", nome + ".pdf")
        browser.close()


if __name__ == "__main__":
    main()
