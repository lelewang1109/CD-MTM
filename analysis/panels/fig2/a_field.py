"""Independently generate fig2/a_field as PDF and PNG."""
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
# (a) field
ax.imshow(f, origin='lower', extent=[0, 10, 0, 10], cmap=fs.FIELD_CMAP, vmin=-1.1, vmax=1.1)
ax.contour(g, g, f, levels=np.linspace(f.min(), f.max(), 13), colors='k', linewidths=.25, alpha=.5)
for k, (x, y) in fc.P.items():
    i, j = idx[k]; x, y = g[j], g[i]
    ax.plot(x, y, 'o', color=COL[k], ms=6, mec='w', mew=.8); ax.text(x + .35, y + .35, k, color='k', fontsize=8, fontweight='bold')
    ax.plot([x, x], [y, -.9], ':', color=COL[k], lw=.8, clip_on=False)
    ax.plot(x, -.9, 'v', color=COL[k], ms=4, clip_on=False)
ax.annotate('', (9.7, -.9), (.3, -.9), arrowprops=dict(arrowstyle='->', lw=.8), annotation_clip=False)
ax.text(5, -1.8, 'reference coordinate $q$', ha='center', fontsize=6.5)
ax.set(xlim=(0, 10), ylim=(0, 10), xticks=[], yticks=[], aspect='auto'); ax.set_title('(a) field: A, B share a trough')
save(fig, 'fig2', 'a_field')
