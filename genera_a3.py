#!/usr/bin/env python3
"""
Genera il menù A3 orizzontale, solo fronte e solo in italiano, con la stessa grafica del menù A4.
Per le altre lingue c'è il QR code in alto a destra.

I piatti, i prezzi e gli allergeni si leggono da sorgenti/menu.html: l'A3 non si modifica a mano,
si corregge il menù A4 e si rilancia questo script.

    pdf/Menu-Autunno-2026_A3_Stampa.pdf    senza fondo, per la carta avorio
    pdf/Menu-Autunno-2026_A3_Schermo.pdf   avorio simulato, per vederlo a video

Uso: python3 genera_a3.py   (serve la connessione per i caratteri di Google Fonts)
"""
import json
import os
from functools import lru_cache

from playwright.sync_api import sync_playwright

from genera_cloud import CHROME, QUI, scarica

SORGENTE = QUI / "sorgenti" / "menu.html"
HTML_A3 = QUI / "sorgenti" / "menu-a3.generato.html"     # generato: non modificarlo a mano

# Legge dal menù A4 i dati che servono all'A3, togliendo tutto l'inglese.
LEGGI_JS = r"""() => {
  const it = s => s.replace(/\s+/g, ' ').trim();
  const allergeni = el => {
    if (!el) return '';
    const c = el.cloneNode(true);
    c.querySelectorAll('.dieta').forEach(d => d.remove());
    return it(c.textContent).replace('Allergeni/Allergens', '').replace('tracce/traces', 'tracce')
      .replace('nessuno · none', '').trim();
  };
  const diete = el => el ? [...el.querySelectorAll('.dieta')].map(d => it(d.textContent).split('/')[0]) : [];
  const nome = h2 => {
    const c = h2.cloneNode(true);
    const cottura = !!c.querySelector('.cottura');
    c.querySelectorAll('.cottura').forEach(x => x.remove());
    const pz = c.querySelector('.pz'); const unita = pz ? it(pz.textContent) : '';
    if (pz) pz.remove();
    return {nome: it(c.innerHTML), cottura, unita};
  };
  const etichetta = eti => it([...eti.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(''));
  const desc = el => el ? it(el.innerHTML) : '';

  const deg = [...document.querySelectorAll('section.deg')].map(s => ({
    nome: it(s.querySelector('h1').textContent),
    sotto: it(s.querySelector('.sotto').textContent),
    prezzo: it(s.querySelector('.prezzo-deg b').textContent),
    portate: [...s.querySelectorAll('.sez')].map(z => ({
      nome: etichetta(z.querySelector('.eti')),
      piatti: [...z.querySelectorAll('.voce')].map(v => Object.assign(nome(v.querySelector('h2')), {
        desc: desc(v.querySelector('.desc')), all: allergeni(v.querySelector('.all')), diete: diete(v.querySelector('.all'))}))
    }))
  }));

  const carta = [...document.querySelectorAll('section.carta')].map(s => {
    const voci = [];
    for (const el of s.querySelector('.corpo').children) {
      if (el.classList.contains('riga')) {
        const h2 = el.querySelector('.voce h2');
        const prezzo = it(el.querySelector('.prezzo').textContent);
        if (h2) {
          const v = el.querySelector('.voce');
          voci.push(Object.assign(nome(h2), {tipo: 'piatto', prezzo, chef: v.classList.contains('chefbox'),
            breve: v.classList.contains('breve'), desc: desc(v.querySelector('.desc')),
            all: allergeni(v.querySelector('.all')), diete: diete(v.querySelector('.all'))}));
        } else {                                   // salsa in aggiunta
          const b = el.querySelector('b');
          voci.push({tipo: 'aggiunta', nome: it(b.textContent), prezzo, all: allergeni(el.querySelector('.all-in'))});
        }
      } else if (el.classList.contains('sottosez')) {
        voci.push({tipo: 'passo', num: it(el.querySelector('.num').textContent), nome: etichetta(el)});
      } else if (el.classList.contains('eti-mini')) {
        voci.push({tipo: 'mini', nome: etichetta(el)});
      } else if (el.querySelector && el.querySelector('.salse')) {
        voci.push({tipo: 'incluse', salse: [...el.querySelectorAll('.salse > span')].map(x => it(x.textContent)),
          all: allergeni(el.querySelector('.all'))});
      } else if (el.classList.contains('nota')) {
        const c = el.cloneNode(true); c.querySelectorAll('.tr-in').forEach(x => x.remove());
        voci.push({tipo: 'nota', testo: it(c.innerHTML).replace(/\s*·\s*$/, '')});
      } else if (el.classList.contains('box-nota')) {
        voci.push({tipo: 'nota', testo: desc(el.querySelector('.desc'))});
      } else if (el.classList.contains('tab')) {
        voci.push({tipo: 'tabella', righe: [...el.querySelectorAll('.n')].map(n => {
          const c = n.cloneNode(true); const i = c.querySelector('i');
          const all = allergeni(i && i.querySelector('.all-in')); if (i) i.remove();
          const u = c.querySelector('.unita'); const unita = u ? it(u.textContent) : ''; if (u) u.remove();
          return {nome: it(c.innerHTML), unita, all, prezzo: it(n.nextElementSibling.textContent)};
        })});
      } else if (el.classList.contains('eti') && el.classList.contains('sezione')) {
        voci.push({tipo: 'sezione', nome: etichetta(el)});
      } else if (el.classList.contains('desc')) {
        voci.push({tipo: 'nota', testo: it(el.innerHTML)});
      }
    }
    return {titolo: it(s.querySelector('h1').textContent), voci};
  });
  return {deg, carta};
}"""


