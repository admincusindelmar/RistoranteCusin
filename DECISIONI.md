# Decisioni sul menù d'autunno 2026

Ogni voce dice cosa è stato deciso e perché. Rispetto al semidefinitivo di Noemi (`riferimenti/2026-10-08_Menu-Semidefinitivo-Noemi.pdf`) **piatti e prezzi non sono cambiati** (i prezzi sono stati poi aggiornati il 09.10.2026, vedi §5): il lavoro riguarda grafica, leggibilità, tono e alcune correzioni di testo, elencate al punto 4. La stessa spiegazione, scritta per Noemi, è in `riferimenti/2026-10-08_Mail-Carmine-a-Noemi.txt`.

## 1. Linee guida della Marca (provvisorie, v0.1 del 03.10.2026)
Valori completi in `riferimenti/guidelines-tokens.json`.
- **Colori**:
  - blu Cusin `#152B61` per il testo dei piatti;
  - champagne `#D6C6A5` **solo per filetti e decori**, mai per il testo: sull'avorio arriva a 1,5:1 e non si legge;
  - avorio `#F4EDE2` come fondo, che in stampa lo dà la carta;
  - grigio caldo scuro `#675E53` per traduzioni, allergeni e note (5,5:1 sull'avorio).
- **Caratteri**: Cormorant Garamond per titoli, nomi dei piatti e traduzioni; Montserrat per descrizioni, etichette e allergeni.
- **Logo**: il monogramma. Il nome si scrive «CUSIN» in Cormorant maiuscolo spaziato.
- **Perché si applicano già al menù**: è il primo stampato dopo le guidelines, e va nelle cartelle nuove che portano lo stesso monogramma.
- Le guidelines sono **provvisorie**. Se cambiano, il menù si adegua dalla stagione successiva.

## 2. Grafica
- **Via l'oro dai testi** (titoli di sezione, «il consiglio dello Chef»). A getto d'inchiostro l'oro diventa un ocra piatto, e sull'avorio si legge pochissimo.
- **Via le icone di sezione** (conchiglia, pesce, spiga, foglia) **e la scrittura a mano**. Erano un secondo linguaggio grafico accanto al monogramma, che ora è l'unico segno.
- **Monogramma in testa** a ogni pagina e **piede «Cusin · Autunno 2026»**, così la carta dice anche di che stagione è.
- **Copertina** (scelta di Carmine fra tre opzioni, 08.10.2026): il monogramma grande, la citazione di Wilde e «CUSIN» in fondo. Il piede della copertina porta solo «Autunno 2026», perché «Cusin» è già sopra: è voluto. Ha sostituito il disegno della terrazza, che non era coerente col tono del menù.
  - Il monogramma va **allineato all'incisione della cartella**: quando la si apre, il foglio compare dove stava la copertina di legno, e il segno deve restare al suo posto.
  - La posizione attuale è **provvisoria**. Le misure da prendere e la formula sono in `STATO.md`.
- **Citazione di Wilde**: l'attribuzione è stata verificata l'08.10.2026. Viene dalle memorie dell'amico Edgar Saltus (*Oscar Wilde: An Idler's Impression*, 1917), è la fonte riportata dai repertori e si può stampare con la firma di Wilde.
  - Nell'impaginato l'italiano sta in un blocco stretto, interlinea 34 px su corpo 35; subito sotto viene la traduzione, poi il filetto e il nome dell'autore.

## 3. Gerarchia e leggibilità
- **Quattro livelli per piatto**:
  1. nome del piatto, Cormorant 22 px, interlinea stretta;
  2. descrizione, Montserrat 12 px, interlinea ariosa (19 px);
  3. traduzione inglese in **Cormorant corsivo, stretta sotto l'italiano**, quasi senza interlinea: le due lingue si leggono come un blocco (richiesta di Carmine);
  4. allergeni in maiuscoletto piccolo e spaziato, **su una riga loro**, staccati dal blocco italiano-inglese. Solo nel crudo, dove le voci sono brevi, stanno sulla stessa riga della traduzione.
