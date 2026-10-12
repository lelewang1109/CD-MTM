"""Independently generate fig6/c_witness_positions as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_witness()
sc, kind, p, ref, L, theta, lo, hi, R, rowsA, mapsA, rowsR, optR, dst, log, H, W, tz, ext, tt, b, i, j, k, q, u = [data[key] for key in ["sc","kind","p","ref","L","theta","lo","hi","R","rowsA","mapsA","rowsR","optR","dst","log","H","W","tz","ext","tt","b","i","j","k","q","u"]]
fig, ax = canvas(2.2, 2.2)
# (c)
q = np.asarray(ref['qs'][tz]); u = rowsA[tz]['x']
for m in range(len(q)):
    c = '#56b4e9' if m in (i, j) else '#e69f00' if m == k else '#aaaaaa'; lw = 1.3 if m in (i, j, k) else .6
    ax.plot([q[m], u[m]], [1, 0], color=c, lw=lw); ax.plot(q[m], 1, 'v', color=c, ms=4.5); ax.plot(u[m], 0, 'o', color=c, ms=4.5, mec='k', mew=.3)
ax.plot([p.canvas_origin, p.canvas_origin + L], [1, 1], 'k', lw=.5); ax.plot([p.canvas_origin, p.canvas_origin + L], [0, 0], 'k', lw=.5)
ax.text(p.canvas_origin, 1.08, 'reference $q$', fontsize=6.5); ax.text(p.canvas_origin, -.16, 'anchor $u$ (tree kept)', fontsize=6.5)
ax.set_ylim(-.28, 1.22); ax.set_yticks([]); ax.set_xticks([])
for sp in ['left', 'bottom']: ax.spines[sp].set_visible(False)
ax.set_title(f'(c) witness {b/L:.0%}, $\\tau^*$ {log[tz]["tau_hier"]/L:.0%}')
save(fig, 'fig6', 'c_witness_positions')
