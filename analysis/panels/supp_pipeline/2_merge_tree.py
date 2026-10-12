"""Independently generate supp_pipeline/2_merge_tree as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_pipeline()
ds, sc, kind, p, ref, L, R, t, fr, ids, q, n, lg0, lgR, rowA, rowR, cols, cl, flat, rowsR, maps, dsk, opt, dst, w0, w1, tt_ = [data[key] for key in ["ds","sc","kind","p","ref","L","R","t","fr","ids","q","n","lg0","lgR","rowA","rowR","cols","cl","flat","rowsR","maps","dsk","opt","dst","w0","w1","tt_"]]
fig, ax = canvas(2.8, 1.8)
# (2) merge tree, legal order of layout A
oA = list(rowA['order'])
draw_tree(ax, fr, {ids[i]: k for k, i in enumerate(oA)})
for k, i in enumerate(oA): ax.plot(k, fr.values[ids[i]], 'o', color=cl[i], ms=3.5, mec='k', mew=.3)
ax.set(title='② merge tree $T_t$ (join tree, hPa)', xticks=[])
save(fig, 'supp_pipeline', '2_merge_tree')
