"""Independently generate fig1/top_tree_kept as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_teaser()
sc, T, lo, hi, p, ref, L, theta, st, Ust, cert_pt, st_pt, H, F, errR, dstar, mapsA, optR, rowsA, rowsR, t, ymax, SN = [data[key] for key in ["sc","T","lo","hi","p","ref","L","theta","st","Ust","cert_pt","st_pt","H","F","errR","dstar","mapsA","optR","rowsA","rowsR","t","ymax","SN"]]
fig, ax = canvas(2.2, 0.8)
top = ax; top.set_ylim(0, ymax); top.tick_params(labelleft=False)
top.bar(t, F / L * 100, color=fs.GRAY, width=.9, label='space cost')
top.bar(t, H / L * 100, bottom=F / L * 100, color=fs.CORAL, width=.9, label='hierarchy cost $H$')
top.axhline(theta / L * 100, color='k', ls=':', lw=.6)
top.set(title='(b) Merge tree kept: certificate $\\tau^*$'); top.legend(loc='upper left', ncol=2, framealpha=.7, handlelength=1)
ax.set_xlim(-.5, T - .5)
ax.tick_params(labelbottom=False)
save(fig, 'fig1', 'top_tree_kept')
