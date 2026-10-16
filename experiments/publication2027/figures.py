"""Replot compact paper figures from saved records; never rerun experiments."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/legacy_publication/pacificvis2027-restructured/figures'
plt.rcParams.update({'font.size':7,'axes.titlesize':7,'axes.labelsize':7,'xtick.labelsize':6.5,'ytick.labelsize':6.5,'legend.fontsize':6.5,'axes.linewidth':.5,'xtick.major.size':2,'ytick.major.size':2,'pdf.fonttype':42,'svg.fonttype':'none'})
NAMES=['era5','wildfire','olr','pm25','ring','gaussians']
LABELS=['ERA5','Fire','OLR','PM2.5','Ring','Gaussians']
fig,axs=plt.subplots(1,4,figsize=(7,1.47))
for ax,name,label in zip(axs,NAMES,LABELS):
 c=json.loads((ROOT/'results'/f'replicate_{name}.json').read_text())['certificate']
 h=np.asarray(c['H_per_frame'])*100; f=np.asarray(c['F_per_frame'])*100;t=np.arange(len(h))
 ax.bar(t,f,color='#999999',width=.9)
 ax.bar(t,h,bottom=f,color='#d55e00',width=.9)
 ax.axhline(2,color='black',ls=':',lw=.65)
 ax.set_title(f'{label}: {c["conflict_frames"]}/{c["frames"]}')
 ax.set_xlim(-1,len(h));ax.set_xlabel('time step')
 ax.spines[['top','right']].set_visible(False)
axs[0].set_ylabel('% of axis')
fig.legend(handles=[Patch(color='#999999',label=r'packing $\tau_{\rm free}$'),Patch(color='#d55e00',label=r'hierarchy $H$'),Line2D([0],[0],color='k',ls=':',lw=.65,label=r'$\theta=2\%$')],loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.5,1.005))
fig.subplots_adjust(left=.065,right=.98,bottom=.28,top=.71,wspace=.37)
for ext in ['pdf','png','svg']:fig.savefig(OUT/f'fig_displacement_compact.{ext}',dpi=250)
plt.close(fig)
fig,axs=plt.subplots(2,3,figsize=(7,2.26))
for ax,name,label in zip(axs.ravel(),NAMES,LABELS):
 r=json.loads((ROOT/'results'/f'attainable_{name}.json').read_text())
 d=[x['delta']*100 for x in r['frontier']]
 ax.step(d,[x['F']*100 for x in r['frontier']],where='post',color='#0072b2',lw=1)
 ax.step(d,[x['Phi']*100 for x in r['frontier']],where='post',color='k',lw=.65,ls='--')
 for o in r['ours']:
  e=o['E_share']*100;a=o['D_opt_share']*100;b=o['D_lca_share']*100
  ax.plot([a,b],[e,e],color='#009e73',lw=.5)
  ax.plot(b,e,'o',mfc='white',mec='#009e73',ms=3.2,mew=.7)
  ax.plot(a,e,'o',color='#009e73',ms=3)
 ymax=max([x['F']*100 for x in r['frontier']]+[x['E_share']*100 for x in r['ours']]+[.1])
 ax.set_ylim(0,1.12*ymax);ax.set_xlim(-2,72);ax.set_title(label,pad=2)
 ax.spines[['top','right']].set_visible(False)
for ax in axs[1,:]:ax.set_xlabel(r'$d_{\rm top}$ (% of value range)')
for ax in axs[:,0]:ax.set_ylabel(r'$\tau(\pi)$ (% axis)')
fig.legend(handles=[Line2D([0],[0],color='#0072b2',label='$F$'),Line2D([0],[0],color='k',ls='--',label=r'$\Phi$'),Line2D([0],[0],color='#009e73',marker='o',ls='none',ms=3,label='optimal filling'),Line2D([0],[0],color='#009e73',marker='o',mfc='white',ls='none',ms=3,label='LCA filling')],loc='upper center',ncol=4,frameon=False,bbox_to_anchor=(.5,1.01),handlelength=1.5)
fig.subplots_adjust(left=.07,right=.995,bottom=.18,top=.77,wspace=.3,hspace=.58)
for ext in ['pdf','png','svg']:fig.savefig(OUT/f'fig_frontier_compact.{ext}',dpi=250)
plt.close(fig)
print('Compact figures written from saved evidence.')

# A code-native overview of the implemented construction.
from matplotlib.patches import FancyBboxPatch
fig,ax=plt.subplots(figsize=(7,0.88))
ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
steps=[('Input','Fields, trees, tracks'),('Diagnose','Packing + hierarchy'),('Construct','Keep tree or relax'),('Fill','Values + barriers'),('Disclose','Map + error strips')]
for i,(title,subtitle) in enumerate(steps):
 x=.006+i*.202
 ax.add_patch(FancyBboxPatch((x,.22),.18,.68,boxstyle='round,pad=0.006',lw=.7,ec='#35566a',fc='#f2f5f7'))
 ax.text(x+.09,.69,str(i+1)+'. '+title,ha='center',va='center',fontsize=8,fontweight='bold',color='#24475b')
 ax.text(x+.09,.40,subtitle,ha='center',va='center',fontsize=6.8)
 if i<4:ax.annotate('',xy=(x+.196,.56),xytext=(x+.184,.56),arrowprops=dict(arrowstyle='->',lw=.8,color='#35566a'))
fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
for ext in ['pdf','png','svg']:fig.savefig(OUT/f'fig_method_overview.{ext}',dpi=250)
plt.close(fig)
