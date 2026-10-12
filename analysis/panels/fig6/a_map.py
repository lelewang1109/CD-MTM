"""Independently generate fig6/a_map as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_witness()
sc, kind, p, ref, L, theta, lo, hi, R, rowsA, mapsA, rowsR, optR, dst, log, H, W, tz, ext, tt, b, i, j, k, q, u = [data[key] for key in ["sc","kind","p","ref","L","theta","lo","hi","R","rowsA","mapsA","rowsR","optR","dst","log","H","W","tz","ext","tt","b","i","j","k","q","u"]]
fig, ax = canvas(2.5, 1.8)
# (a)
ax.imshow(mapsA[:, W0:W1], origin='lower', aspect='auto', extent=ext, cmap=fs.FIELD_CMAP, vmin=lo, vmax=hi)
for t, (b, (i, j, k)) in W.items():
    u = rowsA[t]['x']; ax.plot([t, t], [u[i], u[j]], color='#56b4e9', lw=1.6, alpha=.95, solid_capstyle='round')
    ax.plot(t, u[k], 'o', mfc='none', mec='#e69f00', mew=1.1, ms=4)
ax.axvline(tz, color='w', ls=':', lw=.7); ax.set(xlabel='time step', yticks=[], ylabel='1-D position')
save(fig, 'fig6', 'a_map')
