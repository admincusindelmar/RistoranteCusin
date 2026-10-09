#!/bin/bash
# Genera i due PDF del menù da sorgenti/menu.html con Chrome (o Chromium) in modalità headless.
#   pdf/Menu-Autunno-2026_Schermo.pdf  avorio simulato, per vederlo a video
#   pdf/Menu-Autunno-2026_Stampa.pdf   senza fondo, per la carta avorio
# Uso: ./genera.sh   (dalla cartella del pacchetto)
cd "$(dirname "$0")"
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "$(command -v google-chrome)" "$(command -v chromium)"; do
  [ -n "$c" ] && [ -x "$c" ] && CHROME="$c" && break
done
[ -z "$CHROME" ] && { echo "Chrome non trovato: installa Google Chrome." >&2; exit 1; }
mkdir -p pdf
U="file://$PWD/sorgenti/menu.html"
# virtual-time-budget lascia il tempo ai Google Fonts di caricarsi (serve la connessione)
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 \
  --print-to-pdf="$PWD/pdf/Menu-Autunno-2026_Schermo.pdf" "$U?schermo" 2>/dev/null
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 \
  --print-to-pdf="$PWD/pdf/Menu-Autunno-2026_Stampa.pdf" "$U" 2>/dev/null
ls -la pdf
