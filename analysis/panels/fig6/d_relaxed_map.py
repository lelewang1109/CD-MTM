"""Independently generate fig6/d_relaxed_map as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_witness()
sc, kind, p, ref, L, theta, lo, hi, R, rowsA, mapsA, rowsR, optR, dst, log, H, W, tz, ext, tt, b, i, j, k, q, u = [data[key] for key in ["sc","kind","p","ref","L","theta","lo","hi","R","rowsA","mapsA","rowsR","optR","dst","log","H","W","tz","ext","tt","b","i","j","k","q","u"]]
fig, ax = canvas(2.5, 1.8)
# (c)
ax.imshow(optR[:, W0:W1], origin='lower', aspect='auto', extent=ext, cmap=fs.FIELD_CMAP, vmin=lo, vmax=hi)
for t in range(W0, W1):
    if R['frame_log'][t]['relaxed_nodes']: ax.plot(t, p.canvas_origin + .975 * L, 'v', color='#009e73', ms=3)
ax.axvline(tz, color='w', ls=':', lw=.7); ax.set(xlabel='time step', yticks=[])
save(fig, 'fig6', 'd_relaxed_map')
