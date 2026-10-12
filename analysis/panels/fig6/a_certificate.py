"""Independently generate fig6/a_certificate as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_witness()
sc, kind, p, ref, L, theta, lo, hi, R, rowsA, mapsA, rowsR, optR, dst, log, H, W, tz, ext, tt, b, i, j, k, q, u = [data[key] for key in ["sc","kind","p","ref","L","theta","lo","hi","R","rowsA","mapsA","rowsR","optR","dst","log","H","W","tz","ext","tt","b","i","j","k","q","u"]]
fig, ax = canvas(2.5, 0.9)
top = ax
top.bar(tt, H[W0:W1] / L * 100, color='#d55e00', width=.85, label='hierarchy cost $H$')
top.bar(tt, [W[t][0] / L * 100 if t in W else 0 for t in tt], color='#56b4e9', width=.4, label='witness bound')
top.axhline(theta / L * 100, color='k', ls=':', lw=.6); top.tick_params(labelbottom=False); top.set_ylabel('% axis')
top.legend(loc='upper left', ncol=2, framealpha=.8, handlelength=1)
top.set_title('(a) merge tree kept: $H$ and witness triples'); top.set_ylim(0, 48)
ax.set_xlim(W0 - .5, W1 - .5)
ax.tick_params(labelbottom=False)
save(fig, 'fig6', 'a_certificate')
