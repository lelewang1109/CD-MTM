"""Independently generate fig3/d_tradeoff as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_price()
g, X, Y, f, vals, merges, idx, sAB, sR, gam, q, w, gap, tau, uA, xx, top, lo, cases = [data[key] for key in ["g","X","Y","f","vals","merges","idx","sAB","sR","gam","q","w","gap","tau","uA","xx","top","lo","cases"]]
fig, ax = canvas(2.4, 1.8)
# (d) trade-off
ax.step([0, gam / 2, gam * 1.25], [tau, 0, 0], where='post', color='k', lw=1, ls='--', label='certified bound $\\Phi$')
for (lab, x, y, mk) in [('(a)', 0, tau, 'o'), ('(b)', gam, 0, 's'), ('(c)', gam / 2, 0, 'o')]:
    ax.plot(x, y, mk, color='#009e73' if lab != '(b)' else '#999999', ms=5, mec='k', mew=.4)
    ax.text(x + .015, y + .1, lab, fontsize=6.5)
ax.fill_between([0, gam / 2], 0, tau, color='#dddddd', alpha=.6, lw=0); ax.text(gam * .1, tau * .35, 'impossible', fontsize=6, color='#666666')
ax.set(xlim=(-.02, gam * 1.25), ylim=(-.15, tau * 1.25), xticks=[0, gam / 2, gam], xticklabels=['0', r'$\gamma_v/2$', r'$\gamma_v$'])
ax.set_xlabel('$d_{top}$', labelpad=1); ax.set_ylabel('position error', labelpad=1); ax.set_title('(d) trade-off')
ax.legend(loc='upper right', fontsize=6, handlelength=1.5, frameon=False)
save(fig, 'fig3', 'd_tradeoff')
