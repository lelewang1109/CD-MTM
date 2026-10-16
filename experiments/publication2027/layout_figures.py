"""Draw publication figures from numeric evidence. --prepare refreshes render exports;
otherwise bundled exports reproduce every new figure without raw observations.
"""
from pathlib import Path
import argparse,csv,hashlib,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'analysis'),str(ROOT/'src'),str(ROOT)]
import figstyle as fs
from provenance import verify_saved_file
OUT=ROOT/'results/legacy_publication/pacificvis2027-restructured/figures';DATA=ROOT/'results/publication2027/figure_data'
NAMES=['era5','wildfire','olr','pm25'];LABELS=['ERA5','Fire','OLR','PM2.5'];COLS=['#666666',fs.BLUE,fs.GREEN]
def read(name):return json.loads((ROOT/'results'/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(fig,name):
 for ext in ['pdf','png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=300)
 plt.close(fig)
def prepare(name):
 import replicate as rp,relax_hierarchy as rh,filling as fl
 from fig_witness import witness
 ds=rp.LOADERS[name]();sc=ds['sc'];r=rh.run(ds,.2,make_figure=False,return_internal=True)
 I=r['_internal'];p=I['p'];ref=I['ref'];T=len(sc['ids']);n=max(map(len,sc['ids']))
 a={'field':np.asarray(sc.get('fields_smooth',sc['fields'])),'coords':sc['coords'],'geometry':np.array([p.canvas_origin,p.canvas]),'direction':np.asarray(ref['candidates']['direction']['a'])}
 for key,shape in [('q',(T,n)),('xy',(T,n,2)),('value',(T,n))]:a[key]=np.full(shape,np.nan)
 a['track']=np.full((T,n),-1,dtype=int);a['witness']=np.full((T,3),-1,dtype=int)
 for t,ids in enumerate(sc['ids']):
  k=len(ids);a['q'][t,:k]=ref['qs'][t];a['xy'][t,:k]=[sc['frames'][t].coordinates[i] for i in ids];a['value'][t,:k]=[sc['frames'][t].values[i] for i in ids];a['track'][t,:k]=sc['tracks'][t]
  _,triple=witness(sc['frames'][t],ids,np.asarray(ref['qs'][t]))
  if triple:a['witness'][t]=triple
 for mode,key in [('A','A_full_hierarchy'),('R','R_relaxed')]:
  rows=I['results'][key]['_rows'];matrix,skeletons,_=rh.render(sc,rows,p,ds['nominal']);matrix=matrix.astype(float);a['u'+mode]=np.full((T,n),np.nan);delta=[]
  for t,(fr,sk,row) in enumerate(zip(sc['frames'],skeletons,rows)):
   a['u'+mode][t,:len(sc['ids'][t])]=row['x']
   if mode=='R':matrix[:,t],d=fl.optimal_fill(matrix[:,t],list(sk.ordering),sk.anchors,fr,sc['trees'][0].kind);delta.append(d)
  a['map'+mode]=matrix
  if mode=='R':a['delta']=np.asarray(delta)
 a['H']=np.array([x['tau_hier']-x['tau_free'] for x in r['frame_log']]);a['F']=np.array([x['tau_free'] for x in r['frame_log']])
 for mode in ['A','R']:a['pos'+mode]=np.nanmax(abs(a['u'+mode]-a['q']),axis=1)
 a['dates']=np.array(sc.get('dates',[str(t) for t in range(T)]));expected=read('eval_projection.json')[name]['dstar']['R 20%']
 assert abs(a['delta'].mean()/r['field_range']-expected['mean_share'])<2e-5
 assert abs(a['delta'].max()/r['field_range']-expected['max_share'])<2e-5
 pth=DATA/f'{name}_render.npz';np.savez_compressed(pth,**a)
 sources=sorted(p for folder in ['src','analysis','experiments/era5'] for p in (ROOT/folder).rglob('*.py') if '__pycache__' not in p.parts and 'visualization' not in p.parts and not p.stem.startswith('fig_'))+[ROOT/'analysis/fig_witness.py']
 report={'dataset':name,'frames':T,'range':r['field_range'],'cap':.2,'source_sha256':{str(x.relative_to(ROOT)):sha(x) for x in sources},'arrays_sha256':sha(pth),'mean_scalar_share':a['delta'].mean()/r['field_range'],'max_scalar_share':a['delta'].max()/r['field_range'],'execution':'fresh deterministic construction and optimal rendering; checked against saved evaluation'}
 (DATA/f'{name}_render.json').write_text(json.dumps(report,indent=2)+'\n');print('Verified numeric renders:',name,flush=True)
def load(name):
 p=DATA/f'{name}_render.npz';m=json.loads((DATA/f'{name}_render.json').read_text());assert sha(p)==m['arrays_sha256']
 for source,h in m['source_sha256'].items():verify_saved_file(ROOT,source,h)
 with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in z.files}
def event(ev,n,m):return next(r for r in ev[n]['proxy'] if r['method']==m and r['k']==2 and r['eps']==.02)
def decorate(ax):ax.spines[['top','right']].set_visible(False)
def tracks(ax,d,mode,start,end):
 for track in sorted(set(d['track'][start:end].ravel())-{-1}):
  ts=[];us=[]
  for t in range(start,end):
   ix=np.flatnonzero(d['track'][t]==track);ts.append(t);us.append((d['u'+mode][t,ix[0]]-d['geometry'][0])/d['geometry'][1] if len(ix) else np.nan)
  ax.plot(ts,us,color='white',lw=.5,alpha=.75)
def spatial(ax,d,t):
 c=d['coords'];extent=[c[:,0].min(),c[:,0].max(),c[:,1].min(),c[:,1].max()]
 im=ax.imshow(d['field'][t],origin='lower',extent=extent,cmap=fs.FIELD_CMAP,vmin=d['field'].min(),vmax=d['field'].max(),aspect='auto')
 tri=d['witness'][t];cols={int(tri[0]):fs.BLUE,int(tri[1]):fs.BLUE_LIGHT,int(tri[2]):fs.CORAL} if tri[0]>=0 else {}
 for i,xy in enumerate(d['xy'][t]):
  if not np.isfinite(xy).all():continue
  ax.plot(*xy,'o',color=cols.get(i,'#dddddd'),ms=4,mec='black',mew=.4)
  if i in cols:
   near_right=xy[0]>extent[0]+.85*(extent[1]-extent[0]);near_top=xy[1]>extent[2]+.85*(extent[3]-extent[2])
   ax.annotate(['A','B','C'][list(tri).index(i)],xy,xytext=(-5 if near_right else 3,-9 if near_top else 3),ha='right' if near_right else 'left',textcoords='offset points',fontsize=7,fontweight='bold',bbox=dict(fc='white',alpha=.8,ec='none',pad=.5))
 coast=ROOT/'data/geo/ne_110m_coastline.geojson'
 if coast.exists():
  for f in json.loads(coast.read_text())['features']:
   g=f['geometry'];lines=g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
   for line in lines:
    pts=np.asarray(line);ax.plot(pts[:,0],pts[:,1],color='#333333',lw=.3,alpha=.7)
 centre=np.array([(extent[0]+extent[1])/2,(extent[2]+extent[3])/2]);direction=d['direction'];direction=direction/np.linalg.norm(direction)
 length=.32*min(extent[1]-extent[0],extent[3]-extent[2])
 ax.annotate('',centre+length*direction,centre-length*direction,arrowprops=dict(arrowstyle='->',color='#333333',lw=.75))
 for i in cols:
  xy=d['xy'][t,i];foot=centre+np.dot(xy-centre,direction)*direction
  ax.plot([xy[0],foot[0]],[xy[1],foot[1]],':',color=cols[i],lw=.65,alpha=.8)
 ax.set(xlim=extent[:2],ylim=extent[2:],xticks=[],yticks=[]);ax.set_xlabel('longitude / latitude',fontsize=6.5);return im
def teaser(d):
 t=48;start,end=0,len(d['H']);L=d['geometry'][1]
 fig=plt.figure(figsize=(7,2.3));gs=fig.add_gridspec(1,3,width_ratios=[1,1.3,1.3],left=.03,right=.985,bottom=.19,top=.85,wspace=.36)
 ax=fig.add_subplot(gs[0]);im=spatial(ax,d,t);ax.set_title('(a) Spatial field: step 48');ax.set_xlabel('');cb=fig.colorbar(im,cax=fig.add_axes([.03,.08,.21,.025]),orientation='horizontal');cb.set_label('');fig.text(.245,.086,'hPa',fontsize=6.5)
 for j,mode in enumerate(['A','R']):
  sub=gs[j+1].subgridspec(2,1,height_ratios=[.48,1.52],hspace=.12);top=fig.add_subplot(sub[0]);ax=fig.add_subplot(sub[1])
  ax.imshow(d['map'+mode][:,start:end],origin='lower',aspect='auto',extent=[start-.5,end-.5,0,1],cmap=fs.FIELD_CMAP,vmin=d['field'].min(),vmax=d['field'].max());tracks(ax,d,mode,start,end)
  ax.axvline(t,color='white',ls=':',lw=.7);ax.set(xlabel='time step (step 48 marked)',yticks=[])
  top.plot(np.arange(start,end),d['pos'+mode][start:end]/L*100,color=fs.BLUE if mode=='A' else fs.GREEN,lw=1);top.set(ylabel='error %',ylim=(0,50),xlim=(start-.5,end-.5),xticks=[]);decorate(top)
  top.set_title('(b) RG-MTM-P: displaced anchors' if mode=='A' else '(c) RG-MTM-R: scalar cost')
  if mode=='R':ax.text(.02,.04,f'step 48: merge error {d["delta"][t]:.1f} hPa',transform=ax.transAxes,fontsize=6.5,bbox=dict(fc='white',alpha=.9,ec='none',pad=1))
 save(fig,'fig_teaser_focus')
def overview():
 from domain_filling_figures import overview as full_domain_overview
 full_domain_overview(OUT)
def diagnosis_frontier():
 fig=plt.figure(figsize=(7,2.55));gs=fig.add_gridspec(2,4,height_ratios=[1,1.15],left=.07,right=.98,bottom=.18,top=.87,hspace=.9,wspace=.36)
 for j,(name,label) in enumerate(zip(NAMES,LABELS)):
  ax=fig.add_subplot(gs[0,j]);c=read(f'replicate_{name}.json')['certificate'];h=np.array(c['H_per_frame'])*100;f=np.array(c['F_per_frame'])*100;t=np.arange(len(h));ax.bar(t,f,color=fs.GRAY,width=.9);ax.bar(t,h,bottom=f,color=fs.CORAL,width=.9)
  ix=h>2;ax.plot(t[ix],np.full(ix.sum(),-.055),'|',transform=ax.get_xaxis_transform(),color=fs.CORAL,ms=3,clip_on=False)
  ax.set_title(f'{label}: {c["conflict_frames"]}/{c["frames"]} conflicts');ax.set_xlabel('time step',labelpad=1);ax.set_xlim(-1,len(h));decorate(ax)
  if j==0:ax.set_ylabel('certificate (% axis)')
 for j,name in enumerate(['era5','wildfire']):
  ax=fig.add_subplot(gs[1,2*j:2*j+2]);r=read(f'attainable_{name}.json');x=np.array([v['delta'] for v in r['frontier']])*100
  ax.step(x,[v['F']*100 for v in r['frontier']],where='post',color=fs.BLUE,lw=1);ax.step(x,[v['Phi']*100 for v in r['frontier']],where='post',color='black',ls='--',lw=.65)
  for o in r['ours']:
   a,b,e=100*o['D_opt_share'],100*o['D_lca_share'],100*o['E_share'];ax.plot([a,b],[e,e],color=fs.GREEN,lw=.6);ax.plot(a,e,'o',color=fs.GREEN,ms=3);ax.plot(b,e,'o',mfc='white',mec=fs.GREEN,ms=3)
   if o['cap']==.2:ax.annotate(r'$\kappa=20\%$',(a,e),xytext=(4,6),textcoords='offset points',fontsize=6.5)
  ax.set_title('ERA5' if name=='era5' else 'Fire',pad=2);ax.set_xlabel('merge error (% scalar range)',labelpad=1);ax.set_ylabel('position optimum (% axis)');ax.set_xlim(-1,72);decorate(ax)
 fig.legend(handles=[Patch(color=fs.GRAY,label='packing'),Patch(color=fs.CORAL,label='hierarchy; ticks: H > 2%')],loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.5,1.01))
 fig.legend(handles=[Line2D([0],[0],color=fs.BLUE,label='attainable F'),Line2D([0],[0],color='k',ls='--',label='necessary bound'),Line2D([0],[0],color=fs.GREEN,marker='o',ls='none',ms=3,label='optimal filling'),Line2D([0],[0],color=fs.GREEN,marker='o',mfc='white',ls='none',ms=3,label='LCA filling')],loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.5,-.005))
 save(fig,'fig_diagnosis_tradeoff')
