"""Independently generate fig1/middle_tree_kept as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_teaser()
sc, T, lo, hi, p, ref, L, theta, st, Ust, cert_pt, st_pt, H, F, errR, dstar, mapsA, optR, rowsA, rowsR, t, ymax, SN = [data[key] for key in ["sc","T","lo","hi","p","ref","L","theta","st","Ust","cert_pt","st_pt","H","F","errR","dstar","mapsA","optR","rowsA","rowsR","t","ymax","SN"]]
fig, ax = canvas(2.2, 1.8)
# (b)
ax.imshow(mapsA, origin='lower', aspect='auto', extent=[-.5, T - .5, p.canvas_origin, p.canvas_origin + L],
                                         vmin=lo, vmax=hi, cmap=fs.FIELD_CMAP)
tracks(ax, sc, [r['x'] for r in rowsA]); ax.set(xlabel='time step', yticks=[])

time_marks(ax, sc, SN)
save(fig, 'fig1', 'middle_tree_kept')
