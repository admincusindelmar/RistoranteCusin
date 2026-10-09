# Menù d'autunno 2026 di Cusin — cartella di lavoro

Qui si porta a termine la **carta d'autunno 2026 del ristorante Cusin** (Antignano, Livorno, dentro l'Hotel Rex). Il menù va stampato in casa e inserito nelle cartelle di legno del ristorante.

Il lavoro passa di mano il 09.10.2026. Fin qui lo ha seguito **Carmine Pellegrino**, consulente esterno amico del titolare, partendo dal semidefinitivo di **Noemi Granchi**, direttore di sala. Da ora lo continua Noemi con questa cartella. Il titolare è **Gioacchino Cusin**.

Chi lavora qui deve sapere tutto ciò che sapeva Carmine. Le decisioni e il loro perché sono in `DECISIONI.md`, i punti aperti in `STATO.md`: **leggerli entrambi prima di modificare il menù.**

## Cosa c'è
- `sorgenti/menu.html` — **il menù**: un solo file HTML da cui escono i PDF. Si modifica qui, mai i PDF.
- `sorgenti/cusin-monogramma-blu.png` — il monogramma usato nel menù.
- `genera.sh` — rigenera i due PDF in `pdf/` con Chrome headless. Serve la connessione, perché i caratteri arrivano da Google Fonts.
- `genera_cloud.py` — la stessa cosa nell'ambiente cloud di Claude Code, dove Chrome non scarica da solo i caratteri: `python3 genera_cloud.py`.
- `genera_a3.py` — genera il **menù A3** orizzontale, solo fronte e solo in italiano, leggendo piatti, prezzi e allergeni da `sorgenti/menu.html`: `python3 genera_a3.py`. L'A3 non si modifica a mano: si corregge `menu.html` e si rilanciano tutti e due gli script. `sorgenti/menu-a3.generato.html` lo riscrive lo script ogni volta.
- `sorgenti/qr-menu-lingue.png` — il QR code del menù nelle altre lingue (in blu Cusin), usato nell'A3.
- `pdf/Menu-Autunno-2026_Schermo.pdf` — con l'avorio simulato, per vederlo a video.
- `pdf/Menu-Autunno-2026_Stampa.pdf` — senza fondo, da stampare sulla carta avorio.
- `pdf/Menu-Autunno-2026_A3_Stampa.pdf` e `_A3_Schermo.pdf` — il menù A3, senza fondo e con l'avorio simulato.
- `riferimenti/`:
  - `2026-10-08_Menu-Semidefinitivo-Noemi.pdf` — la versione di partenza;
  - `2026-10-08_Mail-Carmine-a-Noemi.txt` — la mail che spiega tutte le modifiche;
  - `cartelle/` — foto delle cartelle di legno;
  - `logo/` — il monogramma in blu, champagne e avorio;
  - `guidelines-tokens.json` — colori, caratteri e spaziature delle linee guida provvisorie di Cusin.
- `DECISIONI.md` — cosa è stato deciso e perché.
- `STATO.md` — cosa manca, cosa è già risolto, prossimi passi.

## Come si lavora
1. Si modifica `sorgenti/menu.html`.
2. Si lancia `./genera.sh`.
3. **Prima di consegnare si controllano le pagine.** Si rasterizza il PDF (per esempio con `pdftoppm -r 80 -png`) e si guardano le immagini. Le pagine devono essere **9** (copertina più 8) e **nessuna deve sbordare**: il piede «Cusin · Autunno 2026» deve vedersi in fondo a ogni pagina. Se un testo nuovo fa sbordare una pagina, si stringono le spaziature di quella pagina, mai i corpi del testo.
4. Ogni decisione nuova va scritta in `DECISIONI.md`. Ogni punto aperto risolto va tolto da `STATO.md`, e anche il suo giallo dal menù.

## Regole che non si toccano senza parlarne
- **I prezzi li decide Gioacchino** e si scrivono esattamente come li comunica, decimali compresi (18,80 accanto a 18 va bene). Non si arrotondano e non si uniformano. Le guidelines chiedono un formato solo, ma Carmine ha scelto di non toccare i prezzi: questa regola vale più di quella.
- **Allergeni**: si cambiano solo su conferma di cucina o sala, mai per deduzione. Ogni conferma si annota in fondo a `DECISIONI.md` con data e nome di chi l'ha data. Ogni piatto ha la riga «Allergeni/Allergens …», con i numeri della legenda di pagina 8.
- **Giallo** (classe `tbd`) = punto da verificare. Nel PDF finale di stampa non deve restarne nessuno.
- **Registro al «voi»** ovunque.
- **Nomi composti mai spezzati a fine riga**: *passion fruit*, *sedano rapa*, *melone invernale*, *olio extravergine d'oliva*, *18 minuti di cottura*, *Reg. UE 1169/2011*, *king prawn*, *sweet-potato crust*. Nel file sono chiusi in `<span class="nb">`. Ogni testo nuovo va trattato allo stesso modo.
- **Margini**: 40 mm a sinistra per le viti della cartella, 17 mm a destra, 11 mm in alto e in basso. Sono calcolati sulle cartelle vere: non si cambiano.
- **Stampa solo fronte**, su carta avorio martellata da 180–200 g, con la stampante a getto d'inchiostro interna. Le basi della stampa (spegnere il fondo simulato, grammatura, margini) sono note e già provate: non serve ripeterle.
- Il nome del ristorante è **Cusin**. Il vecchio nome non si usa nei testi del menù.
- **Fanno fede `sorgenti/menu.html` e questi file.** `riferimenti/guidelines-tokens.json` serve solo per i colori del tema «Carta». Le sue misure di testo sono quelle di partenza, poi ritoccate nel menù. Temi «Sera», sito e bottoni non riguardano il menù.

## Come fare le modifiche ricorrenti
- **Prezzo mancante**: `<div class="prezzo"><span class="tbd">—</span></div>` diventa `<div class="prezzo">16</div>`.
- **Allergeni confermati**: `<p class="all"><span class="tbd">Allergeni/Allergens …</span></p>` diventa `<p class="all">Allergeni/Allergens 3 · 10</p>`. Le tracce si scrivono `· tracce/traces 6 · 10`. Le diciture si aggiungono così: `<span class="dieta">Vegetariano/Vegetarian</span>`.
- **Allergeni dei contorni**: nella tabella `.tab` della pagina 8, dentro il `<i>` della voce, dopo l'inglese: `<span class="all-in">Allergeni/Allergens 1</span>`. Poi si toglie la riga gialla sotto i contorni.
- **Supplemento del pepe del Madagascar**: se si paga, il modello è quello delle salse in aggiunta della grigliata (pagina 7): una riga `+ …` con il prezzo nella colonna di destra. Se è incluso, si toglie solo il giallo.
- **Formato dell'acqua**: `<span class="unita tbd">formato?</span>` diventa `<span class="unita">75 cl</span>`.
- **Testo nuovo**: i nomi composti si chiudono in `<span class="nb">`.