def al(a):
    return f' <span class="al">{a}</span>' if a else ""


def dieta(d):
    return "".join(f' <span class="dieta">{x}</span>' for x in d)


def piatto(v):
    chef = '<p class="chef">Il consiglio dello Chef</p>' if v.get("chef") else ""
    cott = ' <span class="cottura">18 minuti di cottura</span>' if v.get("cottura") else ""
    unita = f' <span class="unita">{v["unita"]}</span>' if v.get("unita") else ""
    desc = f'<p class="desc">{v["desc"]}{al(v["all"])}{dieta(v["diete"])}</p>' if v.get("desc") else ""
    coda = ""
    if not v.get("desc"):                          # voci brevi del crudo: allergeni sulla riga del nome
        coda = al(v["all"]) + dieta(v["diete"])
    return (f'<div class="v{" firma" if chef else ""}"><div class="tx">{chef}<h4>{v["nome"]}{unita}{cott}{coda}</h4>{desc}</div>'
            f'<div class="pr">{v["prezzo"]}</div></div>')


def blocchi_sezione(titolo, voci):
    """Una sezione della carta divisa in blocchi: può continuare nella colonna dopo, ma solo fra un piatto e l'altro."""
    pezzi = []
    for v in voci:
        t = v["tipo"]
        if t == "piatto":
            pezzi.append(piatto(v))
        elif t == "aggiunta":
            pezzi.append(f'<div class="v aggiunta"><div class="tx">+ {v["nome"].lstrip("+ ")}{al(v["all"])}</div><div class="pr">{v["prezzo"]}</div></div>')
        elif t == "passo":
            pezzi.append(f'<p class="passo"><span class="num">{v["num"]}</span> {v["nome"]}</p>')
        elif t == "mini":
            pezzi.append(f'<p class="mini">{v["nome"]}</p>')
        elif t == "incluse":
            pezzi.append(f'<p class="desc incluse">{" e ".join(v["salse"])}{al(v["all"])}</p>')
        elif t == "nota":
            pezzi.append(f'<p class="nota">{v["testo"]}</p>')
        elif t == "sezione":
            pezzi.append(f'<h2 class="sez-tit sotto-tit">{v["nome"].capitalize()}</h2>')
        elif t == "tabella":
            for r in v["righe"]:
                u = f' <span class="unita">{r["unita"]}</span>' if r["unita"] else ""
                pezzi.append(f'<div class="v corta"><div class="tx"><h4>{r["nome"]}{u}{al(r["all"])}</h4></div><div class="pr">{r["prezzo"]}</div></div>')
    # «Da aggiungere» e il numero del passo restano attaccati al primo piatto che segue
    uniti, attesa = [], ""
    for p in pezzi:
        if p.startswith(('<p class="passo"', '<p class="mini"', '<h2 class="sez-tit')):
            attesa += p
        else:
            uniti.append(attesa + p)
            attesa = ""
    if attesa:
        uniti.append(attesa)
    out = [(f'<h2 class="sez-tit">{titolo}</h2>' + uniti[0], titolo, False)]
    out += [(u, titolo, True) for u in uniti[1:]]
    out[-1] = (out[-1][0] + '<div class="fine-sez"></div>', titolo, out[-1][2])
    return out


