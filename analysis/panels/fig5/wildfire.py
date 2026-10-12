"""Independently generate fig5/wildfire as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

fig, ax = canvas(2.8, 1.8)
n = 'wildfire'; TITLE = {n: 'Wildfire 2019'}
r = json.loads((tr.OUT / f'attainable_{n}.json').read_text())
d = [x['delta'] * 100 for x in r['frontier']]
ax.step(d, [x['F'] * 100 for x in r['frontier']], where='post', color='#0072b2', lw=1.1, label='exact frontier F')
ax.step(d, [x['Phi'] * 100 for x in r['frontier']], where='post', color='k', lw=.7, ls='--', label='certified bound Φ')
for o in r['ours']:
    ax.plot(o['D_lca_share'] * 100, o['E_share'] * 100, 'o', mfc='none', color='#009e73', ms=4.5)
    ax.plot(o['D_opt_share'] * 100, o['E_share'] * 100, 'o', color='#009e73', ms=4.5)
    ax.plot([o['D_opt_share'] * 100, o['D_lca_share'] * 100], [o['E_share'] * 100] * 2, '-', color='#009e73', lw=.5)
ax.set(title=TITLE.get(n, n), xlabel='$d_{top}$ (% of value range)', xlim=(-2, 72))
ax.set_ylabel('τ(π), % of axis')
ax.plot([], [], 'o', color='#009e73', label='R, optimal filling')
ax.plot([], [], 'o', mfc='none', color='#009e73', label='R, LCA filling')
ax.legend(fontsize=6.5, handlelength=1.2, borderpad=.3, labelspacing=.25)
save(fig, 'fig5', 'wildfire')
