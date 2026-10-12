"""Independently generate fig1/top_stmtm as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_teaser()
sc, T, lo, hi, p, ref, L, theta, st, Ust, cert_pt, st_pt, H, F, errR, dstar, mapsA, optR, rowsA, rowsR, t, ymax, SN = [data[key] for key in ["sc","T","lo","hi","p","ref","L","theta","st","Ust","cert_pt","st_pt","H","F","errR","dstar","mapsA","optR","rowsA","rowsR","t","ymax","SN"]]
fig, ax = canvas(2.2, 0.8)
top = ax; top_a = top
top.bar(t, np.array(cert_pt) / L * 100, color='#555555', width=.9, label='unavoidable')
top.bar(t, (np.array(st_pt) - np.array(cert_pt)) / L * 100, bottom=np.array(cert_pt) / L * 100, color='#bbbbbb', width=.9, label='avoidable')
top.set(title='(a) ST-MTM: deviation of its order', ylabel='% axis', ylim=(0, ymax))
top.legend(loc='upper left', ncol=2, framealpha=.7, handlelength=1)
ax.set_xlim(-.5, T - .5)
ax.tick_params(labelbottom=False)
save(fig, 'fig1', 'top_stmtm')