def voce_deg(v):
    """Se la descrizione comincia già col nome del piatto basta quella, altrimenti nome e descrizione."""
    import re
    parola = lambda x: re.sub(r"<[^>]+>", "", x).split()[0].lower()
    return v["desc"] if parola(v["nome"]) == parola(v["desc"]) else f'<b>{v["nome"]}</b> · {v["desc"]}'


def degustazione(d):
    portate = ""
    for p in d["portate"]:
        voci = "".join(f'<li>{voce_deg(v)}{al(v["all"])}</li>' for v in p["piatti"])
        portate += f'<div class="portata"><h5>{p["nome"]}</h5><ul>{voci}</ul></div>'
    return (f'<section class="deg"><div class="deg-testa"><div><h3>{d["nome"]}</h3><p class="deg-sotto">{d["sotto"]}</p></div>'
            f'<div class="deg-prezzo"><b>{d["prezzo"]}</b><span>a persona</span></div></div>{portate}</section>')


SERVIZIO_LEGENDA = """<p class="legenda"><b>Allergeni</b> 1 glutine · 2 crostacei · 3 uova · 4 pesce · 5 arachidi · 6 soia ·
  7 latte e lattosio · 8 frutta a guscio · 9 sedano · 10 senape · 11 sesamo · 12 solfiti · 13 lupini · 14 molluschi</p>
<p class="legale">I numeri accanto ai piatti indicano le sostanze che possono causare allergie o intolleranze (<span class="nb">Reg. UE 1169/2011</span>); «tracce» indica allergeni che possono essere presenti in tracce. Per qualsiasi esigenza alimentare rivolgetevi al nostro personale. Il pesce servito crudo è sottoposto ad abbattimento (<span class="nb">Reg. CE 853/2004</span>).</p>"""


def documento(dati, colonne, servizio):
    def colonna(c):
        h = "".join(f'<div class="blocco">{x}</div>' for x, _, _ in c)
        if c and c[0][2]:
            h = f'<p class="segue">{c[0][1]} <em>segue</em></p>' + h
        return f'<div class="col">{h}</div>'
    serv = "".join(f'<span>{r["nome"]}{" <i>" + r["unita"] + "</i>" if r["unita"] else ""} <b>{r["prezzo"]}</b></span>' for r in servizio)
    return f"""<!doctype html>
<!-- GENERATO da genera_a3.py a partire da menu.html: non modificarlo a mano -->
<html lang="it"><head><meta charset="utf-8"><title>Cusin · Menù A3 Autunno 2026</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&display=swap">
<style>{CSS}</style>
<script>if (location.search.indexOf('schermo') >= 0) document.documentElement.classList.add('schermo');</script>
</head><body>
<main class="foglio">
  <header class="testa">
    <div></div>
    <div class="nome"><img src="cusin-monogramma-blu.png" alt="Cusin"><div><h1>CUSIN</h1><p>La Carta · Autunno 2026</p></div></div>
    <div class="qr"><img src="qr-menu-lingue.png" alt="QR code"><div><p class="qr-it">Il menù nella vostra lingua</p><p>Menu in English · Deutsch · Français · Español</p></div></div>
  </header>
  <p class="eti fascia">Le Degustazioni</p>
  <div class="tre">{"".join(degustazione(d) for d in dati["deg"])}</div>
  <p class="nota-deg">I menù degustazione sono serviti per l'<span class="nb">intero tavolo</span> · Chiedete al nostro personale l'abbinamento al calice dalla <span class="nb">Carta dei Vini</span></p>
  <p class="eti fascia">La Carta</p>
  <div class="colonne" style="grid-template-columns: repeat({len(colonne)}, 1fr)">{"".join(colonna(c) for c in colonne)}</div>
  <footer class="piede-a3">
    <p class="servizio"><b>Servizio</b>{serv}</p>
    {SERVIZIO_LEGENDA}
    <div class="piede"><span>Cusin · Autunno 2026</span></div>
  </footer>
</main></body></html>"""


