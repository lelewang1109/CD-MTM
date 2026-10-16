"""Scalar snapshots, x projections, and three side-by-side temporal maps.
Implementation provenance and quantitative results remain in companion notes.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

import argparse
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,default=ROOT/'results/figures')
args=parser.parse_args()
OUT=args.out;OUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'results/publication2027/bisector_control'
d=np.load(DATA/'bisector_highres_x_three_methods.npz')
r=json.loads((DATA/'bisector_highres_x_three_methods.json').read_text())
a,L=d['geometry']
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':11,'mathtext.fontset':'dejavuserif','pdf.fonttype':42,'svg.fonttype':'none','text.color':'black','axes.labelcolor':'black','xtick.color':'black','ytick.color':'black','axes.spines.top':False,'axes.spines.right':False})
labels={0:'A',1:'B',2:'C'}
colors={0:'#177F9D',1:'#D07823',2:'#8453A1'}
cmap=LinearSegmentedColormap.from_list('mint_teal_blue',[(0.,'#D6EEE6'),(.15,'#B1DDD0'),(.40,'#68BEAD'),(.65,'#3595A6'),(.85,'#286E9E'),(1.,'#244F85')])
fig=plt.figure(figsize=(14,7.0),facecolor='white')
snapshotleft=.145;snapshotright=.902;snapshotwidth=snapshotright-snapshotleft
snap=[0,12,25,38,51,63]
time_limits=(0,63)
def time_x(t):return snapshotleft+snapshotwidth*(t-time_limits[0])/(time_limits[1]-time_limits[0])
fig.text(.077,.981,'Relative distances and absolute position',fontsize=17,fontweight='bold',va='top')
fw=.126;fh=fw*14/7;fb=.650
for t in snap:
 x=time_x(t)-fw/2
 ax=fig.add_axes([x,fb,fw,fh])
 im=ax.imshow(d['field'][t],origin='lower',extent=[0,120,0,120],vmin=0,vmax=r['scalar_range'],cmap=cmap,interpolation='bilinear')
 ax.plot([20,100],[20,100],color='#638B90',lw=.7,ls=(0,(3,3)),alpha=.6)
 ax.plot([35,85],[85,35],color='#638B90',lw=.7,ls=(0,(3,3)),alpha=.6)
 for xy,tr in zip(d['xy'][t],d['track'][t]):
  ax.scatter(xy[0],xy[1],s=35,color=colors[int(tr)],edgecolor='white',lw=.7,zorder=4)
  ax.text(xy[0]+5,xy[1]+4,labels[int(tr)],color='black',fontsize=12,fontweight='bold',path_effects=[pe.withStroke(linewidth=1.7,foreground='white')])
 if t==0:
  ax.annotate('',xy=(52,108),xytext=(10,108),arrowprops=dict(arrowstyle='-|>',color='#2C687A',lw=1.6))
  ax.text(30,94,r'$\mathbf{d}$',ha='center',fontsize=12,color='black')
 ax.set_xticks([]);ax.set_yticks([]);ax.set_title(r'$t='+str(t)+'$',fontsize=12,pad=5)
 for spine in ax.spines.values():spine.set_visible(True);spine.set_linewidth(.7);spine.set_edgecolor('#7E9CA2')
 # Each projection box has exactly the same centre as its scalar snapshot.
 px=fig.add_axes([x,.530,fw,.099]);px.set_xlim(0,120);px.set_ylim(-.30,.40)
 px.set_xticks([]);px.set_yticks([])
 for spine in px.spines.values():spine.set_visible(False)
 px.annotate('',xy=(120,0),xytext=(0,0),arrowprops=dict(arrowstyle='->',color='#6C8D98',lw=1.))
 for track in [0,1,2]:
  i=np.where(d['track'][t]==track)[0][0];q=float(d['q'][t,i])
  px.scatter(q,0,s=42,color=colors[track],edgecolor='white',linewidth=.7,zorder=3)
  px.text(q,.19,labels[track],ha='center',fontsize=11,fontweight='bold')
  px.text(q,-.20,f'{q:g}',ha='center',va='center',fontsize=10)
 # Guides only occupy whitespace between the field and projection.
 fig.add_artist(Line2D([time_x(t),time_x(t)],[.631,fb],transform=fig.transFigure,color='#9AAFB3',lw=.65,ls=(0,(2,3)),zorder=.2))
fig.text(.022,.575,r'$d=x$',fontsize=12)
cbax=fig.add_axes([.028,fb+.030,.009,fh-.060]);cb=fig.colorbar(im,cax=cbax)
cb.set_ticks([0,.5,1.05]);cb.ax.tick_params(labelsize=10,length=2,colors='black');cbax.yaxis.set_ticks_position('left');cbax.set_title('Value',fontsize=11,pad=7);cb.outline.set_edgecolor('#7E9CA2');cb.outline.set_linewidth(.65)
# Each method has its own horizontal time axis; all show the same 64 steps.
axes=[]
panelleft=.080;panelright=.965;panelgap=.065
panelwidth=(panelright-panelleft-2*panelgap)/3
bottom=.085;height=.365
for column,(key,name) in enumerate([('T','TMTM'),('S','ST-MTM'),('R','RG-MTM-R (ours)')]):
 left=panelleft+column*(panelwidth+panelgap)
 ax=fig.add_axes([left,bottom,panelwidth,height]);axes.append(ax)
 ax.set_title(name,fontsize=13,fontweight='bold',pad=12)
 bounds=(d['bounds'+key]-a)/L;matrix=d['map'+key]
 if key!='R':
  if bounds[1]<bounds[0]:matrix=matrix[::-1]
  extent=[-.5,63.5,0,1]
 else:extent=[-.5,63.5,bounds[0],bounds[1]]
 ax.imshow(matrix,origin='lower',aspect='auto',extent=extent,cmap=cmap,vmin=0,vmax=r['scalar_range'],interpolation='nearest')
 ax.set_xlim(*time_limits);ax.set_ylim(0,1)
 for t in snap:ax.axvline(t,color='#557C84',lw=.75,ls=(0,(3,4)),alpha=.55,zorder=2)
 for track in [0,1,2]:
  ys=[]
  for t in range(64):
   i=np.where(d['track'][t]==track)[0][0];y=(d['u'+key][t,i]-a)/L
   if key!='R':y=(y-min(bounds))/abs(bounds[1]-bounds[0])
   ys.append(y)
  ax.plot(range(64),ys,color=colors[track],lw=2.2 if track==1 else 1.25,zorder=4,alpha=1. if track==1 else .90)
  ax.scatter(snap,np.array(ys)[snap],s=27,color=colors[track],edgecolor='white',lw=.65,zorder=5,clip_on=False)
  for t in [0,63]:
   ax.text(1.1 if t==0 else 61.9,ys[t],labels[track],ha='left' if t==0 else 'right',va='center',fontsize=11,fontweight='bold',color='black',path_effects=[pe.withStroke(linewidth=1.9,foreground='white')])
 ax.tick_params(labelsize=10,length=3,colors='black');ax.set_xticks(snap)
 ax.set_xlabel('Time',fontsize=12,labelpad=5)
 if key!='R':ax.set_yticks([0,.5,1]);ax.set_ylabel('Map',fontsize=11,labelpad=9)
 else:
  ticks=np.array([0,20,40,60,80,100,120]);ax.set_yticks(ticks/120);ax.set_yticklabels([str(v) for v in ticks]);ax.set_ylabel(r'Absolute $x$',fontsize=12,labelpad=7)
  for track,xx in [(0,20),(2,100)]:ax.axhline(xx/120,color=colors[track],ls=(0,(5,5)),lw=.8,alpha=.8)
 for spine in ax.spines.values():spine.set_visible(True);spine.set_linewidth(.7);spine.set_edgecolor('#7E9CA2')
# Verify equal panel geometry and identical relative time positions in each map.
for previous,current in zip(axes,axes[1:]):
 assert previous.get_position().x1<current.get_position().x0
 assert np.allclose(previous.get_position().bounds[1::2],current.get_position().bounds[1::2])
for ax in axes:
 box=ax.get_position()
 for t in snap:
  fx=fig.transFigure.inverted().transform(ax.transData.transform((t,.5)))[0]
  expected=(t-time_limits[0])/(time_limits[1]-time_limits[0])
  assert abs((fx-box.x0)/box.width-expected)<1e-10,(t,fx,expected)
for extension in ['png','svg']:
 fig.savefig(OUT/('rgmtm_bisector_absolute_position.'+extension),dpi=240,bbox_inches='tight',facecolor='white')
plt.close(fig)
print('Saved side-by-side method maps with equal panel sizes, identical time ranges, and consistent A/B/C markers.')
