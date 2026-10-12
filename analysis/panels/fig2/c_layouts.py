"""Independently generate fig2/c_layouts as PDF and PNG."""
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
# (c) layouts on the reference axis
q = {k: g[idx[k][1]] for k in fc.P}; w, gap = 1.0, .2
tau = (w + gap + q['B'] - q['C']) / 2; u = dict(A=q['A'], B=q['B'] - tau, C=q['C'] + tau)
yq, y1, y2 = 2.6, 1.55, .35
ax.plot([0, 10], [yq, yq], color='k', lw=.5); ax.text(0, yq + .22, 'reference $q$', fontsize=6.3)
for y0, pos, lab in [(y1, q, 'sorted by $q$: A C B, splits {A,B}'), (y2, u, 'best order keeping {A,B}: A B C')]:
    ax.plot([0, 10], [y0, y0], color='#bbbbbb', lw=.5); ax.text(0, y0 + .24, lab, fontsize=6.3)
    for k, x in pos.items():
        ax.add_patch(Rectangle((x - w / 2, y0 - .15), w, .3, color=COL[k], alpha=.85, lw=0))
        ax.text(x, y0, k, ha='center', va='center', color='w', fontsize=7, fontweight='bold')
for k in fc.P:
    ax.plot(q[k], yq, 'v', color=COL[k], ms=4.5)
    ax.plot([q[k], q[k]], [yq, y2 + .17], ':', color=COL[k], lw=.7)
    if abs(u[k] - q[k]) > .05:
        yy = y2 - (.26 if k == 'B' else .4); ax.add_artist(FancyArrowPatch((q[k], yy), (u[k], yy), arrowstyle='->', mutation_scale=7, color=COL[k], lw=1.1))
ax.text(5, y2 - .72, f'max deviation $\\tau^*$ = {tau:.2f}, shared by B and C', ha='center', fontsize=6.3)
ax.set(xlim=(-.2, 10.2), ylim=(-.45, 3.0), xticks=[], yticks=[]); [ax.spines[s_].set_visible(False) for s_ in ['left', 'bottom']]
ax.set_title('(c) hierarchy vs. space')
save(fig, 'fig2', 'c_layouts')