CSS = """
:root { --blu: #152b61; --champagne: #d6c6a5; --avorio: #f4ede2; --secondario: #675e53; --filetto: rgba(21, 43, 97, 0.25);
  --display: "Cormorant Garamond", Garamond, serif; }
@page { size: A3 landscape; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: var(--display); font-weight: 500; font-variant-numeric: lining-nums; color: var(--blu); background: #fff;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html.schermo body, html.schermo .foglio { background: var(--avorio); }
.nb { white-space: nowrap; }
p, li, h4 { text-wrap: pretty; }
.foglio { width: 420mm; height: 297mm; padding: 10mm 14mm 8mm; display: flex; flex-direction: column; overflow: hidden; }

/* Testata: monogramma e nome al centro, QR code a destra */
.testa { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; padding-bottom: 3mm; }
.testa .nome { display: flex; align-items: center; gap: 6mm; }
.testa .nome img { height: 17mm; display: block; }
.testa h1 { font-weight: 500; font-size: 30pt; letter-spacing: .5em; margin-right: -.5em; line-height: 1; }
.testa .nome p { font-size: 9.5pt; font-weight: 600; letter-spacing: .24em; text-transform: uppercase; margin-top: 2mm; }
.qr { justify-self: end; display: flex; align-items: center; gap: 3mm; }
.qr img { width: 19mm; height: 19mm; display: block; image-rendering: pixelated; }
.qr p { font-size: 10pt; color: var(--secondario); }
.qr .qr-it { font-style: italic; font-size: 14pt; color: var(--blu); }

/* Etichette di fascia con i filetti champagne ai lati, come nelle degustazioni dell'A4 */
.eti { font-size: 10.5pt; font-weight: 600; letter-spacing: .3em; text-transform: uppercase; }
.eti.fascia { display: flex; align-items: center; gap: 4mm; margin: 0 0 2.5mm; }
.eti.fascia::before, .eti.fascia::after { content: ""; flex: 1; height: 1px; background: var(--champagne); }

/* Degustazioni in alto, una accanto all'altra */
.tre { display: grid; grid-template-columns: 1.35fr 1fr 1fr; column-gap: 9mm; }
.deg + .deg { border-left: 1px solid var(--filetto); margin-left: -4.5mm; padding-left: 4.5mm; }
.deg-testa { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5mm; }
.deg h3 { font-weight: 500; font-size: 19pt; line-height: 1; }
.deg-sotto { font-style: italic; font-size: 10.5pt; color: var(--secondario); margin-top: .8mm; }
.deg-prezzo { display: flex; align-items: baseline; gap: 2mm; }
.deg-prezzo b { font-weight: 500; font-size: 22pt; line-height: 1; }
.deg-prezzo span { font-size: 8pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; }
.portata { display: grid; grid-template-columns: 19mm 1fr; column-gap: 2mm; margin-top: 1mm; }
.portata h5 { font-size: 7.5pt; font-weight: 600; letter-spacing: .18em; text-transform: uppercase; padding-top: .9mm; }
.portata ul { list-style: none; }
.portata li { font-size: 10.5pt; line-height: 1.22; margin-bottom: .5mm; }
.portata li b { font-weight: 600; }
.nota-deg { text-align: center; font-size: 10pt; color: var(--secondario); margin: 1.5mm 0 3.5mm; }

/* La carta in colonne */
.colonne { flex: 1; min-height: 0; display: grid; column-gap: 8mm; }
.col { min-height: 0; }
.col + .col { border-left: 1px solid var(--filetto); margin-left: -4mm; padding-left: 4mm; }
.sez-tit { font-weight: 500; font-size: 17pt; line-height: 1.1; display: flex; align-items: baseline; gap: 3mm; margin-bottom: 2mm; }
.sez-tit::after { content: ""; flex: 1; height: 1px; background: var(--champagne); align-self: center; }
.sotto-tit { font-size: 13pt; margin-top: 2.5mm; }
.fine-sez { height: 4mm; }
.segue { font-size: 8pt; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--secondario); margin-bottom: 1.5mm; }
.segue em { font-style: italic; text-transform: none; letter-spacing: 0; font-size: 10pt; font-weight: 500; }
.v { display: grid; grid-template-columns: 1fr 11mm; column-gap: 2mm; margin-bottom: 1.6mm; break-inside: avoid; }
.v h4 { font-weight: 600; font-size: 12pt; line-height: 1.15; }
.v .pr { font-weight: 600; font-size: 12pt; line-height: 1.15; text-align: right; }
.v.firma .tx { border-left: 1px solid var(--champagne); padding-left: 3mm; margin-left: calc(-3mm - 1px); }
.chef { font-size: 7.5pt; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; display: flex; align-items: center; gap: 1.5mm; margin-bottom: .3mm; }
.chef::before { content: ""; width: 5mm; height: 1px; background: var(--champagne); }
.desc { font-size: 10.5pt; line-height: 1.2; margin-top: .2mm; }
.al { color: var(--secondario); font-size: 9.5pt; white-space: nowrap; margin-left: 1mm; }
.al::before { content: "· "; }
.desc > .al:first-child { margin-left: 0; }
.desc > .al:first-child::before { content: none; }
.dieta { font-size: 9.5pt; font-weight: 700; white-space: nowrap; margin-left: 1.5mm; }
.cottura { display: inline-block; font-size: 6.5pt; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
  border: 1px solid var(--champagne); padding: .2mm 1.4mm; margin-left: 1.5mm; vertical-align: 1.5pt; white-space: nowrap; }
.unita { font-style: italic; font-size: 10.5pt; font-weight: 500; color: var(--secondario); margin-left: 1mm; }
.v.aggiunta { margin-top: -.6mm; }
.v.aggiunta .tx, .v.aggiunta .pr { font-size: 10.5pt; }
.v.aggiunta .tx { font-weight: 600; }
.v.corta { margin-bottom: 1mm; }
.passo { font-size: 8.5pt; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; margin: 1.5mm 0 1.2mm; }
.passo .num { font-size: 13pt; letter-spacing: 0; margin-right: .8mm; }
.mini { font-size: 7.5pt; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; margin: .6mm 0 .8mm; }
.incluse { margin-bottom: 1.4mm; }
.nota { font-size: 10pt; line-height: 1.2; color: var(--secondario); margin: .4mm 0 1.6mm; }

/* Piede: servizio, legenda degli allergeni, note di legge */
.piede-a3 { border-top: 1px solid var(--filetto); padding-top: 2mm; margin-top: 2mm; text-align: center; }
.servizio { font-size: 11.5pt; }
.servizio > b { font-size: 9pt; font-weight: 700; letter-spacing: .24em; text-transform: uppercase; margin-right: 4mm; }
.servizio span { margin: 0 4mm; white-space: nowrap; }
.servizio span i { color: var(--secondario); font-size: 10pt; }
.servizio span b { font-weight: 600; margin-left: 1.5mm; }
.legenda { font-size: 9.5pt; color: var(--secondario); margin-top: 1.2mm; }
.legenda b { font-size: 7.5pt; letter-spacing: .2em; text-transform: uppercase; color: var(--blu); margin-right: 2mm; }
.legale { font-size: 8.5pt; color: var(--secondario); margin-top: .6mm; }
.piede { font-size: 7.5pt; letter-spacing: .24em; text-transform: uppercase; color: var(--secondario); margin-top: 1.4mm; }
"""

