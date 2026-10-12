"""Independently generate fig2/d_map_column as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *
from matplotlib.patches import Rectangle, FancyArrowPatch
COL = fc.COL
P = fc.P

data = prepare_concept()
g, X, Y, f, vals, merges, idx, sAB, sRoot, gamma, q, w, gap, tau, u = [data[key] for key in ["g","X","Y","f","vals","merges","idx","sAB","sRoot","gamma","q","w","gap","tau","u"]]
fig, ax = canvas(2.5, 2.1)
# (d) the column of the merge tree map: leaf values at anchors, barriers at merge values between them
order = sorted(fc.P, key=lambda k: u[k]); xx = np.linspace(0, 10, 800)
knots_x = [0.] + [u[k] for k in order] + [10.]; top = sRoot + .12
bars = {('A', 'B'): sAB, ('B', 'C'): sRoot}
prof = np.empty_like(xx); owner = np.empty(len(xx), object)
pts = [(0., top, None)]
for a_, b_ in zip(order[:-1], order[1:]):
    pts += [(u[a_], vals[a_], a_), ((u[a_] + u[b_]) / 2, bars.get((a_, b_), bars.get((b_, a_))), None)]
pts += [(u[order[-1]], vals[order[-1]], order[-1]), (10., top, None)]
px = np.array([p[0] for p in pts]); py = np.array([p[1] for p in pts])
for m in range(len(pts) - 1):
    sel = (xx >= px[m]) & (xx <= px[m + 1]); t_ = (xx[sel] - px[m]) / (px[m + 1] - px[m])
    prof[sel] = py[m] + (py[m + 1] - py[m]) * (1 - np.cos(np.pi * t_)) / 2
for k in fc.P:
    m = abs(xx - u[k]) < .3; ax.plot(xx[m], prof[m], color=COL[k], lw=1.8)
ax.plot(xx, prof, color='k', lw=.5, alpha=.6)
for k in fc.P: ax.plot(u[k], vals[k], 'o', color=COL[k], ms=4, mec='k', mew=.4)
ax.axhline(sAB, color='#888888', lw=.5, ls='--'); ax.axhline(sRoot, color='#888888', lw=.5, ls='--')
ax.text(10.1, sAB, 'A–B', fontsize=6, va='center'); ax.text(10.1, sRoot, 'root', fontsize=6, va='center')
lo = min(vals.values()) - .2
ax.imshow(prof[None, :], extent=[0, 10, lo - .25, lo - .05], aspect='auto', cmap=fs.FIELD_CMAP, vmin=-1.1, vmax=1.1)
ax.set(xlim=(0, 11.2), ylim=(lo - .28, top + .1), xticks=[], yticks=[]); ax.set_xlabel('1-D position (one map column)')
ax.set_title('(d) merge tree map column')
save(fig, 'fig2', 'd_map_column')
