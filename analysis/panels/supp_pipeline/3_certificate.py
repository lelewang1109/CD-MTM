"""Independently generate supp_pipeline/3_certificate as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_pipeline()
ds, sc, kind, p, ref, L, R, t, fr, ids, q, n, lg0, lgR, rowA, rowR, cols, cl, flat, rowsR, maps, dsk, opt, dst, w0, w1, tt_ = [data[key] for key in ["ds","sc","kind","p","ref","L","R","t","fr","ids","q","n","lg0","lgR","rowA","rowR","cols","cl","flat","rowsR","maps","dsk","opt","dst","w0","w1","tt_"]]
fig, ax = canvas(2.8, 1.8)
# (3) certificate
layout_row(ax, rowA, q, 0, cl, L, p.canvas_origin)
ax.set(title=f'③ certificate $\\tau^*$ = {lg0["tau_hier"]/L:.0%}, $\\tau_{{free}}$ = {lg0["tau_free"]/L:.0%}', xticks=[])
save(fig, 'supp_pipeline', '3_certificate')