MISURA_JS = """() => {
  const MM = 96 / 25.4, col = document.querySelector('.col');  // un figlio .blocco per blocco
  const disponibile = document.querySelector('.colonne').getBoundingClientRect().height / MM;
  const r = [...col.children].map(e => e.getBoundingClientRect());
  // altezza di ogni blocco come distanza fra l'inizio del blocco e l'inizio del successivo (comprende i margini)
  const altezze = r.map((x, i) => ((i + 1 < r.length ? r[i + 1].top : col.getBoundingClientRect().top + col.scrollHeight) - x.top) / MM);
  return {altezze, disponibile};
}"""


def dividi(altezze, n, extra):
    """Divide i blocchi, in ordine, in n colonne contigue riducendo al minimo la colonna più alta."""
    pref = [0]
    for h in altezze:
        pref.append(pref[-1] + h)

    @lru_cache(None)
    def migliore(i, k):
        if k == 1:
            return pref[-1] - pref[i] + extra[i], (len(altezze),)
        best = (float("inf"), ())
        for j in range(i + 1, len(altezze) - k + 2):
            resto, tagli = migliore(j, k - 1)
            alto = max(pref[j] - pref[i] + extra[i], resto)
            if alto < best[0]:
                best = (alto, (j,) + tagli)
        return best

    alto, tagli = migliore(0, n)
    inizio, gruppi = 0, []
    for fine in tagli:
        gruppi.append(list(range(inizio, fine)))
        inizio = fine
    return alto, gruppi


