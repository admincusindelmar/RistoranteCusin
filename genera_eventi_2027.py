#!/usr/bin/env python3
"""
Spunti per le serate a tema 2027 (l'ultimo venerdì del mese): due proposte al mese, con il menù.
Stessa grafica del menù d'autunno.

    sorgenti/eventi-2027.html  →  pdf/Serate-a-tema-2027_Proposte.pdf

Uso: python3 genera_eventi_2027.py
"""
import html

from playwright.sync_api import sync_playwright

from genera_cloud import CHROME, QUI, scarica

# (mese, data, nota sulla data, [proposta A, proposta B])
# proposta: (titolo, sottotitolo, gancio, [(portata, piatto)], abbinamento, prezzo)
MESI = [
    ("Gennaio", "Venerdì 29 gennaio", "", [
        ("Livorno d'inverno", "Cacciucco e ponce",
         "La cucina labronica nel mese più freddo: il cacciucco come si fa da noi, e per finire il ponce alla livornese. "
         "Una serata di casa, da raccontare a chi viene da fuori e da ritrovare per chi è di qui.",
         [("Antipasto", "Torta di ceci con baccalà mantecato e cipolla rossa"),
          ("Antipasto", "Triglie alla livornese su crostone di pane toscano"),
          ("Piatto unico", "Il cacciucco di Cusin, con le sue cinque «c»"),
          ("Dolce", "Sfogliatina di mele e il ponce alla livornese")],
         "Rosso della Val di Cornia; ponce al caffè a fine cena", "55"),
        ("Agrumi d'inverno", "Il mare e la luce degli agrumi",
         "Quando fuori è grigio, in tavola arrivano arance, cedri, bergamotto e limoni. "
         "Ogni portata ha il suo agrume: una serata fresca e luminosa nel cuore dell'inverno.",
         [("Antipasto", "Crudo di ricciola, arancia rossa e finocchio"),
          ("Antipasto", "Gamberi al bergamotto con insalata di sedano rapa"),
          ("Primo", "Risotto al limone candito e scampi"),
          ("Secondo", "Spigola al cedro con carciofi croccanti"),
          ("Dolce", "Tarte agli agrumi e meringa bruciata")],
         "Vermentino della costa; un passito per il dolce", "60"),
    ]),
    ("Febbraio", "Venerdì 26 febbraio", "", [
        ("Bollicine e ostriche", "Il crudo incontra lo Champagne",
         "Febbraio è il mese delle ostriche migliori. Una serata dedicata al crudo e alle bollicine, "
         "con un percorso fra Franciacorta e Champagne guidato dal nostro personale di sala.",
         [("Benvenuto", "Ostrica del Doge con perle di limone"),
          ("Antipasto", "Plateau di crudo: scampi, gamberi rossi, tartare di tonno"),
          ("Primo", "Linguine allo Champagne e gamberi rossi"),
          ("Secondo", "Rombo al burro nocciola e crema di topinambur"),
          ("Dolce", "Zabaione allo Champagne con frutti rossi")],
         "Franciacorta con il crudo, Champagne con i piatti caldi", "75"),
        ("Il pesce povero", "Pesce azzurro, grande cucina",
         "Alici, sgombri, sugarelli e palamite: il pesce che il nostro mare dà in abbondanza e che spesso si dimentica. "
         "Una serata buona e sostenibile, con un prezzo più accessibile per avvicinare nuovi clienti.",
         [("Antipasto", "Alici marinate agli agrumi e cipolla di Tropea"),
          ("Antipasto", "Sgombro scottato con salsa verde"),
          ("Primo", "Spaghettoni con palamita, pomodorini e finocchietto"),
          ("Secondo", "Sugarelli in saor con polenta croccante"),
          ("Dolce", "Cantucci e vin santo")],
         "Vermentino o Ansonica; vin santo con il dolce", "45"),
    ]),
    ("Marzo", "Venerdì 26 marzo",
     "È il Venerdì Santo (Pasqua 2027 è il 28 marzo): per tradizione una cena di magro, a base di pesce.", [
        ("Venerdì di magro", "Il baccalà in quattro modi",
         "La cena del Venerdì Santo come si faceva una volta, con il baccalà protagonista. "
         "Un piatto della tradizione livornese, rivisto dalla nostra cucina.",
         [("Antipasto", "Baccalà mantecato su chips di polenta"),
          ("Antipasto", "Frittelle di baccalà e salsa al prezzemolo"),
          ("Primo", "Tortelli di baccalà con crema di ceci"),
          ("Secondo", "Baccalà alla livornese con pomodoro e capperi"),
          ("Dolce", "Schiacciata di Pasqua livornese con crema allo zabaione")],
         "Bianco di struttura, come un Vermentino affinato", "50"),
        ("Primavera dell'orto", "Carciofi, fave e piselli",
         "Le prime verdure della primavera con il pesce: una serata leggera, adatta anche a chi segue il magro, "
         "con un percorso vegetariano a scelta.",
         [("Antipasto", "Carciofi croccanti, seppia e maionese al limone"),
          ("Antipasto", "Crema di piselli con gamberi e menta"),
          ("Primo", "Risotto alle fave e pecorino con scampi crudi"),
          ("Secondo", "Orata con asparagi e salsa al limone"),
          ("Dolce", "Torta di ricotta e fragole")],
         "Vermentino giovane; rosato toscano", "55"),
    ]),
    ("Aprile", "Venerdì 30 aprile",
     "È la vigilia del Primo Maggio: molti hanno il ponte, conviene comunicarla con anticipo.", [
        ("Baccelli e pecorino", "Aspettando il Primo Maggio",
         "In Toscana il Primo Maggio si festeggia con fave fresche e pecorino. "
         "Noi lo anticipiamo di un giorno, con un menù che parte da lì e arriva al mare.",
         [("Benvenuto", "Baccelli e pecorino toscano, come tradizione"),
          ("Antipasto", "Tartare di gamberi, fave e menta"),
          ("Primo", "Pici al ragù di mare e pecorino"),
          ("Secondo", "Trancio di ricciola con piselli e pancetta croccante"),
          ("Dolce", "Crostata di fragole e crema al limone")],
         "Rosato della costa; un bianco toscano giovane", "55"),
        ("Cantina ospite di primavera", "Il ritorno di una serata del vino",
         "Ad aprile 2026 la serata Hofstätter ha aperto la stagione. Per il 2027 proponiamo una cantina "
         "della costa toscana, con il produttore presente in sala a raccontare i suoi vini.",
         [("Antipasto", "Crudo di scampi e asparagi"),
          ("Antipasto", "Calamaro alla brace con crema di piselli"),
          ("Primo", "Risotto agli asparagi e gamberi rossi"),
          ("Secondo", "Dentice al forno con carciofi"),
          ("Dolce", "Piccola pasticceria")],
         "Quattro vini della cantina ospite, uno per portata", "65"),
    ]),
    ("Maggio", "Venerdì 28 maggio", "", [
        ("Tonno rosso", "Dalla testa alla coda",
         "A fine maggio comincia la stagione del tonno rosso. Una serata dedicata a un solo pesce, "
         "usato in ogni sua parte: crudo, scottato, al forno, perfino nel dolce salato del pre-dessert.",
         [("Antipasto", "Tartare di tonno, avocado e sesamo"),
          ("Antipasto", "Ventresca scottata con cipolla in agrodolce"),
          ("Primo", "Spaghetti con bottarga di tonno e limone"),
          ("Secondo", "Filetto di tonno in crosta di pistacchio"),
          ("Dolce", "Semifreddo alle mandorle")],
         "Rosato e un rosso leggero servito fresco", "65"),
        ("Erbe e fiori", "La primavera nel piatto",
         "Erbe aromatiche, fiori eduli e primi ortaggi: una serata colorata e fotogenica, "
         "perfetta da raccontare sui social prima ancora che a tavola.",
         [("Antipasto", "Carpaccio di spigola con fiori e erbe di campo"),
          ("Antipasto", "Fiori di zucca ripieni di ricotta e alici"),
          ("Primo", "Ravioli alle erbe con burro e salvia"),
          ("Secondo", "Rombo al vapore con salsa al basilico"),
          ("Dolce", "Panna cotta alla lavanda e frutti rossi")],
         "Vermentino e un bianco aromatico", "55"),
    ]),
    ("Giugno", "Venerdì 25 giugno", "", [
        ("La notte delle alici", "Il pesce azzurro d'estate",
         "Le alici sono al loro meglio: marinate, fritte, sulla pasta. Una serata semplice e golosa, "
         "da tavolata tra amici, con un prezzo che invoglia a tornare.",
         [("Antipasto", "Alici marinate al limone e pepe rosa"),
          ("Antipasto", "Alici fritte in pastella leggera"),
          ("Primo", "Spaghetti alici, pomodorini e pangrattato"),
          ("Secondo", "Tortino di alici e patate"),
          ("Dolce", "Sorbetto al limone")],
         "Vermentino fresco o bollicine", "45"),
        ("Rosati al tramonto", "La cena dove il sole tramonta sul mare",
         "Il tramonto più lungo dell'anno visto dalla nostra terrazza, con una selezione di rosati italiani e francesi. "
         "La serata più fotografata dell'estate.",
         [("Aperitivo", "Crudo di gamberi rossi e rosato in terrazza"),
          ("Antipasto", "Insalata di polpo, patate e olive taggiasche"),
          ("Primo", "Paccheri con crostacei e pomodorino"),
          ("Secondo", "Ricciola alla griglia con verdure"),
          ("Dolce", "Pesche al vino rosato")],
         "Tre rosati, dal più delicato al più strutturato", "65"),
    ]),
    ("Luglio", "Venerdì 30 luglio", "", [
        ("Gamberi rossi", "Il re del crostaceo",
         "In piena estate, una serata tutta dedicata al gambero rosso: crudo, in bisque, in pasta, alla brace. "
         "Un tema forte, da comunicare con le foto dei piatti.",
         [("Antipasto", "Gambero rosso crudo con burrata e lime"),
          ("Antipasto", "Gambero rosso in tempura di mais"),
          ("Primo", "Linguine al gambero rosso e bisque"),
          ("Secondo", "Gamberi rossi alla brace con salsa al limone"),
          ("Dolce", "Sorbetto all'albicocca")],
         "Bollicine e Vermentino", "70"),
        ("Le isole toscane", "Elba, Capraia e Giglio",
         "Le isole che vediamo dalla terrazza, portate in tavola: i loro vini, l'Aleatico e l'Ansonica, "
         "e i piatti della tradizione isolana.",
         [("Antipasto", "Gurguglione elbano con pesce spada"),
          ("Antipasto", "Totani ripieni all'isolana"),
          ("Primo", "Spaghetti alle cicale di mare"),
          ("Secondo", "Polpo in umido con patate"),
          ("Dolce", "Schiaccia briaca con Aleatico passito")],
         "Ansonica dell'Elba e Aleatico passito", "60"),
    ]),
    ("Agosto", "Venerdì 27 agosto", "", [
        ("Griglia di mare", "Fuoco e terrazza",
         "La griglia accesa all'aperto e il pescato del giorno: una serata conviviale di fine estate, "
         "con la cucina che diventa spettacolo.",
         [("Antipasto", "Crudo del giorno"),
          ("Antipasto", "Spiedini di calamari e gamberi alla brace"),
          ("Primo", "Spaghetti alla brace di pomodoro e alici"),
          ("Secondo", "Grigliata del pescato con verdure"),
          ("Dolce", "Anguria e menta in granita")],
         "Rosato e Vermentino", "60"),
        ("I fichi e il mare", "Il frutto di fine estate",
         "A fine agosto i fichi sono maturi: dolci e salati insieme, accanto al pesce, "
         "con un dolce che li celebra. Un tema insolito che incuriosisce.",
         [("Antipasto", "Fichi, crudo di ricciola e aceto balsamico"),
          ("Antipasto", "Gamberi avvolti nel lardo con fichi caramellati"),
          ("Primo", "Risotto ai fichi e gorgonzola dolce"),
          ("Secondo", "Branzino con fichi e cipolla rossa"),
          ("Dolce", "Crostata di fichi e mandorle")],
         "Un bianco aromatico e un passito per il dolce", "55"),
    ]),
    ("Settembre", "Venerdì 24 settembre", "", [
        ("Mare e bosco", "Porcini e crostacei",
         "Arrivano i primi porcini: li incontriamo con scampi, gamberi e pesce bianco, "
         "in un menù di passaggio fra estate e autunno.",
         [("Antipasto", "Carpaccio di porcini e scampi crudi"),
          ("Antipasto", "Porcini fritti e gamberi croccanti"),
          ("Primo", "Tagliatelle ai porcini e mazzancolle"),
          ("Secondo", "Rana pescatrice con porcini trifolati"),
          ("Dolce", "Torta di castagne e crema al rum")],
         "Un bianco strutturato e un rosso leggero", "65"),
        ("Polpo e moscardini", "I molluschi della nostra costa",
         "Una serata dedicata al polpo, il piatto che a Livorno non manca mai, "
         "cucinato in modi diversi: dall'insalata al ragù.",
         [("Antipasto", "Insalata di polpo, sedano e olive"),
          ("Antipasto", "Moscardini alla diavola su crostone"),
          ("Primo", "Paccheri al ragù di polpo"),
          ("Secondo", "Polpo arrosto con crema di patate affumicate"),
          ("Dolce", "Semifreddo al torrone")],
         "Vermentino e un rosso della costa", "55"),
    ]),
    ("Ottobre", "Venerdì 29 ottobre", "", [
        ("L'uva nel piatto · seconda edizione", "Il ritorno della vendemmia",
         "La serata di ottobre 2026 diventa un appuntamento fisso: l'uva e il vino in ogni portata, "
         "con una cantina diversa ogni anno.",
         [("Antipasto", "Carpaccio di dentice e uva fragola"),
          ("Antipasto", "Gamberi al mosto cotto"),
          ("Primo", "Risotto al vino rosso e radicchio"),
          ("Secondo", "Ricciola al fondo bruno di vino e uva"),
          ("Dolce", "Schiacciata all'uva")],
         "Tre vini della cantina ospite", "60"),
        ("Zucca e mare", "Il colore dell'autunno",
         "La zucca, protagonista dell'autunno, accostata al pesce e ai crostacei: "
         "una serata morbida e calda, da proporre anche alle famiglie.",
         [("Antipasto", "Vellutata di zucca, gamberi e amaretto"),
          ("Antipasto", "Zucca arrosto, baccalà mantecato e semi tostati"),
          ("Primo", "Tortelli di zucca con burro e scampi"),
          ("Secondo", "Rombo con zucca arrosto e salvia"),
          ("Dolce", "Torta di zucca e cannella")],
         "Un bianco morbido e un vino dolce", "55"),
    ]),
    ("Novembre", "Venerdì 26 novembre", "", [
        ("Olio nuovo", "Il frantoio a tavola",
         "Novembre è il mese dell'olio nuovo. Un frantoio toscano ospite e un menù costruito per esaltarlo, "
         "dalla fettunta al dolce all'olio.",
         [("Benvenuto", "Fettunta con olio nuovo"),
          ("Antipasto", "Crudo di spigola e olio nuovo"),
          ("Primo", "Zuppa di ceci e scampi con olio a crudo"),
          ("Secondo", "Baccalà confit all'olio e cavolo nero"),
          ("Dolce", "Torta all'olio e arance")],
         "Un bianco toscano e un rosso giovane", "55"),
        ("Tartufo bianco e mare", "L'incontro più raro",
         "È la stagione del tartufo bianco di San Miniato. Accostarlo al mare è insolito: "
         "per questo funziona, ed è una serata di alto livello.",
         [("Antipasto", "Uovo morbido, crema di patate e tartufo"),
          ("Antipasto", "Carpaccio di scampi e tartufo"),
          ("Primo", "Tagliolini al burro e tartufo bianco"),
          ("Secondo", "Rombo, topinambur e tartufo"),
          ("Dolce", "Zabaione caldo")],
         "Un rosso importante e un bianco affinato", "85"),
    ]),
    ("Dicembre", "Venerdì 17 dicembre",
     "L'ultimo venerdì è il 31 dicembre, che ha già il menù dell'Ultimo dell'Anno. "
     "Per la serata di dicembre proponiamo un altro venerdì: il 17, prima di Natale.", [
        ("La cena degli auguri", "Brindisi prima delle feste",
         "Una cena prima delle feste, per farsi gli auguri con amici e colleghi: "
         "anche per tavolate aziendali, con il panettone artigianale a chiudere.",
         [("Antipasto", "Insalata di mare tiepida e agrumi"),
          ("Antipasto", "Polpettine di pesce e salsa allo zafferano"),
          ("Primo", "Risotto agli scampi e Champagne"),
          ("Secondo", "Branzino in crosta di sale"),
          ("Dolce", "Panettone artigianale con crema al mascarpone")],
         "Bollicine per il brindisi", "55"),
        ("Ostriche e Champagne", "Le feste cominciano qui",
         "In alternativa, una serata elegante per aprire le feste: "
         "ostriche, crudo e un Champagne diverso per ogni portata.",
         [("Benvenuto", "Ostriche di tre provenienze"),
          ("Antipasto", "Crudo di scampi e caviale"),
          ("Primo", "Tagliolini allo Champagne e gamberi rossi"),
          ("Secondo", "Astice alla catalana"),
          ("Dolce", "Piccola pasticceria")],
         "Tre Champagne, uno per portata", "95"),
    ]),
]