- **Tutte le traduzioni in corsivo**, comprese quelle delle etichette («ANTIPASTI *Starters*»), dei contorni, della legenda, delle note e del prezzo («*per person*»).
- **Il blu è dei piatti.** Note di servizio («servito per l'intero tavolo», «chiedete al nostro personale…») e testi legali sono in grigio, così non competono col menù.
- **Due livelli di etichetta.** Il sopratitolo della pagina («DEGUSTAZIONE», «LA CARTA») non ha filetto. Le etichette di sezione ce l'hanno: ai due lati nelle degustazioni, a seguire nelle pagine della carta.
- **Testata identica su tutte le pagine**: monogramma, sopratitolo e titolo cadono alla stessa altezza.
- **Montserrat per i testi piccoli**: sulla carta martellata un carattere senza grazie regge meglio dei corsivi sottili.
- **Nomi composti mai spezzati** (vedi `CLAUDE.md`). Descrizioni e traduzioni evitano le parole sole sull'ultima riga (`text-wrap: pretty`).
- È stata provata una variante «contrasto», con i nomi più grandi e le descrizioni più strette. **Carmine ha scelto la versione attuale.**

## 4. Tono e testi
- **Tutto al «voi».** La bozza mescolava «scegli», «provalo», «chiedi» con «girate pagina», «rivolgetevi». Il voi si rivolge al tavolo, ed è coerente con la copertina e con le note di servizio. Esempio: «Componete il vostro Crudo», «scegliete, abbinate, brindate».
- **Segnalazioni ridotte**: restano il **consiglio dello Chef**, uno per sezione (cappuccino di mazzancolle, paccheri, spigola alla griglia), e le diciture **Vegetariano/Vegetarian** e **Senza lattosio/Lactose free**. Con sei tipi diversi nessuna spiccava.
  - «Ricetta di famiglia» è passata nella descrizione del fritto.
  - «Tradizione toscana» è uscita come segnalazione. Il piatto si chiama ancora «Tagliata toscana», com'è d'uso, e la descrizione dice «Tagliata di manzo alla toscana», così non promette un manzo di origine toscana.
  - «Novità di stagione» è uscita, perché in una carta stagionale è nuovo quasi tutto.
- **L'etichetta «Pre-dessert» è diventata «Per finire»**, perché la portata chiude il menù e non precede un dolce. Il piatto resta «La nostra piccola pasticceria».
- **Allergeni e diciture bilingui**: «Allergeni/Allergens», «tracce/traces».
- **Pasta Benedetto Cavalieri**: accanto al nome dei tre piatti c'è l'etichetta «18 minuti di cottura · *18 min cooking time*», per evitare disservizi (richiesta di Carmine). La nota in fondo alla pagina dei primi presenta solo la pasta.
- **Correzioni**:
  - «olio extravergine d'oliva» invece di «olio EVO»;
  - in inglese «Dentex steak» (il trancio non è un filetto) e «cavolo nero (Tuscan kale)»;
  - il sottotitolo dei secondi copre anche tagliata e cacciucco.
- **Risolti con Carmine l'08.10.2026**:
  - «Calasole» significa tramonto e resta senza spiegazione;
  - «Uovo Livornese» si scrive con le iniziali maiuscole;
  - i prodotti sono tutti freschi, quindi niente asterisco per i congelati;
  - i dolci li presenta la sala, e c'è una riga che lo dice nella pagina dei contorni;
  - coperto e servizio dolce sono «a persona», il servizio tappo «a bottiglia».

## 4b. Menù A3 (09.10.2026)
- **A3 orizzontale, solo fronte, solo in italiano**, con la grafica del menù A4: un solo carattere (Cormorant), testo in blu, champagne solo per filetti e decori, monogramma blu in testa, piede «Cusin · Autunno 2026».
- Dal vecchio A3 (`menu/A3_DEFINITIVO_Menu_Cusin_2026.pdf`) restano **il QR code** del menù nelle altre lingue, in alto a destra, e **le degustazioni in una fascia in alto**, una accanto all'altra. Sotto c'è la carta in cinque colonne bilanciate.
- Il QR è ricolorato in blu Cusin con il fondo trasparente, e il suo testo è al «voi»: «Il menù nella vostra lingua».
- Nelle degustazioni, se la descrizione comincia già col nome del piatto si scrive solo la descrizione; altrimenti si scrivono nome e descrizione.
- Gli allergeni sono solo numeri, accanto alla descrizione; la legenda e le note di legge stanno nel piede, insieme al servizio.
- Il testo viene da `sorgenti/menu.html`, quindi A4 e A3 dicono sempre le stesse cose.
- **Nuovo antipasto** (09.10.2026, richiesta del ristorante): «Antipasto toscano», prosciutto crudo toscano e pecorini, 18. È in fondo agli antipasti, nel menù A4 e nell'A3.

## 5. Conferme ricevute dopo il passaggio
Una riga per conferma: data · chi l'ha data · cosa. Esempio: «10.10.2026 · Chef · maionese al melone invernale: 3 · 10».

- 09.10.2026 · Noemi, prezzi aggiornati la sera dell'08.10.2026 · **prezzi**. Mancanti, ora inseriti: cappuccino di mazzancolle 17,80; sfera di verza 16,40; calamaro e tarassaco 17,90; tagliolini al pepe e limone 17,80; risotto al Calasole 18,40; risotto al dentice 19,30; ravioli e crema di zucca 16,80. Cambiati: spaghetto alle vongole 19,70 → 19,30; spigola alla griglia 24 → 24,30; grigliata di mare 42 → 42,60; scaloppata di tonno 25 → 25,80; cacciucco vegetale 24 → 22,70. Invariati: mare caldo 18,80, paccheri 24,80, spaghetto al pomodoro 15, fritto 21, tagliata 25, salse 5.

- 09.10.2026 · Chef (ricette in `riferimenti/2026-10-09_Ricette-Chef_menu_ottobre_2026.docx` e risposte riferite in chat) · **allergeni**:
  - nido con Uovo Livornese: il nido è di kataifi → 1 · 2 · 3 · 9;
  - perla di mazzancolle e sfera di verza non sono impanate → 2 · 9 e 7 · 9 · 10;
  - cacciucco vegetale: brodo senza sedano → 1;
  - maionesi all'arancia e kiwi e lime: solo uovo → 3; maionesi al melone invernale e all'ostrica: latte senza lattosio → 7 e 7 · 14;
  - grigliata: aggiunto 3 per la salsa all'arancia inclusa; il pesce (4) resta perché a volte c'è il trancio di tonno;
  - mare caldo: niente pesce → 2 · 9 · 14;
  - tagliata toscana: nessun allergene;
  - contorni: verdure al forno miste (zucchina, finocchio, pomodoro, sedano rapa, carota) → 9; patate arrosto in teglia da sole e insalate fatte al momento → nessuno; patatine fritte nello stesso olio del fritto → tracce 2 · 4 · 14;
  - sedano (9): resta su tutti i piatti dove era segnato, perché lo Chef a volte usa il brodo;
  - il Vegetop non contiene soia.
- 09.10.2026 · Chef · gnocchi al Calasole con uovo (3), tagliolini di pasta all'uovo (3), sugo di pomodoro su base di verdure con sedano (9): erano già segnati, nessuna modifica. **Raviolo e ravioli**: uovo, latte senza lattosio e tracce di soia, sesamo e senape → 1 · 3 · 7 · 9 · tracce 6 · 10 · 11.
- 09.10.2026 · Chef · **piccola pasticceria**: biscotto di frolla (glutine, uova, burro senza lattosio), cioccolato fondente al 70% senza lattosio, con lecitina di soia (conferma successiva dello stesso giorno) → 1 · 3 · 6 · 7 · 12. Il 7 resta perché anche il burro senza lattosio è un derivato del latte; il 12 (marmellata di vino) era già segnato.
- 09.10.2026 · Chef · **salse della grigliata**, tutte con latte senza lattosio, olio di girasole e sale, senza uova: basilico → 7; ostrica → 7 · 14; tartufo (con pepe) → 7. La grigliata, con basilico e arancia incluse, diventa 2 · 3 · 4 · 7 · 14.
- 09.10.2026 · Chef · **pepe del Madagascar**: non si paga a parte, la riga resta senza supplemento. **Acqua in vetro**: 70 cl.
- 09.10.2026 · Chef · calamaro: la verdura è **bietola a coste rosse**, non tarassaco. Il piatto si chiama ora «Calamaro e bietola» (Primo Fiore e carta).

## 6. Modifiche del 09.10.2026 (richieste dal ristorante)
- **Copertina**: il sigillo è alto 80 mm e largo 35 mm. Il bordo alto sta a 100 mm dal bordo superiore del foglio, il bordo destro a 80 mm dal bordo destro, quindi l'asse è a 112,5 mm da sinistra. La citazione scende sotto il sigillo ed è 2 punti più piccola (da 35 a 32,3 px). Citazione, traduzione, firma e «CUSIN» sono centrati sull'asse del sigillo (112,5 mm), non sul centro dell'area di testo (116,5 mm), perché il sigillo non sta al centro dell'area di testo.
- **Un solo carattere in tutto il menù**: Cormorant Garamond anche per descrizioni, allergeni, note, prezzi ed etichette. Montserrat non si usa più, e questo supera il punto 3 «Montserrat per i testi piccoli». I corpi sono stati ricalcolati, perché Cormorant è più piccolo a parità di corpo: descrizione 15,5 px, allergeni 13,5 px, prezzi 17,5 px. Le cifre sono allineate (lining).
- **Nome del piatto** un punto più piccolo: da 22 a 20,7 px.
- **Allergeni e diciture non più in maiuscolo**: «Allergeni/Allergens 2 · 9», «Vegetariano/Vegetarian». Le etichette di sezione restano maiuscole e spaziate.
- **Testi**:
  - Stella di Mare: «Sfera di mazzancolle» diventa **«Perla di mazzancolle»**, con «ripiena di sedano rapa, crema di castagne e zenzero» (senza passion fruit e lime);
  - Stella di Mare: seppia «su fondo bruno di cipolla dorata in due consistenze»;
  - Stella di Mare: gnocchi al Calasole «Gnocchi di riso, calamari, totani, seppie e tartufo»;
  - Stella di Mare: piccola pasticceria «Cioccolatini fondenti ripieni di marmellata di vino e crema di melone invernale e biscotto ai fichi»;
  - Vegetariana di Mare e carta: cacciucco vegetale «Brodo di alga kombu, funghi, pomodoro, cipollotto, melone invernale e cavolo nero con cialda di pane croccante»;
  - Primo Fiore: «(il nostro pepe di semi di papaya)» tra parentesi;
  - Primo Fiore e carta: calamaro e tarassaco, «cotto a bassa temperatura» diventa **«Calamaro CBT»** nella descrizione. Il nome del piatto resta (correzione del 09.10.2026). In inglese resta «Slow-cooked squid»;
  - Primo Fiore e carta: tagliolini «artigianali al pepe con limone candito, mazzancolle e funghi porcini»;
  - paccheri farciti, raviolo e ravioli: «ricotta (senza lattosio)», tra parentesi.
- 09.10.2026 · ristorante (risposta in chat) · **antipasto toscano**: prosciutto crudo toscano e pecorini, senza pane, crostini, miele o confetture → 7.
