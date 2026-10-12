"""Independently generate supp_toy/reference as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

fig, ax = canvas(3.4, 0.9)
q = dict(A=20, C=50, B=80); col = dict(A='#0072b2', B='#56b4e9', C='#d55e00')
def draw(ax, pos, title):
    ax.set_xlim(0, 100); ax.set_ylim(-.8, 1.6); ax.axhline(0, color='k', lw=.5)
    for k, x in q.items():
        ax.plot([x, x], [0, .75], ':', color=col[k], lw=.8); ax.text(x, .82, f'$q_{k}$', ha='center', color=col[k], fontsize=6.5)
    for k, x in pos.items():
        ax.add_patch(plt.Rectangle((x - 6, -.22), 12, .44, color=col[k], alpha=.85)); ax.text(x, -.72, k, ha='center', fontsize=6.5)
    ax.set_yticks([]); ax.text(100, 1.25, title, fontsize=6.5, ha='right', va='bottom')
    for sp in ['left', 'top', 'right']: ax.spines[sp].set_visible(False)

draw(ax, dict(A=20, C=50, B=80), 'reference order: splits {A,B}')
ax.set_xlabel('reference coordinate')
save(fig, 'supp_toy', 'reference')