def apri(pg, url):
    pg.route("https://fonts.googleapis.com/**", scarica)
    pg.route("https://fonts.gstatic.com/**", scarica)
    pg.goto(url)
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    if not pg.evaluate("[...document.fonts].filter(f => f.status == 'loaded').length"):
        raise SystemExit("STOP: i caratteri di Google Fonts non si sono caricati")


def main(n_colonne=5):
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None)
        pg = b.new_page()
        apri(pg, SORGENTE.as_uri())
        dati = pg.evaluate(LEGGI_JS)
        (QUI / "pdf").mkdir(exist_ok=True)
        carta = {s["titolo"]: s["voci"] for s in dati["carta"]}
        contorni = carta.pop("Contorni")
        # dalla pagina dei contorni: i contorni e i dolci vanno nella carta, il servizio nel piede
        i_serv = next(i for i, v in enumerate(contorni) if v["tipo"] == "sezione" and v["nome"] == "Servizio")
        servizio = contorni[i_serv + 1]["righe"]
        contorni = contorni[:i_serv]
        crudo = [v for v in carta.pop("Componete il vostro Crudo")]
        tutti = (blocchi_sezione("Antipasti", carta["Antipasti"]) + blocchi_sezione("Il Crudo", crudo) +
                 blocchi_sezione("Primi piatti", carta["Primi piatti"]) + blocchi_sezione("Secondi piatti", carta["Secondi piatti"]) +
                 blocchi_sezione("Contorni", contorni))
        # 1) misura ogni blocco alla larghezza di una colonna
        HTML_A3.write_text(documento(dati, [tutti] + [[] for _ in range(n_colonne - 1)], servizio), encoding="utf-8")
        apri(pg, HTML_A3.as_uri())
        m = pg.evaluate(MISURA_JS)
        extra = [5 if cont else 0 for _, _, cont in tutti]
        alto, gruppi = dividi(m["altezze"], n_colonne, extra)
        print(f"colonna più alta {alto:.0f} mm su {m['disponibile']:.0f} mm disponibili")
        if alto > m["disponibile"]:
            raise SystemExit("STOP: la carta non sta nell'A3")
        # 2) impagina le colonne bilanciate
        HTML_A3.write_text(documento(dati, [[tutti[i] for i in g] for g in gruppi], servizio), encoding="utf-8")
        for query, nome in (("", "Menu-Autunno-2026_A3_Stampa.pdf"), ("?schermo", "Menu-Autunno-2026_A3_Schermo.pdf")):
            apri(pg, HTML_A3.as_uri() + query)
            pg.pdf(path=str(QUI / "pdf" / nome), prefer_css_page_size=True, print_background=True)
            print("creato pdf/" + nome)
        b.close()


if __name__ == "__main__":
    main()
