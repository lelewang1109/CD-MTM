"""Independently generate fig1/bottom_snapshot_4 as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_teaser()
sc, T, lo, hi, p, ref, L, theta, st, Ust, cert_pt, st_pt, H, F, errR, dstar, mapsA, optR, rowsA, rowsR, t, ymax, SN = [data[key] for key in ["sc","T","lo","hi","p","ref","L","theta","st","Ust","cert_pt","st_pt","H","F","errR","dstar","mapsA","optR","rowsA","rowsR","t","ymax","SN"]]
fig, ax = canvas(2.2, 1.7)
import geo
G = geo.Era5Geo(sc.get('window', ROOT_NC), sc['coords'])
k = 3; tt_ = SN[k]
a = ax
a.imshow(sc.get('fields_smooth', sc['fields'])[tt_], origin='lower', extent=G.extent, cmap=fs.FIELD_CMAP, vmin=lo, vmax=hi)
G.graticule(a); G.coastlines(a, COAST)
P_ = np.array([sc['frames'][tt_].coordinates[i] for i in sc['ids'][tt_]])
a.plot(P_[:, 0], P_[:, 1], 'o', mfc='none', mec='w', mew=.8, ms=4)
if k == 0:
    dvec = np.asarray(ref['candidates']['direction']['a']); c0 = np.array([np.mean(G.extent[:2]), np.mean(G.extent[2:])])
    a.annotate('', c0 + 25 * dvec, c0 - 25 * dvec, arrowprops=dict(arrowstyle='->', color=fs.BLUE_LIGHT, lw=1.2))
a.set(xlim=G.extent[:2], ylim=G.extent[2:], xticks=[], yticks=[], aspect='equal')
a.set_title(f'{k + 1}: {sc["dates"][tt_][5:13]}h, $H$ = {H[tt_] / L:.0%}', fontsize=6.5, pad=2)
save(fig, 'fig1', 'bottom_snapshot_4')
