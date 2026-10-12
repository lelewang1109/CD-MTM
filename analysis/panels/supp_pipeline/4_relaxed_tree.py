"""Independently generate supp_pipeline/4_relaxed_tree as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_pipeline()
ds, sc, kind, p, ref, L, R, t, fr, ids, q, n, lg0, lgR, rowA, rowR, cols, cl, flat, rowsR, maps, dsk, opt, dst, w0, w1, tt_ = [data[key] for key in ["ds","sc","kind","p","ref","L","R","t","fr","ids","q","n","lg0","lgR","rowA","rowR","cols","cl","flat","rowsR","maps","dsk","opt","dst","w0","w1","tt_"]]
fig, ax = canvas(2.8, 1.8)
# (4) relaxation
oR = list(rowR['order'])
draw_tree(ax, fr, {ids[i]: k for k, i in enumerate(oR)}, flat=set(flat))
for k, i in enumerate(oR): ax.plot(k, fr.values[ids[i]], 'o', color=cl[i], ms=3.5, mec='k', mew=.3)
ax.set(title=f'④ relax: flatten {len(flat)} weak merge{"s" if len(flat) > 1 else ""} (dashed)', xticks=[])
save(fig, 'supp_pipeline', '4_relaxed_tree')
