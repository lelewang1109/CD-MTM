"""Independently generate supp_dendrogram/reference_heatmap as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

data = prepare_dendrogram()
X, xy, n, q, olo, p, tau, disp_olo, ref, disp_ref = [data[key] for key in ["X","xy","n","q","olo","p","tau","disp_olo","ref","disp_ref"]]
fig, ax = canvas(3.4, 2.3)
order = ref
ax.imshow(X[order], aspect='auto', cmap='Blues', origin='lower', interpolation='nearest')
ax.set(title='Geographic order: fire time series', xlabel='time step (2 days)', ylabel='row (10-km cell)')
save(fig, 'supp_dendrogram', 'reference_heatmap')
