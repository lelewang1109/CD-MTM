"""Independently generate fig3/c_optimal_filling as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *
from fig_topo_price import profile
COL = fc.COL

data = prepare_price()
g, X, Y, f, vals, merges, idx, sAB, sR, gam, q, w, gap, tau, uA, xx, top, lo, cases = [data[key] for key in ["g","X","Y","f","vals","merges","idx","sAB","sR","gam","q","w","gap","tau","uA","xx","top","lo","cases"]]
fig, ax = canvas(2.4, 1.8)
for c, (title, order, pos, bars, dtop, err) in enumerate(cases[2:3], start=2):
    prof = profile(order, pos, vals, bars, top, xx)
    ax.plot(xx, prof, color='k', lw=.8)
    for k in order:
        m = abs(xx - pos[k]) < .35; ax.plot(xx[m], prof[m], color=COL[k], lw=2)
        ax.plot(pos[k], vals[k], 'o', color=COL[k], ms=4, mec='k', mew=.4); ax.text(pos[k], vals[k] - .07, k, ha='center', va='top', fontsize=7, fontweight='bold')
        ax.plot(q[k], lo - .02, '^', color=COL[k], ms=4, clip_on=False)
    ax.axhline(sAB, color='#0072b2', lw=.6, ls='--'); ax.axhline(sR, color='#d55e00', lw=.6, ls='--')
    if c == 0:
        ax.text(9.95, sAB + .02, 'true A–B merge', fontsize=6, color='#0072b2', va='bottom', ha='right')
        ax.text(9.95, sR + .02, 'true root', fontsize=6, color='#d55e00', va='bottom', ha='right')
    # read A-B merge level on the map: max of profile between A and B
    a_, b_ = sorted([pos['A'], pos['B']]); readAB = prof[(xx >= a_) & (xx <= b_)].max()
    if abs(readAB - sAB) > 1e-3:
        xm = (a_ + b_) / 2 + (.9 if c == 1 else -1.6)
        ax.annotate('', (xm, readAB), (xm, sAB), arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=.8))
        ax.text(xm + .15, (readAB + sAB) / 2, 'A–B: ' + (r'$\gamma_v$' if c == 1 else r'$\gamma_v/2$'), color='#c0392b', fontsize=6.5, va='center',
                bbox=dict(facecolor='white', edgecolor='none', pad=.5, alpha=.85))
    if c == 2:
        aC = prof[(xx >= pos['A']) & (xx <= pos['C'])].max(); xm = pos['C'] + .9
        ax.annotate('', (xm, sR), (xm, aC), arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=.8))
        ax.text(xm + .15, (sR + aC) / 2, r'A–C: $\gamma_v/2$', color='#c0392b', fontsize=6.5, va='center',
                bbox=dict(facecolor='white', edgecolor='none', pad=.5, alpha=.85))
    ax.set(xlim=(0, 10), ylim=(lo - .05, top + .08), xticks=[], yticks=[])
    ax.set_title(title)
    ax.text(5, lo - .2, f'position error {err:.2f}   $d_{{top}}$ = ' + ('0' if dtop == 0 else (r'$\gamma_v$' if c == 1 else r'$\gamma_v/2$')),
            ha='center', va='top', fontsize=6.5)
save(fig, 'fig3', 'c_optimal_filling')
