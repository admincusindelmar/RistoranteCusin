# Genera il foglio stampabile per l inventario vini: python3 genera_inventario.py inventario-vini.pdf
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import sys
out = sys.argv[1]
W, H = A4
c = canvas.Canvas(out, pagesize=A4)
c.setTitle("Inventario Vini")
m = 12*mm
c.setFont("Helvetica-Bold", 16)
c.drawString(m, H-m-6*mm, "INVENTARIO VINI")
c.setFont("Helvetica", 10)
c.drawString(m, H-m-14*mm, "Data: ______________________")
c.drawString(m+75*mm, H-m-14*mm, "Compilato da: ______________________")
c.drawRightString(W-m, H-m-6*mm, "Foglio n. ______")
top = H-m-22*mm
bottom = m+4*mm
rows = 30
hh = 9*mm
rh = (top-bottom-hh)/rows
cols = [("N.", 8*mm), ("Nome prodotto", None), ("Cantina", 48*mm), ("Quantità\nordinata", 24*mm), ("Quantità\nmagazzino", 24*mm)]
tw = W-2*m
fixed = sum(w for _, w in cols if w)
cols = [(n, w if w else tw-fixed) for n, w in cols]
xs = [m]
for _, w in cols: xs.append(xs[-1]+w)
# header
c.setFillGray(0.85); c.rect(m, top-hh, tw, hh, fill=1, stroke=0); c.setFillGray(0)
c.setFont("Helvetica-Bold", 9.5)
for i, (n, w) in enumerate(cols):
    lines = n.split("\n"); cx = xs[i]+w/2
    y0 = top-hh/2 + (len(lines)-1)*5.5/2*1 - 3
    for j, l in enumerate(lines):
        c.drawCentredString(cx, y0 - j*11 + (len(lines)-1)*2.5, l)
# zebra + numbers
c.setFont("Helvetica", 8)
for r in range(rows):
    y = top-hh-(r+1)*rh
    if r % 2: c.setFillGray(0.95); c.rect(m, y, tw, rh, fill=1, stroke=0); c.setFillGray(0)
    c.setFillGray(0.4); c.drawCentredString(xs[0]+cols[0][1]/2, y+rh/2-3, str(r+1)); c.setFillGray(0)
# grid
c.setLineWidth(0.5)
for r in range(rows+1):
    y = top-hh-r*rh; c.line(m, y, W-m, y)
for x in xs: c.line(x, top, x, bottom)
c.setLineWidth(1.2); c.rect(m, bottom, tw, top-bottom); c.line(m, top-hh, W-m, top-hh)
c.showPage(); c.save()
