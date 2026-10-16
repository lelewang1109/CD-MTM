from pathlib import Path
import sys,json,itertools,time,hashlib
import numpy as np
from scipy.optimize import linprog
root=Path(__file__).resolve().parents[2];sys.path[:0]=[str(root/'analysis'),str(root/'src'),str(root)]
import general_method as gm,relax_hierarchy as rh,filling as fl,attainable as at
from experiments import era5 as ep
from rgmtm.reference_points import reference_points_from_frames
from rgmtm.baselines.space_filling import merge_levels_on_line
out=root/'results/publication2027/bisector_control';out.mkdir(parents=True,exist_ok=True)
name=sys.argv[1] if len(sys.argv)>1 else 'bisector_highres';axis=sys.argv[2] if len(sys.argv)>2 else 'x';assert axis in ['x','y'];stem=name+'_'+axis
def fixed_reference(sc,ext,lo,hi,allow_radial=False):
 direction=np.array([1.,0.]) if axis=='x' else np.array([0.,1.]);j=0 if axis=='x' else 1
 return dict(kind='direction',qs=[e@direction for e in ext],origin=float(lo[j]),extent=float(hi[j]-lo[j]),label='position along fixed '+axis+' axis',candidates=dict(direction=dict(a=direction.tolist(),angle_deg=0. if axis=='x' else 90.)))
# Explicit task reference replaces automatic reference selection for this experiment.
gm.auto_reference=fixed_reference
def bisector():
 T=64;n=241;span=120.;g=np.linspace(0,span,n);X,Y=np.meshgrid(g,g);coords=np.c_[X.ravel(),Y.ravel()]
 A=np.array([20.,20.]);C=np.array([100.,100.]);bx=np.linspace(40.,80.,T);B=np.c_[bx,120.-bx]
 def blob(c,amp):return amp*np.exp(-((X-c[0])**2+(Y-c[1])**2)/(2*4.**2))
 ridge=0.*np.exp(-((X-60.)**2+(Y-np.clip(Y,30.,90.))**2)/(2*6.**2))
 fields=np.array([blob(A,1.)+blob(C,.95)+blob(b,1.05)+ridge for b in B]);sc=ep.scene_from_fields(fields,coords,(span/(n-1))**2,'split')
 return dict(name='bisector_highres',sc=sc,lo=coords.min(0),hi=coords.max(0),domain_area=n*n*(span/(n-1))**2,nominal=4096,cmap='viridis',vrange=None,native_span=span,meta=dict(A=A,C=C,B=B))
ds=bisector() if name=='bisector_highres' else getattr(gm,name)();sc=ds['sc'];T=len(sc['ids']);nmax=max(map(len,sc['ids']));kind=sc['trees'][0].kind
print('Loaded',name,T,'frames',nmax,'max leaves',flush=True)
res=rh.run(ds,.2,make_figure=False,return_internal=True);internal=res['_internal'];p=internal['p'];ref=internal['ref'];L=p.canvas;a=p.canvas_origin
q=np.concatenate(ref['qs']);ext=reference_points_from_frames(sc['frames'],sc['ids'],kind='extremum')
arrays={'field':np.asarray(sc.get('fields_smooth',sc['fields'])),'coords':sc['coords'],'geometry':np.array([a,L]),'direction':np.array(ref['candidates']['direction']['a']),'H':np.array([r['tau_hier']-r['tau_free'] for r in res['frame_log']]),'F':np.array([r['tau_free'] for r in res['frame_log']]),'n':np.array([len(ids) for ids in sc['ids']])}
for key,shape in [('q',(T,nmax)),('xy',(T,nmax,2)),('centroid',(T,nmax,2)),('value',(T,nmax))]:arrays[key]=np.full(shape,np.nan)
arrays['track']=np.full((T,nmax),-1,int);arrays['M']=np.full((T,nmax,nmax),np.nan)
for t,ids in enumerate(sc['ids']):
 n=len(ids);arrays['q'][t,:n]=ref['qs'][t];arrays['xy'][t,:n]=ext[t];arrays['centroid'][t,:n]=sc['centers'][t];arrays['value'][t,:n]=sc['frames'][t].values[ids];arrays['track'][t,:n]=sc['tracks'][t];arrays['M'][t,:n,:n]=at.lca_matrix(sc['frames'][t],ids,kind)*(-1 if kind=='split' else 1)
