"""
Sistema gli a capo dopo l'impaginazione: se l'ultima parola di un testo resta da sola
sulla riga degli allergeni, gli allergeni vanno a capo e il testo si ridistribuisce.
Usato da genera_menu.py e menu_a3.py prima di misurare e stampare.
"""

SISTEMA_A_CAPO_JS = r"""() => {
  let corretti = 0;
  document.querySelectorAll('span.all-riga, span.al').forEach(sp => {
    const p = sp.parentElement;
    // parole del testo che precedono gli allergeni, con la loro riga
    const parole = [];
    const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) {
      const n = w.currentNode;
      if (sp.contains(n)) break;
      if (n.parentElement.closest('.all-riga, .al, .chef, .etichetta, .cottura')) continue;
      const re = /\S+/g; let m;
      while ((m = re.exec(n.textContent))) {
        const r = document.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
        const q = r.getClientRects()[0]; if (q) parole.push(q.bottom);
      }
    }
    if (parole.length < 1) return;
    const ultima = parole[parole.length - 1];
    const penultima = parole.length > 1 ? parole[parole.length - 2] : ultima;
    const spBottom = sp.getClientRects()[0].bottom;
    const stessaRigaAllergeni = Math.abs(spBottom - ultima) < 4;
    const sola = Math.abs(ultima - penultima) > 4;
    // allergeni da mandare a capo (parola rimasta sola) o già a capo da soli:
    // in entrambi i casi la riga degli allergeni parte pulita, senza puntino né rientro
    if ((stessaRigaAllergeni && sola) || !stessaRigaAllergeni) {
      sp.style.display = 'block';
      sp.style.marginLeft = '0';
      sp.classList.add('a-capo');
      corretti++;
    }
  });
  return corretti;
}"""
