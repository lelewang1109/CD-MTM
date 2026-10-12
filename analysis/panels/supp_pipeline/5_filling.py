"""Independently generate supp_pipeline/5_filling as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_pipeline()
ds, sc, kind, p, ref, L, R, t, fr, ids, q, n, lg0, lgR, rowA, rowR, cols, cl, flat, rowsR, maps, dsk, opt, dst, w0, w1, tt_ = [data[key] for key in ["ds","sc","kind","p","ref","L","R","t","fr","ids","q","n","lg0","lgR","rowA","rowR","cols","cl","flat","rowsR","maps","dsk","opt","dst","w0","w1","tt_"]]
fig, ax = canvas(2.8, 1.8)
# (5) relaxed layout + optimal filling
me_lca = float(rh.merge_errors(sc, maps, dsk, kind)[t].max())
y = np.linspace(p.canvas_origin, p.canvas_origin + L, maps.shape[0], endpoint=False) + L / maps.shape[0] / 2
v = maps[:, t].astype(float); vo = opt[:, t]; vmin, vmax = v.min(), v.max()
ax.plot(y, (v - vmin) / (vmax - vmin), color='#999999', lw=.8, ls='--', label='LCA filling')
ax.plot(y, (vo - vmin) / (vmax - vmin), color='#0072b2', lw=1.0, label='optimal filling')
for i in range(n):
    z, w, u = rowR['z'][i], rowR['w'][i], rowR['x'][i]
    ax.add_patch(Rectangle((z - w / 2, -.28), w, .12, color=cl[i], alpha=.55, lw=0)); ax.plot(u, -.22, 'o', color=cl[i], ms=3.5, mec='k', mew=.4)
    ax.plot(q[i], -.02, 'v', color=cl[i], ms=4)
ax.set_ylim(-.34, 1.08); ax.set_yticks([]); ax.set_xticks([]); ax.legend(loc='upper left', framealpha=.7, handlelength=1.2)
ax.set(title=f'⑤ error {np.max(abs(rowR["x"]-q))/L:.1%}; $\\delta^*$ = {dst[t]:.1f} hPa (LCA {me_lca:.1f})')
save(fig, 'supp_pipeline', '5_filling')