def motion_cost():
 ev=read('eval_projection.json');fig,axs=plt.subplots(1,3,figsize=(7,2.1),gridspec_kw={'width_ratios':[1.5,1.05,1.05]});y=np.arange(4)
 for j,m in enumerate(['ST-MTM','A','R 20%']):
  vals=[event(ev,n,m) for n in NAMES];axs[0].barh(y+(j-1)*.22,[100*r['error'] for r in vals],height=.2,color=COLS[j])
  for yy,r in zip(y+(j-1)*.22,vals):axs[0].text(100*r['error']+.5,yy,str(round(r['error']*r['clear'])),va='center',fontsize=6)
 axs[0].set_yticks(y,[f'{l} (n={event(ev,n,"A")["clear"]})' for n,l in zip(NAMES,LABELS)]);axs[0].set(xlim=(0,60),xlabel='proxy error (%)',title='(a) Motion errors; labels = counts');axs[0].invert_yaxis()
 for j,other in enumerate(['ST-MTM','A']):
  rows=[next(r for r in ev[n]['paired'] if r['method']=='R 20%' and r['other']==other and r['k']==2 and r['eps']==.02)['err'] for n in NAMES]
  for i,r in enumerate(rows):
   diff=r['diff']*100;lo,hi=np.array(r['ci95'])*100;axs[1].errorbar(diff,i+(j-.5)*.2,xerr=[[max(0,diff-lo)],[max(0,hi-diff)]],fmt='o' if j==0 else 's',ms=3,color=COLS[j],lw=.8,capsize=2)
 axs[1].axvline(0,color='#777777',ls=':',lw=.7);axs[1].set(yticks=y,yticklabels=[],ylim=(3.5,-.5),xlabel='paired difference (pp)',title='(b) Relaxed minus comparator')
 for i,n in enumerate(NAMES):
  d=ev[n]['dstar']['R 20%'];a,b=100*d['mean_share'],100*d['max_share'];axs[2].plot([a,b],[i,i],color=fs.BLUE,lw=.9);axs[2].plot(a,i,'o',color=fs.BLUE,ms=4);axs[2].plot(b,i,'D',color=fs.CORAL,ms=4);axs[2].text(b+.7,i,f'{b:.1f}',va='center',fontsize=6)
 axs[2].set(xlim=(0,43),yticks=y,yticklabels=[],ylim=(3.5,-.5),xlabel='merge error (% scalar range)',title='(c) Relaxed scalar cost')
 for ax in axs:decorate(ax)
 handles=[Patch(color=c,label=l) for c,l in zip(COLS,['ST-MTM','RG-MTM-P','RG-MTM-R'])]+[Line2D([0],[0],marker='o',color=COLS[0],ls='none',ms=3,label='vs ST-MTM'),Line2D([0],[0],marker='s',color=COLS[1],ls='none',ms=3,label='vs RG-MTM-P'),Line2D([0],[0],marker='o',color=fs.BLUE,ls='none',ms=3,label='mean cost'),Line2D([0],[0],marker='D',color=fs.CORAL,ls='none',ms=3,label='max cost')]
 fig.legend(handles=handles,loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.5,-.005),columnspacing=.8,handlelength=1)
 fig.subplots_adjust(left=.145,right=.985,top=.84,bottom=.35,wspace=.25);save(fig,'fig_motion_scalar_cost')