params=gm.Parameters(canvas=ds['native_span'],canvas_origin=float(min(ds['lo'][0],0.)),width_scale=.5*ds['native_span']/ds['domain_area'],gap=ds['native_span']/240,extra_budget=ds['native_span']/120,rho=.5)
report={'dataset':name,'reference_axis':axis,'frames':T,'kind':kind,'scalar_range':float(np.ptp(sc['fields'])),'reference_origin':a,'reference_extent':L,'reference_direction':arrays['direction'].tolist(),'cap_fraction':.2,'calibration':'Baselines receive their best single affine minimax calibration to reference coordinates over the whole sequence, including one global reflection; no framewise fitting. RG-MTM uses its native reference coordinates.','methods':{},'spatial_resolution':241,'grid_pitch':.5,'analytic_B_centres':ds['meta']['B'].tolist(),'sampling_note':'Same fields and algorithms as diagonal control, spatial grid refined from 61x61 to 241x241. Reference and reported anchors use sampled extrema, not smoothed display paths.'}
for key,method in [('T','TMTM'),('S','ST-MTM'),('R','RG-MTM')]:
 print('Constructing',method,flush=True)
 if key in ['T','S']:
  rr=ep.run_method(sc,method,params,canvas=ds['native_span'],length=ds['nominal'],refine_raster=False,strict_checks=False,stmtm_parameters=ep.b2.LayoutParameters('uniform',65.,.95,1.5,ds['nominal'],0,min_spacing_delta=.01,optimizer_tolerance=1e-11) if key=='S' else None)
  U=[r['pixel_x'].copy() for r in rr['rows']];matrix=rr['maps'].astype(float)
  if key=='T':
   scale,shift=rr['gauge']['scale'],rr['gauge']['shift'];span=ds['native_span'];glo=shift if scale>0 else shift-span;ghi=glo+span
   anchors=[np.rint((u-glo)/(ghi-glo)*(matrix.shape[0]-1)).astype(int) for u in U]
  else:
   disc=rr['records']['discrete'];anchors=[]
   for ids,d in zip(sc['ids'],disc):
    anc=np.array(d['anchors'],int)[[list(d['ordering']).index(i) for i in ids]]
    if rr['gauge']['scale']<0:anc=matrix.shape[0]-1-anc
    anchors.append(anc)
   # Derive the exact returned raster coordinate map from a frame with >=2 extrema.
   t0=next(t for t in range(T) if len(U[t])>=2);slope,offset=np.polyfit(anchors[t0],U[t0],1);glo=offset;ghi=offset+slope*(matrix.shape[0]-1)
   assert max(np.max(abs(offset+slope*anc-u)) for anc,u in zip(anchors,U))<1e-7
  # Strong baseline control: one best fixed affine map (minimax) across every observed feature.
  uu=np.concatenate(U);B=np.column_stack([uu,np.ones(len(uu))]);Aub=np.vstack([np.c_[B,-np.ones(len(uu))],np.c_[-B,-np.ones(len(uu))]])
  fit=linprog([0.,0.,1.],A_ub=Aub,b_ub=np.r_[q,-q],bounds=[(None,None),(None,None),(0,None)],method='highs');assert fit.success
  alpha,beta,_=fit.x
  unconstrained_error=float(fit.x[2]);degenerate=abs(alpha)<1e-8
  if degenerate:
   fits=[linprog([0.,0.,1.],A_ub=Aub,b_ub=np.r_[q,-q],bounds=[bd,(None,None),(0,None)],method='highs') for bd in [(1e-3,None),(None,-1e-3)]]
   fit=min([f for f in fits if f.success],key=lambda f:f.x[2]);alpha,beta,_=fit.x
  assert abs(alpha)>1e-8
  Up=[alpha*u+beta for u in U];mapbounds=[alpha*glo+beta,alpha*ghi+beta]
  report['methods'][method]={'affine_scale':float(alpha),'affine_shift':float(beta),'best_sequence_max_error_pct':float(100*fit.x[2]/L),'native_raster_length':matrix.shape[0],'unconstrained_affine_error_pct':100*unconstrained_error/L,'affine_fit_degenerate':bool(degenerate),'nonzero_scale_floor':.001 if degenerate else None}
 else:
  rows=internal['results']['R_relaxed']['_rows'];matrix,skels,_=rh.render(sc,rows,p,ds['nominal']);matrix=matrix.astype(float)
  anchors=[];Up=[]
  for t,(fr,sk) in enumerate(zip(sc['frames'],skels)):
   ids=sc['ids'][t];anc=np.array(sk.anchors,int)[[list(sk.ordering).index(i) for i in ids]];anchors.append(anc);Up.append(a+anc/(matrix.shape[0]-1)*L)
   matrix[:,t],_=fl.optimal_fill(matrix[:,t],list(sk.ordering),sk.anchors,fr,kind)
  mapbounds=[a,a+L];report['methods'][method]={'affine_scale':1.,'affine_shift':0.,'native_raster_length':matrix.shape[0]}
 arrays['map'+key]=matrix;arrays['bounds'+key]=np.array(mapbounds);arrays['u'+key]=np.full((T,nmax),np.nan)
 stress=[];ce=[];delta=[];pos=[]
 for t,(u,ids,anc) in enumerate(zip(Up,sc['ids'],anchors)):
  n=len(ids);arrays['u'+key][t,:n]=u;pos.append(float(np.max(abs(u-ref['qs'][t]))/L))
  native=merge_levels_on_line(matrix[:,t],anc,kind);true=arrays['M'][t,:n,:n];delta.append(float(np.max(abs(native-true))))
  pairs=list(itertools.combinations(range(n),2));d1=np.array([abs(u[i]-u[j]) for i,j in pairs])
  def st(points):
   if n<3:return np.nan
   d2=np.array([np.linalg.norm(points[i]-points[j]) for i,j in pairs]);factor=(d1@d2)/max(d1@d1,1e-12);return float(np.sqrt(np.sum((factor*d1-d2)**2)/np.sum(d2**2)))
  stress.append(st(ext[t]));ce.append(st(sc['centers'][t]))
 arrays['pos'+key]=np.array(pos);arrays['stress'+key]=np.array(stress);arrays['cstress'+key]=np.array(ce);arrays['delta'+key]=np.array(delta)
 report['methods'][method].update(mean_frame_max_position_pct=float(100*np.mean(pos)),mean_extremum_stress=float(np.nanmean(stress)),mean_centroid_stress=float(np.nanmean(ce)),mean_merge_error_pct=float(100*np.mean(delta)/report['scalar_range']),max_merge_error_pct=float(100*np.max(delta)/report['scalar_range']))
