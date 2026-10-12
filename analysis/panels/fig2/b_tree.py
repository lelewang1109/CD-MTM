"""Independently generate fig2/b_tree as PDF and PNG."""
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
# (b) join tree
xs = dict(A=0, B=1, C=2); xAB = .5
for k in 'AB': ax.plot([xs[k], xs[k]], [vals[k], sAB], color=COL[k], lw=2)
ax.plot([0, 1], [sAB, sAB], color='k', lw=1); ax.plot([xAB, xAB], [sAB, sRoot], color='#0072b2', lw=2, alpha=.6)
ax.plot([xs['C'], xs['C']], [vals['C'], sRoot], color=COL['C'], lw=2); ax.plot([xAB, 2], [sRoot, sRoot], color='k', lw=1)
ax.plot([1.25, 1.25], [sRoot, sRoot + .12], color='k', lw=1)
for k in fc.P: ax.plot(xs[k], vals[k], 'o', color=COL[k], ms=5, mec='k', mew=.4); ax.text(xs[k], vals[k] - .09, k, ha='center', va='top', fontsize=7, fontweight='bold')
ax.plot(xAB, sAB, 's', color='k', ms=3.5); ax.plot(1.25, sRoot, 's', color='k', ms=3.5)
ax.annotate('', (1.62, sRoot), (1.62, sAB), arrowprops=dict(arrowstyle='<->', lw=.7, color='#c0392b'))
ax.text(1.68, (sAB + sRoot) / 2, r'$\gamma_v$', color='#c0392b', fontsize=7.5, va='center')
ax.text(-.15, sAB + .03, 'A–B merge', fontsize=6, va='bottom'); ax.text(.55, sRoot + .03, 'root', fontsize=6, va='bottom')
ax.set(xlim=(-.4, 2.4), ylim=(min(vals.values()) - .3, sRoot + .3), xticks=[]); ax.set_ylabel('value', labelpad=1)
ax.set_title('(b) merge tree $((A,B),C)$')
save(fig, 'fig2', 'b_tree')
