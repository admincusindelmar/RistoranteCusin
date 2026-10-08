#!/usr/bin/env python3
"""
Genera il menù food del Ristorante Cusin nello stile della Carta Vini 2026.

Richiede: playwright, shapely (per i tratteggi dell'illustrazione di copertina).

Uso:
    python3 genera_menu.py            -> bozza (evidenzia in giallo ciò che è ancora da definire)
    python3 genera_menu.py --finale   -> versione pulita da stampa

Per modificare piatti, prezzi o allergeni basta cambiare i dati qui sotto.
Il testo tra [[doppie quadre]] è un punto ancora da decidere in cucina.

Misure riprese dalla Carta Vini 2026 (A4, porta menù forato):
  testo da 43,3 mm dal bordo sinistro · filetto prezzi a 183 mm · prezzi a 187 mm
  filetto di testata a 16,8 mm · numero di pagina a 282 mm · sfondo #e9ebf0
"""
import html
import math
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from a_capo import SISTEMA_A_CAPO_JS
from illustrazione_costa import COSTA_INCHIOSTRO

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


def piatto(nome, desc, en, allergeni=(), prezzo=None, chef=False, nota=None, cottura=False, extra=(),
           etichetta=None, tracce=()):
    """extra = salse o aggiunte a pagamento: [(nome, en, prezzo, allergeni)]
    etichetta = (italiano, inglese): segnalazione del piatto diversa dal consiglio dello Chef"""
    return dict(nome=nome, desc=desc, en=en, allergeni=allergeni, prezzo=prezzo, chef=chef,
                nota=nota, cottura=cottura, extra=extra, etichetta=etichetta, tracce=tracce)