# Select a focused conflict frame, based on measured local comparisons, with full-sequence curves alongside.
candidates=[]
for t in range(T):
 if arrays['n'][t]!=3 or arrays['H'][t]/L<=.02:continue
 if arrays['stressS'][t]>=arrays['stressT'][t] or arrays['posR'][t]>=arrays['posS'][t]:continue
 score=arrays['posS'][t]-arrays['posR'][t]
 candidates.append((float(score),t))
if not candidates:
 candidates=[(float(arrays['posS'][t]-arrays['posR'][t]),t) for t in range(T) if arrays['H'][t]/L>.02]
selected=63;report['selected_frame']=selected;report['selection_rule']='Final mirror endpoint. Original generic rule unused: Maximum ST-MTM-minus-RG-MTM achieved position-error gain among 3-leaf conflict frames with ST-MTM stress below TMTM and RG-MTM position error below ST-MTM. If none, maximize gain among conflict frames.'
report['candidate_count']=len(candidates);report['candidate_frames']=[t for _,t in sorted(candidates,reverse=True)]
report['selected']={m:{'position_pct':float(100*arrays['pos'+k][selected]),'extremum_stress':float(arrays['stress'+k][selected]),'centroid_stress':float(arrays['cstress'+k][selected]),'merge_error_pct':float(100*arrays['delta'+k][selected]/report['scalar_range'])} for k,m in [('T','TMTM'),('S','ST-MTM'),('R','RG-MTM')]}
report['source_sha256']={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'analysis/task_reference.py',root/'analysis/general_method.py',root/'analysis/relax_hierarchy.py',root/'analysis/filling.py',root/'experiments/era5.py']}
np.savez_compressed(out/(stem+'_three_methods.npz'),**arrays)
report['arrays_sha256']=hashlib.sha256((out/(stem+'_three_methods.npz')).read_bytes()).hexdigest();(out/(stem+'_three_methods.json')).write_text(json.dumps(report,indent=2))
print(json.dumps(report['selected'],indent=2));print('Selected frame',selected,'q',arrays['q'][selected],'M',arrays['M'][selected],flush=True)