def cases(data):
 ev=read('eval_projection.json');fig=plt.figure(figsize=(7,3.55));gs=fig.add_gridspec(2,4,width_ratios=[1.05,.75,1.15,1.15],left=.055,right=.97,bottom=.18,top=.9,hspace=.75,wspace=.36);sel={}
 for row,name in enumerate(['era5','olr']):
  d=data[name];t=48 if name=='era5' else int(np.argmax(d['H']));start,end=(38,57) if name=='era5' else (max(0,t-6),min(len(d['H']),t+7));L=d['geometry'][1];sel[name]={'frame':t,'window':[start,end],'rule':'retained interior witness at step 48' if name=='era5' else 'first maximum hierarchy-cost frame; not selected by proxy outcome'}
  ax=fig.add_subplot(gs[row,0]);im=spatial(ax,d,t);ax.set_title(f'{"ERA5" if name=="era5" else "OLR"}: step {t}',pad=3);fig.colorbar(im,ax=ax,fraction=.05,pad=.02,label='hPa' if name=='era5' else r'W m$^{-2}$')
  ax=fig.add_subplot(gs[row,1]);tri=d['witness'][t];q=(d['q'][t]-d['geometry'][0])/L;u=(d['uA'][t]-d['geometry'][0])/L
  for i in range(len(q)):
   if not np.isfinite(q[i]):continue
   color=fs.BLUE if i in tri[:2] else fs.CORAL if i==tri[2] else '#bbbbbb';ax.plot([q[i],u[i]],[1,0],color=color,lw=.9);ax.plot(q[i],1,'v',color=color,ms=3);ax.plot(u[i],0,'o',color=color,ms=3)
  ax.set(xlim=(0,1),ylim=(-.15,1.15),xticks=[],yticks=[]);ax.set_title('Reference / tree anchors',fontsize=6.5);ax.text(0,1.08,'q',fontsize=7);ax.text(0,-.1,'u',fontsize=7);ax.set_xlabel(f'H = {100*d["H"][t]/L:.1f}% axis',fontsize=6.5);ax.spines[:].set_visible(False)
  for j,mode in enumerate(['A','R']):
   ax=fig.add_subplot(gs[row,j+2]);ax.imshow(d['map'+mode][:,start:end],origin='lower',aspect='auto',extent=[start-.5,end-.5,0,1],cmap=fs.FIELD_CMAP,vmin=d['field'].min(),vmax=d['field'].max());tracks(ax,d,mode,start,end);ax.axvline(t,color='white',ls=':',lw=.7);ax.set(yticks=[],xlabel='time step')
   e=event(ev,name,'A' if mode=='A' else 'R 20%');ax.set_title(f'{"RG-MTM-P" if mode=="A" else "RG-MTM-R"}: {round(e["error"]*e["clear"])}/{e["clear"]} errors*',pad=3)
   text=f'step {t}: position {100*d["pos"+mode][t]/L:.1f}%'
   if mode=='R':text+=f'\nmerge error {d["delta"][t]:.1f} '+('hPa' if name=='era5' else r'W m$^{-2}$')
   ax.text(.02,.04,text,transform=ax.transAxes,fontsize=6,bbox=dict(fc='white',alpha=.9,ec='none',pad=1))
 fig.text(.055,.018,'* Errors use the complete sequence, not just the displayed window. Scalar colors are shared within each row.',fontsize=6.5)
 save(fig,'fig_linked_cases');return sel

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare',action='store_true');args=ap.parse_args();OUT.mkdir(exist_ok=True);DATA.mkdir(parents=True,exist_ok=True);fs.apply();plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'rgmtm-layout-20261014'})
 if args.prepare:
  for n in ['era5','olr']:prepare(n)
 import fig_concept as concept
 concept.OUT=OUT;concept.main()
 data={n:load(n) for n in ['era5','olr']};teaser(data['era5']);overview();diagnosis_frontier();motion_cost();sel=cases(data)
 ev=read('eval_projection.json');values=[]
 for name in NAMES:
  for method in ['ST-MTM','A','R 20%']:
   r=event(ev,name,method);d=ev[name]['dstar'].get(method,{})
   values.append({'dataset':name,'method':method,'events':r['clear'],'errors':round(r['error']*r['clear']),'error_pct':100*r['error'],'mean_merge_pct':100*d['mean_share'] if d else 0.,'max_merge_pct':100*d['max_share'] if d else 0.})
 with (DATA/'motion_scalar_plot_values.csv').open('w',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(values[0]));writer.writeheader();writer.writerows(values)
 sources=['eval_projection.json','replicate_era5.json','replicate_wildfire.json','replicate_olr.json','replicate_pm25.json','attainable_era5.json','attainable_wildfire.json']
 report={'selection':sel,'evidence_sha256':{n:sha(ROOT/'results'/n) for n in sources},'render_exports':{n:sha(DATA/f'{n}_render.npz') for n in data},'generator_sha256':sha(Path(__file__)),'figures':{n:sha(OUT/f'{n}.pdf') for n in ['fig_teaser_focus','fig_method_visual','fig_diagnosis_tradeoff','fig_motion_scalar_cost','fig_linked_cases','fig_concept']},'semantics':'k=2, epsilon=2%; paired confidence intervals from saved moving-block bootstrap; no participant outcomes'}
 (DATA/'figure_manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('Five PDF/PNG/editable SVG figures exported.',flush=True)
if __name__=='__main__':main()
