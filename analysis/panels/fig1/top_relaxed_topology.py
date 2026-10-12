"""Independently generate fig1/top_relaxed_topology as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_teaser()
sc, T, lo, hi, p, ref, L, theta, st, Ust, cert_pt, st_pt, H, F, errR, dstar, mapsA, optR, rowsA, rowsR, t, ymax, SN = [data[key] for key in ["sc","T","lo","hi","p","ref","L","theta","st","Ust","cert_pt","st_pt","H","F","errR","dstar","mapsA","optR","rowsA","rowsR","t","ymax","SN"]]
fig, ax = canvas(2.2, 0.5)
bot = ax; bot.bar(t, dstar, color=fs.BLUE, width=.9); bot.tick_params(labelleft=False)
bot.text(.99, .9, f'topological cost $\\delta^*$ (max {max(dstar):.0f} hPa)', transform=bot.transAxes, ha='right', va='top', fontsize=6.5, color=fs.BLUE)
ax.set_xlim(-.5, T - .5)
ax.tick_params(labelbottom=False)
save(fig, 'fig1', 'top_relaxed_topology')