ANNO_2026 = [("Aprile", "Hofstätter"), ("Maggio", "Crudité"), ("Giugno", "Levii"), ("Luglio", "Riso Maremma"),
             ("Agosto", "Panettone"), ("Settembre", "Benedetto Cavalieri"), ("Ottobre", "L'uva nel piatto"),
             ("Novembre", "Castagne")]


def e(t):
    return html.escape(t)


def proposta(lettera, p):
    titolo, sotto, gancio, menu, vino, prezzo = p
    righe = "".join(f'<div class="piatto"><span class="portata">{e(a)}</span><span class="nome">{e(b)}</span></div>' for a, b in menu)
    return f"""<div class="proposta">
  <p class="lettera">Proposta {lettera}</p>
  <h2>{e(titolo)}</h2>
  <p class="sotto-p">{e(sotto)}</p>
  <p class="gancio">{e(gancio)}</p>
  <div class="menu">{righe}</div>
  <div class="chiusa"><p class="vino"><b>Nel bicchiere</b> · {e(vino)}</p><p class="prezzo"><b>{prezzo}</b> € <span>a persona</span></p></div>
</div>"""


def documento():
    pagine = []
    pagine.append("""<section class="pag copertina">
  <img class="mono" src="cusin-monogramma-blu.png" alt="Cusin">
  <p class="eti">Proposte per il 2027</p>
  <h1>Le serate a tema</h1>
  <p class="sotto">L'ultimo venerdì di ogni mese, due idee e il loro menù</p>
  <div class="filetto"></div>
  <p class="intro">Nel 2026 le serate a tema hanno raccontato vini, produttori e ingredienti: da Hofstätter a Benedetto Cavalieri,
  dal riso di Maremma all'uva nel piatto. Per il 2027 le portiamo a dodici mesi, sempre l'ultimo venerdì,
  con due proposte per ogni mese da cui scegliere. I menù sono spunti per la cucina: piatti, prezzi e abbinamenti
  si definiscono con lo Chef prima di comunicare la serata.</p>
  <div class="piede"><span>Cusin · Serate a tema 2027</span><span></span></div>
</section>""")
    cal = "".join(f'<div class="cal-r"><span class="m">{e(m)}</span><span class="d">{e(d)}</span>'
                  f'<span class="t">{e(p[0][0])} <i>oppure</i> {e(p[1][0])}</span></div>' for m, d, _, p in MESI)
    passato = " · ".join(f"{e(m)} <b>{e(t)}</b>" for m, t in ANNO_2026)
    pagine.append(f"""<section class="pag">
  <div class="testa"><img src="cusin-monogramma-blu.png" alt="Cusin"><p class="eti">Il calendario</p><h1 class="h1p">Dodici venerdì</h1></div>
  <div class="cal">{cal}</div>
  <div class="nota-box"><p class="eti-mini">Da ricordare</p>
    <p>26 marzo è il <b>Venerdì Santo</b>: la serata diventa una cena di magro.</p>
    <p>30 aprile è la <b>vigilia del Primo Maggio</b>: molti hanno il ponte, va comunicata presto.</p>
    <p>31 dicembre è l'<b>Ultimo dell'Anno</b>, che ha il suo menù: la serata di dicembre si sposta al 17.</p></div>
  <div class="nota-box"><p class="eti-mini">Il 2026</p><p class="passato">{passato}</p></div>
  <div class="piede"><span>Cusin · Serate a tema 2027</span><span></span></div>
</section>""")
    for mese, data, nota, (a, b) in MESI:
        n = f'<p class="nota-data">{e(nota)}</p>' if nota else ""
        pagine.append(f"""<section class="pag mese">
  <div class="testa-mese"><img src="cusin-monogramma-blu.png" alt="Cusin"><div><h1 class="h1p">{e(mese)}</h1><p class="data">{e(data)}</p></div></div>
  {n}
  <div class="due">{proposta("A", a)}{proposta("B", b)}</div>
  <div class="piede"><span>Cusin · Serate a tema 2027</span><span>{e(mese)}</span></div>
</section>""")
    pagine.append("""<section class="pag">
  <div class="testa"><img src="cusin-monogramma-blu.png" alt="Cusin"><p class="eti">Per ogni serata</p><h1 class="h1p">Come lavorarle</h1></div>
  <div class="passi">
    <div><h3>Sei settimane prima</h3><p>Scegliere la proposta, definire il menù con lo Chef e, se c'è, confermare la cantina o il produttore ospite.</p></div>
    <div><h3>Tre settimane prima</h3><p>Preparare il menù della serata con la grafica del menù, la locandina e i testi per WhatsApp, mail e social.</p></div>
    <div><h3>Due settimane prima</h3><p>Primo messaggio WhatsApp e mail. Si prenota rispondendo al messaggio o con il pulsante «Prenota ora».</p></div>
    <div><h3>Una settimana prima</h3><p>Promemoria a chi non ha risposto, con i posti che restano. Un ultimo messaggio il giorno prima, se ci sono posti.</p></div>
    <div><h3>Dopo la serata</h3><p>Foto dei piatti sui social e un grazie a chi è venuto, con la data della serata del mese dopo.</p></div>
  </div>
  <div class="nota-box"><p class="eti-mini">Prezzi</p><p>I prezzi indicati sono di riferimento, con i vini in abbinamento da decidere caso per caso. Li stabilisce Gioacchino.</p></div>
  <div class="piede"><span>Cusin · Serate a tema 2027</span><span></span></div>
</section>""")
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><title>Cusin · Serate a tema 2027</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&display=swap">
<style>{CSS}</style></head><body>
{''.join(pagine)}
</body></html>"""


CSS = """
:root { --blu:#152b61; --champagne:#d6c6a5; --avorio:#f4ede2; --secondario:#675e53; --filetto:rgba(21,43,97,.25); }
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Cormorant Garamond", Garamond, serif; font-weight: 500; font-variant-numeric: lining-nums; color: var(--blu); }
.pag { width: 210mm; height: 297mm; padding: 14mm 18mm 11mm; display: flex; flex-direction: column; break-after: page; background: var(--avorio); }
.pag:last-child { break-after: auto; }
.piede { margin-top: auto; display: flex; justify-content: space-between; font-size: 10.5px; letter-spacing: .24em; text-transform: uppercase; color: var(--secondario); border-top: 1px solid var(--filetto); padding-top: 3mm; }
.eti { font-size: 12.5px; font-weight: 600; letter-spacing: .28em; text-transform: uppercase; }
.eti-mini { font-size: 11px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; margin-bottom: 1.5mm; }
/* copertina */
.copertina { align-items: center; text-align: center; justify-content: center; }
.copertina .mono { height: 38mm; margin: 30mm 0 12mm; }
.copertina h1 { font-weight: 500; font-size: 54px; line-height: 1; margin-top: 5mm; }
.copertina .sotto { font-style: italic; font-size: 21px; margin-top: 4mm; }
.filetto { width: 60px; height: 1px; background: var(--champagne); margin: 10mm auto; }
.intro { font-size: 17px; line-height: 1.5; max-width: 140mm; text-align: center; color: var(--blu); margin-bottom: 20mm; }
/* testate */
.testa { text-align: center; }
.testa img { height: 9mm; display: block; margin: 0 auto 4mm; }
.h1p { font-weight: 500; font-size: 38px; line-height: 1.05; margin-top: 2mm; }
.testa-mese { display: flex; align-items: center; gap: 6mm; border-bottom: 1px solid var(--champagne); padding-bottom: 4mm; }
.testa-mese img { height: 13mm; }
.data { font-style: italic; font-size: 19px; color: var(--secondario); }
.nota-data { font-style: italic; font-size: 15px; background: #ebe2d3; padding: 2mm 3mm; margin-top: 3mm; }
/* calendario */
.cal { margin-top: 8mm; }
.cal-r { display: grid; grid-template-columns: 30mm 46mm 1fr; align-items: baseline; padding: 2.1mm 0; border-bottom: 1px solid var(--filetto); }
.cal-r .m { font-size: 12px; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
.cal-r .d { font-size: 16px; font-style: italic; color: var(--secondario); }
.cal-r .t { font-size: 16.5px; font-weight: 600; }
.cal-r .t i { font-weight: 500; color: var(--secondario); }
.nota-box { margin-top: 7mm; font-size: 15px; line-height: 1.45; }
.passato { font-size: 15px; }
.passato b { font-weight: 600; }
/* mese */
.due { display: flex; flex-direction: column; gap: 5mm; margin-top: 5mm; flex: 1; }
.proposta { flex: 1; border-left: 1px solid var(--champagne); padding-left: 5mm; display: flex; flex-direction: column; }
.lettera { font-size: 11px; font-weight: 700; letter-spacing: .24em; text-transform: uppercase; color: var(--secondario); }
.proposta h2 { font-weight: 600; font-size: 25px; line-height: 1.1; margin-top: 1mm; }
.sotto-p { font-style: italic; font-size: 16.5px; color: var(--secondario); }
.gancio { font-size: 15px; line-height: 1.42; margin-top: 2mm; }
.menu { margin-top: 3mm; }
.piatto { display: grid; grid-template-columns: 27mm 1fr; padding: .9mm 0; border-bottom: 1px solid var(--filetto); }
.portata { font-size: 10.5px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; padding-top: 1mm; }
.nome { font-size: 16.5px; }
.chiusa { display: flex; justify-content: space-between; align-items: baseline; margin-top: 2.5mm; }
.vino { font-size: 14.5px; font-style: italic; color: var(--secondario); }
.vino b { font-style: normal; font-weight: 700; font-size: 10.5px; letter-spacing: .16em; text-transform: uppercase; color: var(--blu); }
.prezzo { font-size: 15px; white-space: nowrap; }
.prezzo b { font-size: 28px; font-weight: 500; }
.prezzo span { font-size: 10.5px; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; }
/* come lavorarle */
.passi { margin-top: 8mm; display: flex; flex-direction: column; gap: 5mm; }
.passi h3 { font-size: 13px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }
.passi p { font-size: 16.5px; line-height: 1.45; }
"""


def main():
    f = QUI / "sorgenti" / "eventi-2027.html"
    f.write_text(documento(), encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.route("https://fonts.googleapis.com/**", scarica)
        pg.route("https://fonts.gstatic.com/**", scarica)
        pg.goto(f.as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        # nessuna pagina deve sbordare
        sborda = pg.evaluate("[...document.querySelectorAll('.pag')].map((p,i)=>[i+1,p.scrollHeight>p.clientHeight+1]).filter(x=>x[1]).map(x=>x[0])")
        if sborda:
            print("ATTENZIONE: pagine che sbordano", sborda)
        pg.pdf(path=str(QUI / "pdf" / "Serate-a-tema-2027_Proposte.pdf"), prefer_css_page_size=True, print_background=True)
        b.close()
    print("creato pdf/Serate-a-tema-2027_Proposte.pdf")


if __name__ == "__main__":
    main()
