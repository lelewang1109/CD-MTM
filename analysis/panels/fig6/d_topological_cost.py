"""Independently generate fig6/d_topological_cost as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_witness()
sc, kind, p, ref, L, theta, lo, hi, R, rowsA, mapsA, rowsR, optR, dst, log, H, W, tz, ext, tt, b, i, j, k, q, u = [data[key] for key in ["sc","kind","p","ref","L","theta","lo","hi","R","rowsA","mapsA","rowsR","optR","dst","log","H","W","tz","ext","tt","b","i","j","k","q","u"]]
fig, ax = canvas(2.5, 0.55)
bot = ax; bot.bar(tt, dst[W0:W1], color='#0072b2', width=.85); bot.tick_params(labelbottom=False, labelleft=False)
bot.text(.3, .95, f'$\\delta^*$ (max {max(dst[W0:W1]):.0f} hPa)', transform=bot.transAxes, ha='left', va='top', fontsize=6.5, color='#0072b2')
ax.set_xlim(W0 - .5, W1 - .5)
ax.tick_params(labelbottom=False)
save(fig, 'fig6', 'd_topological_cost')
