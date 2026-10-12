"""Independently generate fig6/d_position_error as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_witness()
sc, kind, p, ref, L, theta, lo, hi, R, rowsA, mapsA, rowsR, optR, dst, log, H, W, tz, ext, tt, b, i, j, k, q, u = [data[key] for key in ["sc","kind","p","ref","L","theta","lo","hi","R","rowsA","mapsA","rowsR","optR","dst","log","H","W","tz","ext","tt","b","i","j","k","q","u"]]
fig, ax = canvas(2.5, 0.55)
top = ax; top.set_ylim(0, 24)
top.bar(tt, [np.max(abs(r['x'] - r['reference'])) / L * 100 for r in rowsR[W0:W1]], color='#009e73', width=.85)
top.tick_params(labelbottom=False, labelleft=False); top.set_title(f'(d) relaxed ($\\kappa$ = {int(KAPPA*100)}%), optimal filling')
top.text(.01, .95, 'max position error', transform=top.transAxes, ha='left', va='top', fontsize=6.5, color='#009e73')
ax.set_xlim(W0 - .5, W1 - .5)
ax.tick_params(labelbottom=False)
save(fig, 'fig6', 'd_position_error')
