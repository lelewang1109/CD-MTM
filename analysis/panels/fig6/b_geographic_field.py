"""Independently generate fig6/b_geographic_field as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_witness()
sc, kind, p, ref, L, theta, lo, hi, R, rowsA, mapsA, rowsR, optR, dst, log, H, W, tz, ext, tt, b, i, j, k, q, u = [data[key] for key in ["sc","kind","p","ref","L","theta","lo","hi","R","rowsA","mapsA","rowsR","optR","dst","log","H","W","tz","ext","tt","b","i","j","k","q","u"]]
fig, ax = canvas(2.4, 2.4)
# (b) the 2-D field at the zoomed step with the witness triple and the reference direction
import geo
G = geo.Era5Geo(sc.get('window', Path(__file__).resolve().parents[1] / 'data/real/ERA5_MSLP/ERA5_MSLP_19991117_20000114_12h_arco.nc'), sc['coords'])
ax.imshow(sc.get('fields_smooth', sc['fields'])[tz], origin='lower', extent=G.extent, cmap=fs.FIELD_CMAP, vmin=lo, vmax=hi)
G.graticule(ax); G.coastlines(ax, Path(__file__).resolve().parents[1] / 'data/geo/ne_110m_coastline.geojson')
b, (i, j, k) = W[tz]; ids = sc['ids'][tz]; Pw = np.array([sc['frames'][tz].coordinates[x] for x in ids])
dvec = np.asarray(ref['candidates']['direction']['a']); c0 = np.array([np.mean(G.extent[:2]), np.mean(G.extent[2:])])
ax.annotate('', c0 + 38 * dvec, c0 - 38 * dvec, arrowprops=dict(arrowstyle='->', color='w', lw=1))
for m in range(len(ids)):
    c = '#56b4e9' if m in (i, j) else '#e69f00' if m == k else '#dddddd'
    foot = c0 + ((Pw[m] - c0) @ dvec) * dvec
    if m in (i, j, k): ax.plot([Pw[m, 0], foot[0]], [Pw[m, 1], foot[1]], ':', color=c, lw=.9)
    ax.plot(*Pw[m], 'o', color=c, ms=5 if m in (i, j, k) else 3.5, mec='k', mew=.4)
    if m in (i, j, k):
        ax.text(Pw[m, 0] + 2.5, Pw[m, 1] - 1, f'{float(sc["frames"][tz].values[ids[m]]):.0f}', color='w', fontsize=6, fontweight='bold')
ax.set(xlim=G.extent[:2], ylim=G.extent[2:], xticks=[], yticks=[], aspect='equal')
ax.set_xlabel(f'(b) step {tz}: pressure field (hPa)', fontsize=7.5)
save(fig, 'fig6', 'b_geographic_field')
