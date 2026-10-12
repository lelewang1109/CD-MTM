"""Independently generate supp_pipeline/6_map as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_pipeline()
ds, sc, kind, p, ref, L, R, t, fr, ids, q, n, lg0, lgR, rowA, rowR, cols, cl, flat, rowsR, maps, dsk, opt, dst, w0, w1, tt_ = [data[key] for key in ["ds","sc","kind","p","ref","L","R","t","fr","ids","q","n","lg0","lgR","rowA","rowR","cols","cl","flat","rowsR","maps","dsk","opt","dst","w0","w1","tt_"]]
fig, ax = canvas(2.8, 1.8)
# (6) map excerpt with strips
w0, w1 = max(0, t - 18), min(len(rowsR), t + 4)
ax.imshow(opt[:, w0:w1], origin='lower', aspect='auto', extent=[w0 - .5, w1 - .5, p.canvas_origin, p.canvas_origin + L], cmap=fs.FIELD_CMAP,
          vmin=np.min(sc['fields']), vmax=np.max(sc['fields']))
ax.axvline(t, color='w', lw=.8, ls=':')
ax.set_yticks([]); ax.set_xlabel('time step')
save(fig, 'supp_pipeline', '6_map')