NOVITA = ("Novità di stagione", "New this season")
CLASSICO = ("Un classico della casa", "A house classic")
FAMIGLIA = ("La ricetta di famiglia", "Family recipe")
TRADIZIONE = ("Tradizione toscana", "Tuscan tradition")


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
                piatto("Nido con uovo livornese",
                       "Nido con uovo livornese, gambero rosso, crema di fichi e olio alla liquirizia",
                       "Nest with Livorno-style egg, red prawn, fig cream and liquorice oil", (2, 3)),
                piatto("Sfera di mazzancolle",
                       "Sfera di mazzancolle ripiena di battuto di sedano rapa, "
                       "su crema di castagne e zenzero, passion fruit e lime",
                       "King prawn sphere filled with chopped celeriac, "
                       "on chestnut and ginger cream with passion fruit and lime", (2, 9)),
                piatto("Seppia e cipolla dorata",
                       "Seppia su crema di cipolla dorata dolce e croccante di cipolla",
                       "Cuttlefish on sweet golden onion cream with crispy onion", (14,)),
            ]),
            ("Primi", "First courses", [
                piatto("Gnocchi al Calasole",
                       "Gnocchi di riso con calamari, totani, seppie e tartufo",
                       "Rice gnocchi with squid, flying squid, cuttlefish and truffle", (3, 14)),
                piatto("Paccheri farciti",
                       "Paccheri con farcitura di ricotta senza lattosio, mazzancolle e colatura di cachi",
                       "Paccheri filled with lactose-free ricotta, king prawns and persimmon glaze",
                       (1, 2, 7)),
            ]),
            ("Secondo", "Main course", [
                piatto("Dentice e cardo",
                       "Trancio di dentice, carpaccio di cardo sfumato al vino bianco e olio al caffè",
                       "Dentex fillet, cardoon carpaccio with white wine and coffee oil", (4, 12)),
            ]),
            ("Pre-dessert", "Pre-dessert", [
                piatto("La nostra piccola pasticceria",
                       "Due cioccolatini fondenti ripieni, uno di marmellata di vino e l'altro "
                       "di crema di melone invernale, e un biscotto ai fichi",
                       "Two dark chocolates, filled with wine jam and with winter melon cream, "
                       "and a fig biscuit", (1, 3, 7, 12)),
            ]),
        ],
    ),
    dict(
        id="vegetariana",
        icona="alga",
        nome="Vegetariana di Mare",
        sotto="Il profumo del mare, senza pesce",
        sotto_en="The scent of the sea, without fish",
        prezzo=45,
        portate=[
            ("Antipasti", "Starters", [
                piatto("Cialda di ceci",
                       "Cialda di ceci, lattuga di mare, oliva taggiasca e scorza di limone",
                       "Chickpea wafer, sea lettuce, Taggiasca olive and lemon zest", ()),
                piatto("Sfera di verza",
                       "Sfera di cavolo verza con robiola e pera, senape e olio al wakame",
                       "Savoy cabbage sphere with robiola and pear, mustard and wakame oil",
                       (7, 10)),
            ]),
            ("Primo", "First course", [
                piatto("Raviolo e crema di zucca",
                       "Raviolo ripieno di ricotta senza lattosio, adagiato su crema di zucca, burro chiarificato alla salicornia",
                       "Raviolo filled with lactose-free ricotta, on pumpkin cream, clarified butter with samphire", (1, 3, 7)),
            ]),
            ("Secondo", "Main course", [
                piatto("Cacciucco vegetale",
                       "Brodo di alga kombu e funghi, pomodoro e cialda di pane croccante, "
                       "con cipollotto, melone invernale e cavolo nero",
                       "Kombu seaweed and mushroom broth, tomato and crispy bread wafer, "
                       "with spring onion, winter melon and black cabbage",
                       (1,)),
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
                piatto("Butterfly di baccalà, pecorino e Pepaya",
                       "Baccalà arrostito su crema di pecorino e Pepaya, il nostro pepe di semi di papaya",
                       "Roasted salt cod butterfly on pecorino cream with Pepaya, our papaya-seed pepper",
                       (4, 7)),
                piatto("Calamaro e tarassaco",
                       "Calamaro cotto a bassa temperatura su erbette di tarassaco, salsa di acciughe e aceto al mirtillo",
                       "Slow-cooked squid on dandelion greens, anchovy sauce and blueberry vinegar", (4, 12, 14)),
            ]),
            ("Primo", "First course", [
                piatto("Tagliolini al pepe e limone",
                       "Tagliolini artigianali al pepe e limone con limone candito, mazzancolle e funghi porcini",
                       "Handmade pepper and lemon tagliolini with candied lemon, king prawns and porcini mushrooms",
                       (1, 2, 3)),
            ]),
            ("Secondo", "Main course", [
                piatto("Spigola in crosta",
                       "Spigola con carapace di patata americana e pomodorini confit, "
                       "sale alla maggiorana e olio al ribes",
                       "Sea bass in a sweet-potato crust with confit cherry tomatoes, "
                       "marjoram salt and redcurrant oil", (4,)),
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
           "Mare caldo con crema alle ostriche, citronette di limone e olio EVO",
           "Warm seafood with oyster cream, lemon citronette and extra virgin olive oil",
           (2, 4, 14), prezzo="18,80"),
    piatto("Cappuccino di mazzancolle",
           "Mazzancolle con crema di lenticchie e spuma di erborinato",
           "King prawns with lentil cream and blue cheese foam",
           (2, 7), prezzo="17,80", chef=True),
    piatto("Sfera di verza",
           "Sfera di cavolo verza con robiola e pera, senape e olio al wakame",
           "Savoy cabbage sphere with robiola and pear, mustard and wakame oil",
           (7, 10), prezzo="16,40", nota="Vegetariano · Vegetarian"),
    piatto("Calamaro e tarassaco",
           "Calamaro cotto a bassa temperatura su erbette di tarassaco, salsa di acciughe e aceto al mirtillo",
           "Slow-cooked squid on dandelion greens, anchovy sauce and blueberry vinegar", (4, 12, 14),
           prezzo="17,90", etichetta=NOVITA),
]

# Componi il tuo Crudo: (nome, en, unità, unità_en, prezzo, allergeni)
CRUDO_PEZZI = [
    ("Ostrica del Doge", "Doge oyster", "al pezzo", "each", "8,50", (14,)),
    ("Scampo crudo", "Raw langoustine", "al pezzo", "each", "7,20", (2,)),
    ("Gambero rosso crudo", "Raw red prawn", "al pezzo", "each", "7,40", (2,)),
    ("Tartare di tonno", "Tuna tartare", "la porzione", "portion", "18", (4,)),
    ("Carpaccio di pescato", "Catch of the day carpaccio", "la porzione", "portion", "15", (4,)),
]
CRUDO_FUORI_MENU = ("Eventuali proposte di crudo fuori menù vi saranno comunicate dal nostro personale",
                    "Any off-menu raw specials will be presented by our staff")
CRUDO_SALSE_INCLUSE = ["Maionese all'arancia", "Maionese kiwi e lime"]
CRUDO_SALSE_INCLUSE_EN = "Orange mayonnaise and kiwi & lime mayonnaise"
CRUDO_SALSE_EXTRA = [  # (nome, en, prezzo, allergeni)
    ("Maionese al melone invernale", "Winter melon mayonnaise", "5", ()),
    ("Maionese all'ostrica", "Oyster mayonnaise", "5", (14,)),
]

PRIMI = [
    piatto("Paccheri Benedetto Cavalieri",
           "Cacio e pepe con gambero rosso e la sua bisque",
           "Paccheri cacio e pepe with red prawn and its bisque",
           (1, 2, 7), prezzo="24,80", chef=True, cottura=True,
           nota="Provalo con una spolverata di pepe del Madagascar · Try it with a dusting of Madagascar pepper"),
    piatto("Tagliolini al pepe e limone",
           "Tagliolini artigianali al pepe e limone con limone candito, mazzancolle e funghi porcini",
           "Handmade pepper and lemon tagliolini with candied lemon, king prawns and porcini mushrooms", (1, 2, 3),
           prezzo="17,80"),
    piatto("Spaghetto Benedetto Cavalieri",
           "Alle vongole veraci, fiocchi di pomodoro e olio al lime",
           "Spaghetti with clams, tomato flakes and lime oil", (1, 14), prezzo="19,30", cottura=True),
    piatto("Spaghetto Benedetto Cavalieri al pomodoro",
           "Spaghetto con salsa di pomarola fresca",
           "Spaghetti with fresh pomarola sauce", (1,), prezzo=15),
    piatto("Risotto al Calasole",
           "Risotto con battuto toscano, calamari, totani, seppie e tartufo",
           "Risotto with Tuscan soffritto, squid, flying squid, cuttlefish and truffle", (9, 14),
           prezzo="18,40", etichetta=NOVITA, nota="Senza lattosio · Lactose free"),
    piatto("Risotto al dentice",
           "Risotto al dentice con finocchietto selvatico, cipollotto fresco e carpaccio di finocchio",
           "Dentex risotto with wild fennel, fresh spring onion and fennel carpaccio", (4,),
           prezzo="19,30", nota="Senza lattosio · Lactose free"),
    piatto("Ravioli e crema di zucca",
           "Ravioli ripieni di ricotta senza lattosio, adagiati su crema di zucca, burro chiarificato alla salicornia",
           "Ravioli filled with lactose-free ricotta, on pumpkin cream, clarified butter with samphire", (1, 3, 7),
           nota="Vegetariano · Vegetarian"),
]

SECONDI = [
    piatto("Spigola alla griglia",
           "Spigola alla griglia con verdure spicchiate",
           "Grilled sea bass with roasted vegetable wedges", (4,), prezzo=24, chef=True),
    piatto("Grigliata di mare",
           "Mazzancolle, gambero rosso, scampi, tonno e spiedino di calamari, "
           "servita con due salse incluse: basilico e arancia",
           "King prawns, red prawn, langoustines, tuna and squid skewer, "
           "served with two sauces: basil and orange",
           (2, 4, 14), prezzo=42,
           extra=[("Salsa all'ostrica", "Oyster sauce", "5", (14,)),
                  ("Salsa al tartufo", "Truffle sauce", "5", ())]),
    piatto("Scaloppata di tonno alla nocciola",
           "Tonno in crosta di nocciola, crema di acetosella, olio al prezzemolo e verdure scottate",
           "Tuna in hazelnut crust, sorrel cream, parsley oil and seared vegetables",
           (4, 8), prezzo=25),
    piatto("Il fritto di mare della Zia",
           "Frittura di mare e verdure in farina di riso, leggera e croccante",
           "Light, crispy fried seafood and vegetables in rice flour",
           (2, 4, 14), prezzo=21, etichetta=FAMIGLIA),
    piatto("Cacciucco vegetale",
           "Brodo di alga kombu e funghi, pomodoro e cialda di pane croccante, "
           "con cipollotto, melone invernale e cavolo nero",
           "Kombu seaweed and mushroom broth, tomato and crispy bread wafer, "
           "with spring onion, winter melon and black cabbage",
           (1,), prezzo=24, nota="Vegetariano · Vegetarian"),
    piatto("Tagliata toscana",
           "Tagliata di manzo con patate arrosto",
           "Sliced Tuscan beef steak with roast potatoes", (), prezzo=25, etichetta=TRADIZIONE),
]

CONTORNI = [
    piatto("Verdure al forno spicchiate", "", "Roasted vegetable wedges", (), prezzo="8,50"),
    piatto("Patate arrosto", "", "Roast potatoes", (), prezzo=7),
    piatto("Patatine fritte", "", "French fries", (), prezzo=7),
    piatto("Insalata verde", "", "Green salad", (), prezzo=7),
    piatto("Insalata mista", "", "Mixed salad", (), prezzo=7),
]

SERVIZIO = [
    ("Acqua in vetro", "Water in glass bottle", "3"),
    ("Coperto", "Cover charge", "4"),
    ("Servizio dolce", "Cake service for desserts brought by guests", "2"),
    ("Servizio tappo", "Corkage fee", "16"),
]


# ---------------------------------------------------------------------------
# REGOLE GENERALI SUGLI ALLERGENI (indicazioni della cucina)
# ---------------------------------------------------------------------------
SEDANO, SOIA, SENAPE = 9, 6, 10


def _aggiungi(p, *numeri):
    p["allergeni"] = tuple(sorted(set(p["allergeni"]) | set(numeri)))


# il sedano è presente in tutte le preparazioni di antipasti e primi
for _d in DEGUSTAZIONI + [ULTIMO]:
    for _portata, _, _piatti in _d["portate"]:
        if _portata in ("Antipasti", "Primi", "Primo"):
            for _p in _piatti:
                _aggiungi(_p, SEDANO)
for _p in ANTIPASTI + PRIMI:
    _aggiungi(_p, SEDANO)

# pasta Benedetto Cavalieri: senza uova, può contenere tracce di soia e senape
# (anche i paccheri farciti della Stella di Mare sono Benedetto Cavalieri)
_cavalieri = [p for p in PRIMI if "Benedetto Cavalieri" in p["nome"]]
_cavalieri += [p for _, _, ps in DEGUSTAZIONI[0]["portate"] for p in ps if p["nome"] == "Paccheri farciti"]
assert len(_cavalieri) == 4
for _p in _cavalieri:
    _p["allergeni"] = tuple(a for a in _p["allergeni"] if a != 3)
    _p["tracce"] = (SOIA, SENAPE)

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


def allerg_riga(a, tracce=()):
    """Allergeni sulla stessa riga della traduzione; le tracce sono indicate a parte."""
    if not a and not tracce:
        return ""
    tr = f' · tracce {" · ".join(map(str, tracce))}' if tracce else ""
    # lo spazio prima permette di mandare a capo gli allergeni interi, senza spezzare il testo
    return f' <span class="all-riga">Allergeni {" · ".join(str(x) for x in a)}{tr}</span>'


# --- Illustrazioni a tratto, in stile incisione ------------------------------

def _p(x, y):
    return f"{x:.2f} {y:.2f}"


def svg_capasanta():
    """Conchiglia (capasanta) con costolature doppie, bordo ondulato e linee di crescita."""
    cx, cy, n = 60.0, 92.0, 15
    a0, a1 = math.radians(18), math.radians(162)

    def raggio(a):
        return 78 * (0.80 + 0.20 * math.sin(a))

    def pt(r, a):
        return cx + r * math.cos(a), cy - r * math.sin(a)

    angoli = [a0 + (a1 - a0) * i / (n - 1) for i in range(n)]
    bordo = f"M{_p(*pt(raggio(a0) * .93, a0))}"
    for i in range(n - 1):
        am = (angoli[i] + angoli[i + 1]) / 2
        p1 = pt(raggio(angoli[i + 1]) * .93, angoli[i + 1])
        c = pt(raggio(am) * 1.04, am)
        bordo += f" Q{_p(*c)} {_p(*p1)}"
    coste = ""
    for i, a in enumerate(angoli[:-1]):
        am = (a + angoli[i + 1]) / 2
        for d in (-.018, .018):
            x1, y1 = pt(9, am + d)
            x2, y2 = pt(raggio(am) * 1.0, am + d * 2.2)
            xc, yc = pt(raggio(am) * .55, am + d * 1.6 + .015)
            coste += f"M{_p(x1, y1)} Q{_p(xc, yc)} {_p(x2, y2)} "
    crescita = ""
    for f in (.34, .5, .66, .8):
        pts = [pt(raggio(a) * f, a) for a in [a0 + (a1 - a0) * k / 40 for k in range(41)]]
        crescita += "M" + " L".join(_p(*q) for q in pts) + " "
    l0, r0 = pt(raggio(a1) * .93, a1), pt(raggio(a0) * .93, a0)
    orecchie = (f"M{_p(*l0)} L{_p(cx - 26, cy - 8)} L{_p(cx - 28, cy + 4)} L{_p(cx, cy + 4)} "
                f"L{_p(cx + 28, cy + 4)} L{_p(cx + 26, cy - 8)} L{_p(*r0)} "
                f"M{_p(cx - 26, cy - 8)} L{_p(cx - 9, cy - 5)} M{_p(cx + 26, cy - 8)} L{_p(cx + 9, cy - 5)} "
                f"M{_p(cx - 24, cy - 2)} L{_p(cx - 8, cy)} M{_p(cx + 24, cy - 2)} L{_p(cx + 8, cy)}")
    return f"""<svg viewBox="0 0 120 100" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
<path d="{bordo}" stroke-width="1.1"/><path d="{orecchie}" stroke-width=".9"/>
<path d="{coste}" stroke-width=".55"/><path d="{crescita}" stroke-width=".4" stroke-dasharray="1.2 2.2" opacity=".75"/>
</g></svg>"""


def svg_pesce():
    """Pesce (orata) con squame, pinne a raggi, opercolo e linea laterale."""
    corpo = ("M14 40 C 26 22, 60 10, 96 16 C 114 19, 128 28, 138 38 "
             "C 128 48, 114 57, 96 60 C 60 66, 26 58, 14 40 Z")
    squame = ""
    for riga, y in enumerate(range(14, 66, 5)):
        off = 3 if riga % 2 else 0
        for x in range(48 + off, 134, 6):
            squame += f"M{x} {y - 2.6} A3 3 0 0 0 {x} {y + 2.6} "
    coda = "M136 40 L162 18 C 156 30, 156 50, 162 62 Z"
    raggi_coda = "".join(f"M138 40 L{160 - abs(k) * .35:.1f} {40 + k:.1f} " for k in range(-19, 21, 4))
    dorsale = "M50 17 C 58 2, 90 -1, 108 20"
    raggi_dors = "".join(
        f"M{50 + i * 5.8:.1f} {17 - 1.5 * math.sin(i / 10 * math.pi) + (i / 10) * 3:.1f} "
        f"L{53 + i * 5.4:.1f} {7 - 5 * math.sin(i / 10 * math.pi) + (i / 10) * 11:.1f} "
        for i in range(11))
    anale = "M92 60 C 98 70, 110 70, 118 53"
    raggi_anale = "".join(f"M{94 + i * 5:.1f} {60 - i * 1.6:.1f} L{96 + i * 5:.1f} {67 - i * 2.4:.1f} "
                          for i in range(5))
    pettorale = "M44 44 C 54 42, 64 48, 68 56 C 58 56, 49 52, 44 44 Z"
    raggi_pett = "".join(f"M46 45 L{58 + i * 2.6:.1f} {49 + i * 1.8:.1f} " for i in range(4))
    return f"""<svg viewBox="0 0 166 72" class="ill" aria-hidden="true">
<defs><clipPath id="corpo-pesce"><path clip-rule="evenodd" d="{corpo} {pettorale}"/></clipPath></defs>
<g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
<path d="{squame}" stroke-width=".45" opacity=".7" clip-path="url(#corpo-pesce)"/>
<path d="{corpo}" stroke-width="1.1"/>
<path d="{dorsale}" stroke-width=".9"/><path d="{raggi_dors}" stroke-width=".5"/>
<path d="{anale}" stroke-width=".9"/><path d="{raggi_anale}" stroke-width=".5"/>
<path d="{coda}" stroke-width=".9"/><path d="{raggi_coda}" stroke-width=".45"/>
<path d="{pettorale}" stroke-width=".8"/><path d="{raggi_pett}" stroke-width=".45"/>
<path d="M40 22 C 48 32, 48 48, 40 58" stroke-width=".9"/><path d="M35 25 C 41 33, 41 47, 35 55" stroke-width=".5"/>
<path d="M44 34 C 70 27, 104 29, 134 39" stroke-width=".5" stroke-dasharray="1.4 1.8"/>
<circle cx="27" cy="35" r="3.6" stroke-width=".9"/><circle cx="27.4" cy="35" r="1.5" fill="currentColor" stroke="none"/>
<path d="M14 40 L22 41.5" stroke-width=".8"/>
</g></svg>"""


def svg_alga():
    """Alga marina a nastri ondulati con nervatura, bolle e sasso: marino ma vegetale."""
    def fronda(x0, alt, amp, fase, larg, pieghe=1.6):
        n = 36
        cen, sx, dx = [], [], []
        for i in range(n + 1):
            u = i / n
            y = 96 - u * alt
            x = x0 + amp * math.sin(u * math.pi * pieghe + fase) * u
            w = larg * (math.sin(math.pi * min(u * 1.08, 1)) ** .7) + .4 * (1 - u)
            cen.append((x, y))
            sx.append((x - w, y))
            dx.append((x + w, y))
        bordo = "M" + " L".join(_p(*q) for q in sx) + " L" + " L".join(_p(*q) for q in reversed(dx)) + " Z"
        nerv = "M" + " L".join(_p(*q) for q in cen)
        vene = ""
        for i in range(4, n - 2, 3):
            (xc, yc), (xl, yl), (xr, yr) = cen[i], sx[i - 2], dx[i - 2]
            vene += f"M{_p(xc, yc)} L{_p(xl * .55 + xc * .45, yl)} M{_p(xc, yc)} L{_p(xr * .55 + xc * .45, yr)} "
        return bordo, nerv, vene

    parti = [fronda(42, 86, 13, 0, 8.5, 2.1), fronda(26, 64, 10, 2.4, 7, 1.9), fronda(58, 72, 11, 3.8, 7.2, 2.0),
             fronda(14, 40, 6, 1, 5, 1.5), fronda(72, 46, 6, 4.4, 5.2, 1.6)]
    bordi = "".join(f'<path d="{b}" stroke-width=".9" fill="#fff"/>' for b, _, _ in reversed(parti))
    nerv = "".join(f'<path d="{n}" stroke-width=".5"/><path d="{v}" stroke-width=".35" opacity=".8"/>'
                   for _, n, v in reversed(parti))
    return f"""<svg viewBox="-4 0 92 100" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
{bordi}{nerv}
<path d="M10 97 C 16 90, 30 89, 38 94 C 46 89, 62 88, 74 97" stroke-width=".9"/>
<path d="M18 96 C 22 93, 28 93, 31 95 M50 95 C 55 92, 62 92, 66 95" stroke-width=".4"/>
<circle cx="76" cy="26" r="2.6" stroke-width=".7"/><circle cx="81" cy="15" r="1.8" stroke-width=".7"/>
<circle cx="76" cy="6" r="1.2" stroke-width=".7"/><circle cx="6" cy="44" r="1.6" stroke-width=".7"/>
</g></svg>"""


FOGLIA = """<svg viewBox="0 0 60 60" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
<path d="M10 50C8 26 24 8 52 8c0 28-18 44-42 42z"/><path d="M10 50L44 16" stroke-width=".7"/>
<path d="M20 40l-2-10M20 40l10 2M28 32l-1-11M28 32l11 1M36 24l0-9M36 24l9 0" stroke-width=".5"/></g></svg>"""

PESCE = svg_pesce()
CONCHIGLIA = svg_capasanta()
ALGA = svg_alga()

SPIGA = """<svg viewBox="0 0 60 60" class="ill" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
<path d="M30 56V14"/><path d="M30 18c-6-2-9-8-8-14 6 2 9 8 8 14zM30 18c6-2 9-8 8-14-6 2-9 8-8 14z"/>
<path d="M30 30c-7-2-11-8-10-14 7 2 11 8 10 14zM30 30c7-2 11-8 10-14-7 2-11 8-10 14z"/>
<path d="M30 42c-7-2-11-8-10-14 7 2 11 8 10 14zM30 42c7-2 11-8 10-14-7 2-11 8-10 14z"/></g></svg>"""

# freccia arrotolata disegnata a mano, punta verso sinistra (verso il nome del piatto)
FRECCIA = """<svg viewBox="0 0 90 34" class="freccia" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
<path d="M86 22 C 74 30, 58 30, 56 20 C 54 10, 68 8, 68 17 C 68 26, 46 30, 30 26 C 20 23, 12 19, 5 15"/>
<path d="M5 15 L13 13.2 M5 15 L10.5 21"/></g></svg>"""


def testata(titolo, sotto, icona=""):
    return f"""<header class="testata{'' if icona else ' senza-icona'}">
  <h1>{t(titolo)}</h1><div class="riga"></div><p class="sottotitolo">{t(sotto)}</p>
  {f'<div class="icona">{icona}</div>' if icona else ''}
</header>"""


def riga_piatto(p):
    chef = '<span class="chef">il consiglio dello Chef</span>' if p["chef"] else ""
    if p["etichetta"]:
        chef += f'<span class="etichetta">{p["etichetta"][0]} <em>{p["etichetta"][1]}</em></span>'

    cott = (f'<span class="cottura">{FRECCIA}<span>18 minuti<br>di cottura<br><em>18 min cooking</em></span></span>'
            if p["cottura"] else "")
    desc = f'<p class="desc">{t(p["desc"])}</p>' if p["desc"] else ""
    en = f'<p class="en">{t(p["en"])}{allerg_riga(p["allergeni"], p["tracce"])}</p>' if p["en"] else ""
    nota = f'<p class="nota">{t(p["nota"])}</p>' if p["nota"] else ""
    classi = "voce" + (" firma" if p["chef"] else "") + (" con-cottura" if p["cottura"] else "")
    return f"""<div class="{classi}">
  <div class="testo">{chef}<h3>{t(p['nome'])}{cott}</h3>{desc}{en}{nota}</div>
  <div class="prezzo">{prezzo(p['prezzo'])}</div>{righe_extra(p['extra'], 'Salse in aggiunta', 'Extra sauces')}
</div>"""


def righe_extra(extra, titolo, titolo_en):
    """Aggiunte a pagamento: righe con il prezzo nella stessa colonna dei piatti."""
    righe = ""
    for i, (nome, en, pr, al) in enumerate(extra):
        intest = (f'<span class="extra-tit">{titolo} <em>{titolo_en}</em></span>' if i == 0 else "")
        al_txt = f' <span class="all-riga">Allergeni {" · ".join(map(str, al))}</span>' if al else ""
        righe += (f'<div class="testo extra">{intest}<span class="extra-nome">+ {t(nome)}</span> '
                  f'<em class="en-riga">{t(en)}</em>{al_txt}</div><div class="prezzo extra">{pr}</div>')
    return righe


def elenco(voci, classe=""):
    return f'<div class="elenco {classe}">{"".join(riga_piatto(v) for v in voci)}</div>'


def pagina(corpo, n=None, classe=""):
    num = f'<footer class="num">{n}</footer>' if n else ""
    return f'<section class="pagina {classe}">{corpo}{num}</section>'


def pagina_copertina():
    """Pagina iniziale: citazione di Oscar Wilde, illustrazione a tratto, nome del ristorante."""
    corpo = f"""<div class="copertina">
  <div class="cop-ill">{COSTA_INCHIOSTRO}</div>
  <blockquote>
    <p class="cit">«Ho dei gusti semplicissimi:<br>mi accontento sempre del meglio.»</p>
    <p class="autore">Oscar Wilde</p>
    <p class="cit-en">“I have the simplest tastes. I am always satisfied with the best.”</p>
  </blockquote>
</div>
<p class="nome-rist">Ristorante Cusin</p>"""
    return pagina(corpo, None, "p-copertina")


def pagina_degustazione(d, n):
    blocchi = []
    for it, en, piatti in d["portate"]:
        voci = "".join(
            f"""<li><h3>{t(p['nome'])}</h3>
            {f'<p class="desc">{t(p["desc"])}</p>' if p['desc'] else ''}
            <p class="en">{t(p['en'])}{allerg_riga(p['allergeni'], p['tracce'])}</p></li>"""
            for p in piatti)
        blocchi.append(f'<div class="portata"><h2>{it} <span>{en}</span></h2><ul>{voci}</ul></div>')
    corpo = f"""
{testata('Degustazione', 'Tasting Menu', ALGA if d.get('icona') == 'alga' else CONCHIGLIA)}
<div class="deg">
  <h1 class="deg-nome">{t(d['nome'])}</h1>
  <p class="deg-sotto">{t(d['sotto'])}<br><em>{t(d['sotto_en'])}</em></p>
  {''.join(blocchi)}
  <div class="deg-prezzo"><span class="cifra">{d['prezzo']}</span>
    <span class="pp">a persona<br><em>per person</em></span></div>
  <p class="tavolo">Il menù degustazione è servito per l'intero tavolo<br>
  <em>The tasting menu is served to the whole table</em></p>
  <p class="abbina">Chiedi al nostro personale l'abbinamento al calice dalla Carta dei Vini<br>
  <em>Ask our staff for a wine-by-the-glass pairing from our Wine List</em></p>
</div>"""
    return pagina(corpo, n, "p-deg riempi")


def pagina_carta(titolo, sotto, icona, intro, corpo_extra, n, classe=""):
    corpo = f"""{testata(titolo, sotto, icona)}
<p class="intro">{intro}</p>{corpo_extra}"""
    return pagina(corpo, n, (classe + " riempi").strip())


def pagina_crudo(n):
    pezzi = "".join(f"""<div class="voce">
  <div class="testo"><h3>{t(nome)} <span class="unita">{unita}</span></h3>
  <p class="en">{t(en)} · {unita_en}{allerg_riga(al)}</p></div>
  <div class="prezzo">{prezzo(pr)}</div></div>""" for nome, en, unita, unita_en, pr, al in CRUDO_PEZZI)
    salse = "".join(f"<li>{t(s)}</li>" for s in CRUDO_SALSE_INCLUSE)
    extra = "".join(f"""<div class="voce"><div class="testo"><h3>+ {t(nome)}</h3>
  <p class="en">{en}{allerg_riga(al)}</p></div><div class="prezzo">{pr}</div></div>""" for nome, en, pr, al in CRUDO_SALSE_EXTRA)
    corpo = f"""{testata('Il Crudo', 'Raw Bar', CONCHIGLIA)}
<div class="crudo-titolo">
  <h2>Componi il tuo Crudo</h2>
  <p>Il tuo plateau, a modo tuo: scegli, abbina, brinda.<br><em>Your platter, your way: pick, pair and raise a glass.</em></p>
</div>
<ol class="passi">
  <li><span class="n">1</span>
    <h4>Scegli i tuoi pezzi <em>Pick your pieces</em></h4>
    <div class="elenco">{pezzi}</div>
    <p class="fuori-menu">{CRUDO_FUORI_MENU[0]}<br><em>{CRUDO_FUORI_MENU[1]}</em></p>
  </li>
  <li><span class="n">2</span>
    <h4>Abbina le nostre salse <em>Pair them with our sauces</em></h4>
    <p class="salse-tit">Incluse nel tuo crudo <em>Included</em></p>
    <ul class="salse">{salse}</ul>
    <p class="salse-en">{CRUDO_SALSE_INCLUSE_EN} · Allergeni · Allergens&nbsp; 3</p>
    <p class="salse-tit">Da aggiungere <em>Add-ons</em></p>
    <div class="elenco">{extra}</div>
  </li>
  <li><span class="n">3</span>
    <h4>Brinda con le bollicine <em>Raise a glass of bubbles</em></h4>
    <div class="elenco compatto">
      <div class="voce"><div class="testo"><h3>Calice di Franciacorta <em class="en-riga">Glass of Franciacorta</em></h3></div><div class="prezzo">14</div></div>
      <div class="voce"><div class="testo"><h3>Calice di Champagne <em class="en-riga">Glass of Champagne</em></h3></div><div class="prezzo">23</div></div>
    </div>
  </li>
</ol>
<p class="condividi">{FRECCIA}perfetto da condividere al centro del tavolo</p>"""
    return pagina(corpo, n, "p-crudo riempi")


def pagina_primi(n):
    nota = """<div class="nota-pasta">
  <p class="spiega">Usiamo la pasta Benedetto Cavalieri – artigianale, trafilata al bronzo, essiccata per 30 ore
  con il “Metodo delicato” dal 1918. Il lungo tempo di cottura è la misura della sua qualità.</p>
  <p class="en">We use Benedetto Cavalieri pasta – artisanal, bronze-drawn and dried for 30 hours
  with the “Metodo delicato” since 1918. Its long cooking time is the measure of its quality.</p>
</div>"""
    corpo = f"""{testata("Primi Piatti", "First Courses", SPIGA)}{elenco(PRIMI)}{nota}"""
    return pagina(corpo, n, "p-primi riempi")


def pagina_secondi(n):
    return pagina_carta("Secondi Piatti", "Main Courses", PESCE,
                        "Il pescato alla griglia, in crosta e fritto leggero · "
                        "<em>Grilled, crusted and lightly fried catch</em>",
                        elenco(SECONDI), n)


def elenco_contorni():
    return f"""<div class="elenco compatto">{"".join(f'''<div class="voce"><div class="testo"><h3>{c["nome"]} <em class="en-riga">{c["en"]}</em></h3></div>
  <div class="prezzo">{prezzo(c["prezzo"])}</div></div>''' for c in CONTORNI)}</div>"""


def pagina_servizio_allergeni(n):
    servizio = "".join(f"""<div class="voce"><div class="testo"><h3>{a} <em class="en-riga">{b}</em></h3></div>
  <div class="prezzo">{c}</div></div>""" for a, b, c in SERVIZIO)
    leg = "".join(f"<li><b>{k}</b> {a} <em>{b}</em></li>" for k, (a, b) in ALLERGENI.items())
    corpo = f"""{testata('Contorni', 'Side Dishes', FOGLIA)}
{elenco_contorni()}
<div class="sezione"><h2>Servizio <span>Service</span></h2></div>
<div class="elenco compatto">{servizio}</div>
<div class="allergeni">
  <h2>Allergeni <span>Allergens</span></h2>
  <ul class="legenda">{leg}</ul>
  <p>Il numero accanto a ogni piatto indica le sostanze che possono causare allergie o intolleranze
  (Reg. UE 1169/2011). Per qualsiasi esigenza alimentare rivolgetevi al nostro personale:
  la documentazione completa è disponibile su richiesta. La dicitura «tracce» indica allergeni
  che possono essere presenti in tracce.</p>
  <p class="en">The numbers next to each dish refer to the allergens listed above (EU Reg. 1169/2011).
  Please inform our staff of any food allergy or intolerance; full documentation is available on request.
  «Tracce» means the product may contain traces.</p>
  <p>Il pesce destinato al consumo crudo o praticamente crudo è sottoposto a trattamento di bonifica
  preventiva mediante abbattimento, come previsto dal Reg. CE 853/2004.</p>
  <p class="en">Fish served raw or nearly raw has been blast-frozen in accordance with EC Reg. 853/2004.</p>
</div>"""
    return pagina(corpo, n)


CSS = """
@page { size: A4; margin: 0; }
:root {
  --inchiostro:#191919; --tenue:#6d6d74; --filo-testata:#3d3d3b; --filo:#afafb2;
  --oro:#a88a4a; --ill:#8b8b93;
  /* misure della Carta Vini */
  --sx: 43.3mm;      /* inizio testo dal bordo sinistro (fori del porta menù) */
  --dx: 17mm;        /* margine destro */
  --x-filo: 139.7mm; /* filetto prezzi a 183 mm dal bordo = 139,7 mm dall'inizio testo */
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: none; color: var(--inchiostro);
  font-family: 'Cormorant Garamond', Georgia, serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
mark { background: #fff1a8; color: #6b5200; padding: 0 3px; border-radius: 2px; font-style: normal; }
.pagina { width: 210mm; height: 297mm; padding: 8.4mm var(--dx) 22mm var(--sx); position: relative;
  overflow: hidden; page-break-after: always; }
.num { position: absolute; top: 282mm; left: 0; right: 0; text-align: center; font-size: 15pt;
  font-weight: 300; color: #231f20; }
.ill { width: 100%; height: 100%; color: var(--ill); }

/* testata: MAIUSCOLO spaziato, filetto a 16,8 mm, sottotitolo sotto il filetto */
.testata { position: relative; height: 26mm; margin-bottom: 6mm; }
.testata h1 { font-size: 21pt; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; line-height: 1.1; }
.testata .riga { position: absolute; top: 9.4mm; left: 0; width: 116mm; height: .53mm; background: var(--filo-testata); }
.testata .sottotitolo { position: absolute; top: 10.6mm; font-size: 16pt; font-weight: 300; letter-spacing: .1em; }
.testata.senza-icona .riga { width: 143.5mm; }
/* illustrazione nello spazio dopo il filetto: da 165 a 192 mm, centrata sul filetto */
.testata .icona { position: absolute; left: 121.5mm; top: 3.4mm; width: 28mm; height: 12.5mm;
  display: flex; align-items: center; justify-content: center; }
.testata .icona svg { width: 100%; height: 100%; }
.intro { font-size: 12.5pt; font-style: italic; color: var(--tenue); margin: -1mm 0 6mm; max-width: 136mm; }

/* voci: testo a sinistra, filetto verticale continuo a 183 mm, prezzo a 187 mm */
.elenco { position: relative; display: flex; flex-direction: column; gap: 4.2mm; }
.elenco::before { content: ""; position: absolute; left: var(--x-filo); top: -1mm; bottom: -1mm;
  width: .53mm; background: var(--filo); }
.voce { display: grid; grid-template-columns: calc(var(--x-filo) - 4mm) 1fr; column-gap: 8mm; }
.voce .testo { position: relative; }
.voce .prezzo { font-size: 14pt; font-weight: 700; align-self: center; }
.voce h3 { font-size: 14.5pt; font-weight: 700; line-height: 1.2; }
.voce .desc { font-size: 12.5pt; line-height: 1.25; }
.voce .en { font-size: 11.5pt; font-style: italic; color: var(--tenue); line-height: 1.25; }
.voce .nota { font-size: 11.5pt; font-style: italic; color: var(--oro); margin-top: .6mm; line-height: 1.25; }
.all { display: block; font-size: 9.5pt; letter-spacing: .05em; color: var(--tenue); margin-top: .6mm; }
.chef { display: block; font-family: 'Caveat', cursive; font-weight: 600; font-size: 14pt; color: var(--oro);
  line-height: 1; margin-bottom: .8mm; }
.passi .chef, .crudo .chef { display: inline; }
.voce.firma .testo { border: 1px solid #c9bb95; padding: 2.6mm 3.5mm; margin-left: -3.5mm; }
.compatto { gap: 2.6mm; }
.compatto .voce h3 { font-size: 14pt; }
.en-riga { font-weight: 400; font-size: 11.5pt; color: var(--tenue); margin-left: 2mm; }

/* freccia arrotolata "18 minuti" */
.voce h3 { position: relative; }
.cottura { position: absolute; right: 0; top: .6mm; display: flex; align-items: center; gap: 1mm;
  font-family: 'Caveat', cursive; font-size: 14pt; line-height: .95; color: var(--oro); }
.cottura em { font-style: normal; font-size: 11.5pt; opacity: .85; }
.voce.firma .cottura { right: 0; }
.p-primi .elenco { gap: 2.6mm; }
.p-primi .intro { margin-bottom: 4.5mm; }
.voce.con-cottura .testo > p:not(.nota) { max-width: calc(100% - 36mm); }
.voce.con-cottura.firma .testo > p:not(.nota) { max-width: calc(100% - 33mm); }
.freccia { width: 10mm; height: 6mm; color: var(--oro); flex: none; }
.nota-pasta { margin-top: 4.5mm; padding-top: 2mm; border-top: 1px solid var(--filo); max-width: 136mm; }
.nota-pasta p { font-size: 12pt; line-height: 1.3; }
.nota-pasta p.en { font-size: 11pt; font-style: italic; color: var(--tenue); margin-top: 1mm; }

/* sotto-sezione (come "Toscana" nella carta vini) */
.sezione { margin: 8mm 0 3.5mm; }
.sezione h2 { font-size: 19pt; font-weight: 700; }
.sezione h2 span { font-size: 13pt; font-weight: 400; font-style: italic; color: var(--tenue); margin-left: 2mm; }

/* il crudo */
.crudo-titolo { margin: -2mm 0 5mm; }
.crudo-titolo h2 { font-family: 'Caveat', cursive; font-weight: 600; font-size: 33pt; color: var(--oro); line-height: 1; }
.crudo-titolo p { font-size: 12.5pt; line-height: 1.3; margin-top: 1mm; }
.crudo-titolo em { color: var(--tenue); }
.passi { list-style: none; position: relative; }
.passi > li:not(:last-child)::before { content: ""; position: absolute; left: -9.3mm; top: 11mm;
  bottom: calc(-6mm - var(--aria, 0mm) + 1.5mm); border-left: 1.3px dashed #c9bb95; }
.passi > li { position: relative; margin-bottom: 6mm; }
.passi .n { position: absolute; left: -14.5mm; top: -1mm; width: 10.5mm; height: 10.5mm; border-radius: 50%;
  border: 1.2px solid var(--oro); color: var(--oro); text-align: center;
  font-family: 'Caveat', cursive; font-weight: 600; font-size: 19pt; line-height: 10mm; }
.passi h4 { font-size: 12pt; font-weight: 700; letter-spacing: .22em; text-transform: uppercase; margin-bottom: 3mm; }
.passi h4 em { font-weight: 400; letter-spacing: .06em; text-transform: none; color: var(--tenue); margin-left: 1.5mm; font-size: 12pt; }
.passi .elenco { gap: 2.6mm; }
.unita { font-weight: 400; font-style: italic; font-size: 12pt; color: var(--tenue); }
.salse { list-style: none; display: flex; flex-wrap: wrap; gap: 2.5mm; max-width: 136mm; }
.salse li { font-size: 13pt; padding: 1.2mm 4.5mm; border: 1px solid #c9bb95; border-radius: 20mm; }
.condividi { display: flex; align-items: center; gap: 2mm; font-family: 'Caveat', cursive; font-size: 17pt;
  color: var(--oro); margin-top: -1mm; }

/* degustazioni: centrate sulla colonna di testo, non sul foglio */
.p-deg { display: flex; flex-direction: column; }
.deg { text-align: center; flex: 1; display: flex; flex-direction: column; justify-content: center; }
.deg > * { flex: none; }
.deg-nome { font-size: 35pt; font-weight: 400; letter-spacing: .06em; line-height: 1.05; }
.deg-sotto { font-size: 13pt; color: var(--tenue); margin: 1.5mm 0 4mm; line-height: 1.25; }
.portata { margin: 0 auto 2.6mm; width: 100%; }
.portata h2 { font-size: 11.5pt; font-weight: 600; letter-spacing: .3em; text-transform: uppercase; color: var(--oro);
  margin-bottom: 1.2mm; }
.portata h2 span { font-weight: 400; font-style: italic; letter-spacing: .08em; text-transform: none; color: var(--tenue); }
.portata ul { list-style: none; }
.portata li { margin-bottom: 1.8mm; }
.portata li h3 { font-size: 14pt; font-weight: 700; line-height: 1.15; }
.portata .desc { font-size: 12.5pt; line-height: 1.2; }
.portata .en { font-size: 11.3pt; font-style: italic; color: var(--tenue); line-height: 1.2; }
.all-riga { font-style: normal; font-size: 9.5pt; letter-spacing: .05em; margin-left: 2.5mm; white-space: nowrap; }
.all-riga::before { content: '·'; margin-right: 2.5mm; }
.all-riga.a-capo::before { content: none; }
.deg-prezzo { align-self: center; display: inline-flex; align-items: center; gap: 4mm; margin-top: 1.5mm; padding: 0 7mm;
  border-left: .53mm solid var(--filo); border-right: .53mm solid var(--filo); }
.deg-prezzo .cifra { font-size: 31pt; font-weight: 600; }
.deg-prezzo .pp { font-size: 11pt; text-align: left; line-height: 1.2; color: var(--tenue); }
.tavolo { font-size: 12.5pt; font-weight: 600; margin-top: 2.5mm; line-height: 1.25; }
.tavolo em { font-weight: 400; color: var(--tenue); }
.abbina { font-size: 11.5pt; color: var(--tenue); margin-top: 1.5mm; line-height: 1.25; }

/* allergeni */
.allergeni { margin-top: 10mm; border-top: 1px solid var(--filo); padding-top: 5mm; max-width: 150mm; }
.allergeni h2 { font-size: 14pt; font-weight: 700; letter-spacing: .3em; text-transform: uppercase; margin-bottom: 3mm; }
.allergeni h2 span { font-weight: 400; font-style: italic; letter-spacing: .08em; text-transform: none; color: var(--tenue); }
.legenda { list-style: none; columns: 2; column-gap: 8mm; font-size: 12pt; margin-bottom: 4mm; }
.legenda li { padding: .5mm 0; }
.legenda b { display: inline-block; width: 7mm; }
.legenda em { color: var(--tenue); }
.allergeni p { font-size: 10.8pt; line-height: 1.3; margin-bottom: 1mm; }
.allergeni p.en { font-style: italic; color: var(--tenue); margin-bottom: 2.4mm; }
/* aria: --aria viene calcolata pagina per pagina per riempire il foglio senza sforare */
.riempi { --aria: 0mm; }
.riempi .elenco { gap: calc(4.2mm + var(--aria)); }
.p-primi.riempi .elenco { gap: calc(1.2mm + var(--aria)); }
.riempi .voce .testo > * + * { margin-top: calc(var(--aria) * .09); }
.riempi .voce .testo > .all { margin-top: calc(.6mm + var(--aria) * .09); }
.riempi .elenco.compatto { gap: calc(2.6mm + var(--aria) * .5); }
.riempi .intro { margin-bottom: calc(6mm + var(--aria)); }
.riempi .sezione { margin-top: calc(8mm + var(--aria)); margin-bottom: calc(3.5mm + var(--aria) * .5); }
.riempi .nota-pasta { margin-top: calc(2mm + var(--aria)); }
.riempi .passi > li { margin-bottom: calc(6mm + var(--aria)); }
.riempi .crudo-titolo { margin-bottom: calc(5mm + var(--aria)); }
.p-deg.riempi .deg { justify-content: flex-start; }
.p-deg.riempi .deg-sotto { margin-bottom: calc(4mm + var(--aria)); }
.p-deg.riempi .portata { margin-bottom: calc(2.6mm + var(--aria)); }
.p-deg.riempi .portata li { margin-bottom: calc(1.8mm + var(--aria) * .45); }
.p-deg.riempi .deg-nome { margin-top: calc(var(--aria) * .6); }
/* salse/aggiunte a pagamento */
.testo.extra { font-size: 12.5pt; line-height: 1.25; margin-top: 1.4mm; }
.extra-tit { display: block; font-size: 10.5pt; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--oro); margin-bottom: .4mm; }
.extra-tit em { font-weight: 400; letter-spacing: .06em; text-transform: none; color: var(--tenue); }
.extra-nome { font-weight: 600; }
.prezzo.extra { font-size: 13pt !important; font-weight: 600 !important; align-self: end !important; }
.voce .all-riga, .testo.extra .all-riga { color: var(--tenue); font-style: normal; }
.salse-tit { font-size: 11.5pt; font-weight: 600; margin: 0 0 1.6mm; }
.salse-tit em { font-weight: 400; color: var(--tenue); margin-left: 1mm; }
.salse + .salse-en { font-size: 11pt; font-style: italic; color: var(--tenue); margin: 1.4mm 0 3.5mm; }
/* copertina: tutto centrato sulla colonna di testo (da 43,3 a 193 mm), come il resto del menù */
.p-copertina { display: flex; flex-direction: column; }
.copertina { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding-bottom: 10mm; }
.cop-ill { width: 120mm; height: 60mm; margin-bottom: 12mm; }
.cop-ill svg { width: 100%; height: 100%; }
.copertina blockquote { max-width: 130mm; }
.cit { font-size: 25pt; font-style: italic; font-weight: 400; line-height: 1.35; }
.autore { margin-top: 9mm; font-size: 13pt; font-weight: 700; letter-spacing: .32em; text-transform: uppercase; }
.autore::before { content: ""; display: block; width: 18mm; height: .53mm; background: var(--filo-testata); margin: 0 auto 6mm; }
.cit-en { margin-top: 6mm; font-size: 12.5pt; font-style: italic; color: var(--tenue); line-height: 1.3; }
.nome-rist { position: absolute; top: 266mm; left: var(--sx); right: var(--dx); text-align: center;
  font-size: 15pt; font-weight: 600; letter-spacing: .4em; text-transform: uppercase; }
.etichetta { display: block; font-size: 10pt; font-weight: 600; letter-spacing: .22em; text-transform: uppercase;
  color: var(--oro); line-height: 1; margin-bottom: 1.2mm; }
.etichetta::before { content: "✦"; letter-spacing: 0; margin-right: 1.8mm; font-size: 9pt; }
.etichetta em { font-weight: 400; font-style: italic; letter-spacing: .06em; text-transform: none; color: var(--tenue); margin-left: 1mm; }
.nota-pasta p.spiega { font-weight: 700; }
p, h3, h4, li { text-wrap: pretty; }
.fuori-menu { font-size: 11.5pt; font-style: italic; color: var(--oro); margin-top: 2.4mm; line-height: 1.3; max-width: 136mm; }
.fuori-menu em { color: var(--tenue); font-size: 10.5pt; }
.bozza { position: fixed; top: 3mm; left: 6mm; font-size: 8pt; letter-spacing: .2em; color: #a08400; }
"""

RIEMPI_JS = """() => {
  const MM = 96 / 25.4, LIMITE = 270 * MM;   // il contenuto resta sopra i 270 mm (numero di pagina a 282)
  const fondo = p => {
    const top = p.getBoundingClientRect().top; let max = 0;
    p.querySelectorAll('*').forEach(e => {
      if (e.closest('.num') || e.closest('.testata') || e.matches('.deg, .elenco')) return;
      const r = e.getBoundingClientRect(); if (r.height) max = Math.max(max, r.bottom - top);
    });
    return max;
  };
  const esito = [];
  document.querySelectorAll('.pagina.riempi').forEach((p, i) => {
    let lo = 0, hi = 15;
    p.style.setProperty('--aria', '0mm');
    if (fondo(p) <= LIMITE) {
      for (let k = 0; k < 18; k++) {
        const m = (lo + hi) / 2; p.style.setProperty('--aria', m + 'mm');
        if (fondo(p) <= LIMITE) lo = m; else hi = m;
      }
    }
    p.style.setProperty('--aria', lo + 'mm');
    esito.push(Math.round(lo * 10) / 10);
  });
  return esito;
}"""

# Controllo sovrapposizioni: ogni elemento grafico (illustrazioni, filetti, riquadri, frecce,
# etichette a mano) non deve toccare nessun testo né un altro elemento grafico.
SOVRAPPOSIZIONI_JS = """() => {
  const MM = 96 / 25.4, errori = [];
  const box = (r, nome) => ({l: r.left, t: r.top, r: r.right, b: r.bottom, nome});
  const tocca = (a, b) => a.l < b.r - .5 && b.l < a.r - .5 && a.t < b.b - .5 && b.t < a.b - .5;
  document.querySelectorAll('.pagina').forEach((p, ip) => {
    const grafici = [], testi = [];
    p.querySelectorAll('.icona svg, .cop-ill svg, .autore, .nome-rist, .riga, .cottura, .chef, .etichetta, .freccia, .passi .n, .salse li, .num').forEach(e =>
      grafici.push({...box(e.getBoundingClientRect(), e.className.baseVal ?? e.className), el: e}));
    p.querySelectorAll('.elenco').forEach(e => {         // filetto verticale dei prezzi
      const r = e.getBoundingClientRect(), x = r.left + 139.7 * MM;
      grafici.push({l: x, r: x + .53 * MM, t: r.top - MM, b: r.bottom + MM, nome: 'filetto prezzi', el: e});
    });
    p.querySelectorAll('.indice .lista').forEach(e => {     // filetto verticale dell'indice
      const r = e.getBoundingClientRect(), x = r.left + 139.7 * MM;
      grafici.push({l: x, r: x + .53 * MM, t: r.top - 30 * MM, b: r.bottom + 4 * MM, nome: 'filetto indice', el: e});
    });
    p.querySelectorAll('.deg-prezzo').forEach(e => {        // filetti ai lati del prezzo degustazione
      const r = e.getBoundingClientRect();
      [r.left, r.right - .53 * MM].forEach(x => grafici.push({l: x, r: x + .53 * MM, t: r.top, b: r.bottom, nome: 'filetto prezzo', el: null}));
    });
    p.querySelectorAll('.voce.firma .testo').forEach(e => {   // bordi dei riquadri
      const r = e.getBoundingClientRect();
      [[r.left, r.top, r.right, r.top + 1], [r.left, r.bottom - 1, r.right, r.bottom],
       [r.left, r.top, r.left + 1, r.bottom], [r.right - 1, r.top, r.right, r.bottom]]
        .forEach(([l, t, rr, b]) => grafici.push({l, t, r: rr, b, nome: 'bordo riquadro', el: e}));
    });
    const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) {
      const n = w.currentNode; if (!n.textContent.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      [...rg.getClientRects()].forEach(r => testi.push({...box(r, n.textContent.trim().slice(0, 30)), el: n.parentElement}));
    }
    const dentro = (a, b) => a.el && b.el && (a.el.contains(b.el) || b.el.contains(a.el)) && !/filetto/.test(a.nome + b.nome);
    grafici.forEach((g, i) => {
      testi.forEach(tx => { if (!dentro(g, tx) && tocca(g, tx)) errori.push(`pag. ${ip + 1}: ${g.nome} tocca "${tx.nome}"`); });
      grafici.slice(i + 1).forEach(h => { if (!dentro(g, h) && tocca(g, h)) errori.push(`pag. ${ip + 1}: ${g.nome} tocca ${h.nome}`); });
    });
  });
  return errori;
}"""


def documento(pagine, titolo):
    font = (QUI / "fonts.css").read_text()
    bozza = "" if FINALE else '<div class="bozza">BOZZA · in giallo i punti da definire</div>'
    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>{titolo}</title>
<style>{font}{CSS}</style></head><body>{bozza}{''.join(pagine)}</body></html>"""


def main():
    carta = [
        pagina_copertina(),
        *[pagina_degustazione(d, i + 1) for i, d in enumerate(DEGUSTAZIONI)],
        pagina_carta("Antipasti", "Starters", PESCE,
                     "Per iniziare, il mare in piccoli assaggi · <em>To begin, the sea in small bites</em>",
                     elenco(ANTIPASTI) +
                     '<p class="condividi" style="margin-top:8mm">' + FRECCIA +
                     'e per chi ama il crudo… girate pagina: Componi il tuo Crudo</p>',
                     4),
        pagina_crudo(5),
        pagina_primi(6),
        pagina_secondi(7),
        pagina_servizio_allergeni(8),
    ]
    suffisso = "" if FINALE else "_BOZZA"
    lavori = [
        (carta, f"Menu_RistoranteCusin_2026{suffisso}", "Menu Ristorante Cusin 2026"),
        # Ultimo dell'Anno accantonato per ora: per rigenerarlo togliere il commento
        # ([pagina_degustazione(ULTIMO, None)], f"Menu_UltimoDellAnno_2026{suffisso}", "Ultimo dell'Anno 2026"),
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
            print("  a capo sistemati:", pagina_web.evaluate(SISTEMA_A_CAPO_JS))
            aria = pagina_web.evaluate(RIEMPI_JS)
            print("  aria aggiunta (mm) per pagina da riempire:", aria)
            errori = pagina_web.evaluate(SOVRAPPOSIZIONI_JS)
            if errori:
                print("\n".join(errori))
                raise SystemExit(f"STOP {nome}: ci sono sovrapposizioni, PDF non generato")
            # controllo: nessun contenuto deve sforare la pagina
            sfori = pagina_web.evaluate("""() => [...document.querySelectorAll('.pagina')].map((p, i) => {
                const fondo = p.getBoundingClientRect().bottom - 15 * 3.7795;
                const oltre = [...p.querySelectorAll('.testo, .portata, .allergeni, .nota-pasta, .condividi, .passi, .tavolo, .abbina')]
                    .some(e => e.getBoundingClientRect().bottom > fondo);
                return oltre ? i + 1 : null; }).filter(Boolean)""")
            if sfori:
                raise SystemExit(f"STOP {nome}: contenuto oltre il limite di fondo pagina nelle pagine {sfori}")
            pagina_web.pdf(path=str(QUI / f"{nome}.pdf"), format="A4", print_background=True,
                           prefer_css_page_size=True)
            print("creato", nome + ".pdf")
        browser.close()


if __name__ == "__main__":
    main()
