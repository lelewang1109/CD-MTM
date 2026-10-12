"""Independently generate fig4/wildfire as PDF and PNG."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *

fig, ax = canvas(3.4, 1.6)
n = 'wildfire'; label = 'Wildfire 2019'
c = json.loads((tr.OUT / f'replicate_{n}.json').read_text())['certificate']
H = np.array(c['H_per_frame']) * 100; F = np.array(c['F_per_frame']) * 100; t = np.arange(len(H))
ax.bar(t, F, color='#999999', width=.9, label='space cost $\\tau_{\\rm free}$')
ax.bar(t, H, bottom=F, color='#d55e00', width=.9, label='hierarchy cost $H$')
ax.axhline(2, color='k', ls=':', lw=.8, label='$\\theta$ = 2%')
ax.set(title=f"{label}: {c['conflict_frames']}/{c['frames']} with $H>\\theta$", xlabel='time step', xlim=(-1, len(H)))
ax.set_ylabel('% of axis')
ax.legend(loc='upper center', framealpha=.8, handlelength=1.2)
save(fig, 'fig4', 'wildfire')
