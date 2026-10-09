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

## 5. Conferme ricevute dopo il passaggio
Una riga per conferma: data · chi l'ha data · cosa. Esempio: «10.10.2026 · Chef · maionese al melone invernale: 3 · 10».

- 09.10.2026 · Noemi, prezzi aggiornati la sera dell'08.10.2026 · **prezzi**. Mancanti, ora inseriti: cappuccino di mazzancolle 17,80; sfera di verza 16,40; calamaro e tarassaco 17,90; tagliolini al pepe e limone 17,80; risotto al Calasole 18,40; risotto al dentice 19,30; ravioli e crema di zucca 16,80. Cambiati: spaghetto alle vongole 19,70 → 19,30; spigola alla griglia 24 → 24,30; grigliata di mare 42 → 42,60; scaloppata di tonno 25 → 25,80; cacciucco vegetale 24 → 22,70. Invariati: mare caldo 18,80, paccheri 24,80, spaghetto al pomodoro 15, fritto 21, tagliata 25, salse 5.
