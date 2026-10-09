# Stato al 09.10.2026

Il menù è completo nella struttura. Restano i punti in giallo: sono domande, non scelte grafiche, e **ogni punto qui sotto ha il suo giallo nel menù**. Erano già nella mail di Carmine a Noemi dell'08.10.2026.

## Da chiudere (in giallo nel menù)
**Allergeni da confermare** (cucina o sala):
1. **Maionesi del crudo** (arancia, kiwi e lime, melone invernale, ostrica): oltre all'uovo (3) c'è senape (10)? La maionese al melone invernale oggi non ha allergeni, quella all'ostrica solo 14.
2. **Salse della grigliata** (basilico, arancia, ostrica, tartufo): sono a base di maionese? Quali allergeni hanno?
3. **Piccola pasticceria**: il cioccolato fondente contiene lecitina di soia (6) o tracce di latte e frutta a guscio?
4. **Nido con Uovo Livornese**: se il nido è di pasta o kataifi, manca il glutine (1).
5. **Sfera di mazzancolle, sfera di verza**: se sono impanate, mancano glutine (1) e uovo (3).
6. **Cacciucco vegetale**: è l'unico piatto con un brodo senza sedano (9). È giusto?
7. **Tagliata toscana e contorni**: quali allergeni hanno?
8. **Patatine fritte**: se vanno nello stesso olio del fritto di mare, si indicano 2, 4 e 14.

**Altro**:
9. **Prezzi mancanti**: cappuccino di mazzancolle, sfera di verza, calamaro e tarassaco, tagliolini, risotto al Calasole, risotto al dentice, ravioli.
10. **Acqua in vetro**: il formato (75 cl? 50 cl?). Va aggiunto accanto al nome, come «a persona» per il coperto.
11. **Pepe del Madagascar** sui paccheri: è un supplemento? Se sì, va scritto con il prezzo.

## Monogramma della copertina
La posizione attuale è provvisoria: 45 mm dal bordo alto del foglio, asse a 116,5 mm dal bordo sinistro, altezza 42 mm. Sta nelle tre variabili `--mono-top`, `--mono-asse` e `--mono-h` di `sorgenti/menu.html`.

Le misure si prendono sulla cartella del menù:
- **a** = distanza del bordo alto dell'incisione dal bordo alto della cartella;
- **b** = distanza del centro del monogramma dal bordo sinistro della cartella;
- **h** = altezza dell'incisione;
- **c** = di quanto il bordo alto del foglio montato sta sotto il bordo alto della cartella;
- **d** = di quanto il bordo sinistro del foglio montato sta a destra del bordo sinistro della cartella.

I tre valori si calcolano così:
- `--mono-top` = a − c
- `--mono-asse` = b − d
- `--mono-h` = h

**Attenzione**: l'incisione è centrata sul pannello che si apre, cioè a destra della costa, non sulla cartella intera. Per la formula la larghezza della costa non serve: basta misurare **b** dal bordo sinistro della cartella. La mail la chiedeva solo come controllo.

Dopo il calcolo: si stampa la copertina su carta comune, la si monta e si apre la cartella un paio di volte per controllare.

## Prossimi passi
1. Chiudere i punti 1–11 e togliere il loro giallo (classe `tbd`) da `sorgenti/menu.html`.
2. Allineare il monogramma con le misure.
3. Rigenerare con `./genera.sh` e controllare le 9 pagine.
4. Fare una prova su un foglio di carta avorio martellata: leggibilità dei grigi e dei corsivi piccoli, con la luce della sala.
5. Stampare la versione definitiva da `pdf/Menu-Autunno-2026_Stampa.pdf`. Prima va verificato che nel menù non resti nessun giallo.

## Fuori da questa cartella
La **carta dei vini** ha una sua cartella di legno (foto in `riferimenti/cartelle/`), ma non fa parte di questo lavoro.
