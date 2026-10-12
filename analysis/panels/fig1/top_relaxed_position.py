"""Independently generate fig1/top_relaxed_position as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_teaser()
sc, T, lo, hi, p, ref, L, theta, st, Ust, cert_pt, st_pt, H, F, errR, dstar, mapsA, optR, rowsA, rowsR, t, ymax, SN = [data[key] for key in ["sc","T","lo","hi","p","ref","L","theta","st","Ust","cert_pt","st_pt","H","F","errR","dstar","mapsA","optR","rowsA","rowsR","t","ymax","SN"]]
fig, ax = canvas(2.2, 0.5)
top = ax; top.bar(t, errR / L * 100, color=fs.GREEN, width=.9); top.set_ylim(0, ymax / 2)
top.set_title(f'(c) Relaxed ($\\kappa$ = {int(KAPPA*100)}%), optimal filling'); top.tick_params(labelleft=False)
top.text(.99, .9, 'max position error', transform=top.transAxes, ha='right', va='top', fontsize=6.5, color=fs.GREEN)
ax.set_xlim(-.5, T - .5)
ax.tick_params(labelbottom=False)
save(fig, 'fig1', 'top_relaxed_position')
