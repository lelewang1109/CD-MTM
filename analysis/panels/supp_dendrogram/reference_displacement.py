"""Independently generate supp_dendrogram/reference_displacement as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_dendrogram()
X, xy, n, q, olo, p, tau, disp_olo, ref, disp_ref = [data[key] for key in ["X","xy","n","q","olo","p","tau","disp_olo","ref","disp_ref"]]
fig, ax = canvas(2.2, 2.3)
disp = disp_ref
ax.plot(disp / n * 100, np.arange(n), color='#0072b2', lw=.35)
ax.axvline(tau / n * 100, color='#d55e00', ls='--', lw=.8, label='$\\tau^*$')
ax.set(xlabel='displacement (%)', ylabel='row', ylim=(0,n), xlim=(0,100))
ax.legend(loc='lower right', handlelength=1.2)
save(fig, 'supp_dendrogram', 'reference_displacement')
