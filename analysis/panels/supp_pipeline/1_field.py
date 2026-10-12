"""Independently generate supp_pipeline/1_field as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_pipeline()
ds, sc, kind, p, ref, L, R, t, fr, ids, q, n, lg0, lgR, rowA, rowR, cols, cl, flat, rowsR, maps, dsk, opt, dst, w0, w1, tt_ = [data[key] for key in ["ds","sc","kind","p","ref","L","R","t","fr","ids","q","n","lg0","lgR","rowA","rowR","cols","cl","flat","rowsR","maps","dsk","opt","dst","w0","w1","tt_"]]
fig, ax = canvas(2.8, 1.8)
# (1) field
C = np.asarray(sc['coords']); lo, hi = C.min(0), C.max(0)
import geo; G = geo.Era5Geo(sc['window'], C) if 'window' in sc else None
ax.imshow(sc.get('fields_smooth', sc['fields'])[t], origin='lower', extent=G.extent if G else [lo[0], hi[0], lo[1], hi[1]], cmap=fs.FIELD_CMAP)
if G: G.graticule(ax); G.coastlines(ax, COAST); ax.set(xlim=G.extent[:2], ylim=G.extent[2:])
P = np.array([fr.coordinates[k] for k in ids])
for i in range(n): ax.plot(P[i, 0], P[i, 1], 'o', color=cl[i], ms=4, mec='w', mew=.5)
a = np.asarray(ref['candidates']['direction']['a']); c0 = (lo + hi) / 2; s = .38 * (hi - lo).min()
ax.annotate('', c0 + s * a, c0 - s * a, arrowprops=dict(arrowstyle='->', color='w', lw=1.4))
ax.set(title='① field, extrema, reference direction', xticks=[], yticks=[])
save(fig, 'supp_pipeline', '1_field')
