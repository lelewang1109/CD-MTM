"""Independently generate supp_pipeline/6_error_strip as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_pipeline()
ds, sc, kind, p, ref, L, R, t, fr, ids, q, n, lg0, lgR, rowA, rowR, cols, cl, flat, rowsR, maps, dsk, opt, dst, w0, w1, tt_ = [data[key] for key in ["ds","sc","kind","p","ref","L","R","t","fr","ids","q","n","lg0","lgR","rowA","rowR","cols","cl","flat","rowsR","maps","dsk","opt","dst","w0","w1","tt_"]]
fig, ax = canvas(2.8, 0.7)
top = ax; tt_ = np.arange(w0, w1)
top.bar(tt_, [np.max(abs(r['x'] - r['reference'])) / L * 100 for r in rowsR[w0:w1]], color='#009e73', width=.8)

top.set_xlim(w0 - .5, w1 - .5); top.set_xticks([]); top.set_yticks([])
top.set_title('⑥ map with error strip')
save(fig, 'supp_pipeline', '6_error_strip')
