"""Shared active-real-dataset certificate figure, using completed evidence only."""
from pathlib import Path
import sys,json
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import task_reference as tr,figstyle as fs
from dataset_suite import REAL_DATASETS,LABELS
fs.apply();fig,axs=tr.plt.subplots(2,2,figsize=(fs.TEXT_W,2.6),layout='constrained')
for ax,n in zip(axs.ravel(),REAL_DATASETS):
 c=json.loads((tr.OUT/f'replicate_{n}.json').read_text())['certificate']
 H=np.array(c['H_per_frame'])*100;F=np.array(c['F_per_frame'])*100;t=np.arange(len(H))
 ax.bar(t,F,color='#999999',width=.9,label=r'space cost $\tau_{\mathrm{free}}$')
 ax.bar(t,H,bottom=F,color='#d55e00',width=.9,label=r'hierarchy cost $H$')
 ax.axhline(2,color='k',ls=':',lw=.8,label=r'$\theta=2\%$')
 ax.set(title=f'{LABELS[n]}: {c["conflict_frames"]}/{c["frames"]} conflict frames',xlabel='time step',ylabel='% of axis',xlim=(-1,len(H)))
for ax in axs.ravel()[len(REAL_DATASETS):]:ax.set_visible(False)
handles,labels=axs[0,0].get_legend_handles_labels()
fig.legend(handles,labels,loc='upper center',ncol=3,fontsize=6,frameon=False,bbox_to_anchor=(.5,1.04))
fig.set_constrained_layout_pads(h_pad=.08,w_pad=.04)

for ext in ('png','pdf'):fig.savefig(tr.OUT/f'fig_rq1.{ext}',dpi=300,bbox_inches='tight')
tr.plt.close(fig)
