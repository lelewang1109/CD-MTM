"""Generate tables and grouped result snapshots without replacing manuscript prose."""
from pathlib import Path
import csv, hashlib, json, shutil, sys, subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'analysis'))
from dataset_suite import PAPER_DATASETS
PAPER=ROOT/'paper/pacificvis2027-restructured'; OUT=ROOT/'results/publication2027'
SHORT=dict(era5='ERA5',wildfire='Fire',olr='OLR',pm25='PM2.5',ring='Ring',gaussians='Gaussians')
METHODS=['TMTM','ST-MTM','Hilbert','Morton','q-sort (packed)','A','R 20%']
LABELS=dict(zip(METHODS,['TMTM','ST-MTM','Hilbert','Morton','Packed sort','CD-MTM (tree kept)',r'CD-MTM, $\kappa=20\%$']))
def read(name):return json.loads((ROOT/'results'/name).read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def event(ev,m):
 rows=[r for r in ev['proxy'] if r['method']==m and r['k']==2 and r['eps']==.02]
 if len(rows)!=1:raise ValueError(f'Expected one motion record: {m}')
 return rows[0]
def table(path,cols,header,rows,caption,label,notes='',wide=True):
 env='table*' if wide else 'table'
 path.write_text('\n'.join([rf'\begin{{{env}}}[t]',rf'\caption{{{caption}}}\label{{{label}}}',r'\centering\footnotesize',r'\setlength{\tabcolsep}{3pt}',rf'\begin{{tabular}}{{{cols}}}\toprule',header+r'\\\midrule',*[' & '.join(map(str,row))+r'\\' for row in rows],r'\bottomrule\end{tabular}',r'\par\smallskip{\footnotesize\raggedright '+notes+r'\par}' if notes else '',rf'\end{{{env}}}'])+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True);tabs=PAPER/'tables';tabs.mkdir(exist_ok=True)
 pos=read('final_performance.json');ev=read('eval_projection.json');nat=read('native_merge_errors.json');fill=read('filling.json')
 reps={n:read(f'replicate_{n}.json') for n in PAPER_DATASETS};fronts={n:read(f'attainable_{n}.json') for n in PAPER_DATASETS}
 def topo(n,m):
  if m in ['TMTM','ST-MTM']:return nat[n][m]['mean_share'],nat[n][m]['max_share']
  if m=='A':
   r=next(r for r in fill[n] if r['cap']==0);return r['mean_opt_share'],r['D_opt_share']
  return ev[n]['dstar'][m]['mean_share'],ev[n]['dstar'][m]['max_share']
 for n in PAPER_DATASETS:
  if not(pos[n]['frames']==reps[n]['certificate']['frames']==nat[n]['TMTM']['frames']):raise ValueError('Frame mismatch: '+n)
  for d in [pos[n],nat[n]]:
   for source,h in d['source_sha256'].items():
    if digest(ROOT/source)!=h:raise ValueError(f'Stale evidence: {n}/{source}')
  for m in METHODS:
   event(ev[n],m)
   if m in ['TMTM','ST-MTM','A'] and np.any(np.asarray(pos[n]['methods'][m]['per_frame'])+1e-8<pos[n]['bound_per_frame']):raise ValueError('Hierarchy bound violated: '+n+'/'+m)
 specs=[['ERA5','1999-11-17--2000-01-14',118,r'$49\times49$','Join','250 km'],['Fire','Nov.--Dec. 2019',30,r'$64\times64$','Split','50.7 km'],['OLR','2024-06-01--2024-07-30',60,r'$49\times49$','Join','500 km'],['PM2.5','2000-01-01--2000-01-30',30,r'$49\times49$','Split','100 km'],['Ring','Synthetic expansion',40,r'$14\times14$','Split','None'],['Gaussians','Synthetic motion',64,r'$64\times64$','Split','None']]
 table(tabs/'datasets.tex','llrlll','Data & Period / construction & Frames & Grid & Tree & Smoothing',specs,'Evaluated fields. Processing defines the tested extrema and merge trees.','tab:data','ERA5 is sampled every 12 hours; fire every two days; OLR and PM2.5 daily. January PM2.5 is an exploratory display selection.')
 rows=[]
 for n in PAPER_DATASETS:
  c=reps[n]['certificate'];f=np.asarray(c['F_per_frame']);h=np.asarray(c['H_per_frame'])
  rows.append([SHORT[n],c['frames'],f"{c['leaves'][0]}--{c['leaves'][1]}",f'{100*f.mean():.2f}',f'{100*h.mean():.2f}',f'{100*(f+h).mean():.2f}',f"{c['conflict_frames']}/{c['frames']}"])
 table(tabs/'certificates.tex','lrrrrrl',r'Data & Frames & Leaves & Packing \% & Hierarchy \% & Total \% & Conflict frames',rows,'Full interval-model certificates: temporal means normalized by reference extent.','tab:cert',r'Total is $\overline{\tau^*}/L=\overline{\tau_\free}/L+\overline{H}/L$. Conflicts use $H>0.02L$. These are minimum attainable maximum errors under the shared geometry.')
 header='Method & '+' & '.join(r'\multicolumn{2}{c}{'+SHORT[n]+'}' for n in PAPER_DATASETS)+r'\\'+''.join(r'\cmidrule(lr){'+f'{2+2*i}-{3+2*i}'+'}' for i in range(6))+' & '+' & '.join([r'$P$ & $D$']*6)
 rows=[];flat=[]
 for m in METHODS:
  row=[LABELS[m]]
  for n in PAPER_DATASETS:
   dm,dx=topo(n,m);p=pos[n]['methods'][m]['mean'];v=event(ev[n],m);row.extend([f'{100*p:.2f}',f'{100*dm:.2f}'])
   flat.append(dict(dataset=n,method=m,frames=pos[n]['frames'],order_error_mean_pct=100*p,point_bound_mean_pct=100*pos[n]['bound_mean'],merge_error_mean_pct=100*dm,merge_error_max_pct=100*dx,motion_clear_events=v['clear'],motion_error_pct=100*v['error'] if v['clear'] else None))
  rows.append(row)
 table(tabs/'tradeoff.tex','l'+'rr'*6,header,rows,'Reference-order alignment and scalar merge fidelity (\%; lower is better).','tab:tradeoff',r'$P$: mean width-free minimax error after optimal monotone calibration / reference extent; not achieved anchor displacement. $D$: mean framewise maximum tracked-extremum merge error / processed scalar range. Native and rendered baselines use actual scalar barriers; CD-MTM and packed sorting use optimal filling. The protocols differ as stated in the text.')
 rows=[]
 for n in PAPER_DATASETS:
  vals=[event(ev[n],m) for m in ['ST-MTM','A','R 20%']];count=vals[0]['clear'];dm,dx=topo(n,'R 20%')
  rows.append([SHORT[n],count,*[f"{round(v['error']*count)}/{count}" if count else '--' for v in vals],f'{100*dx:.1f}'])
 table(tabs/'motion.tex','lrrrrr',r'Data & Events & ST-MTM & Tree kept & Relaxed & Max $D$ \%',rows,"Motion-proxy errors and the relaxed map's worst-frame scalar cost.",'tab:motion',r'Errors = reversals + misses at $k=2$, 2\% thresholds. -- denotes undefined rates without clear events. These geometric readings assume known identities.',wide=False)
 for stem in ['datasets','certificates','motion']:
  text=(tabs/f'{stem}.tex').read_text().replace(r'\begin{table*}[t]',r'\begin{table}[H]').replace(r'\begin{table}[t]',r'\begin{table}[H]').replace(r'\end{table*}',r'\end{table}')
  (tabs/f'{stem}_supp.tex').write_text(text)
 with (OUT/'main_comparison.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
 membership={'main':[f'replicate_{n}.json' for n in PAPER_DATASETS]+[f'attainable_{n}.json' for n in PAPER_DATASETS]+['final_performance.json','native_merge_errors.json','eval_projection.json','filling.json','pointcert.json'],
 'sensitivity':['robustness.json','persistence.json','sensitivity.json','stmtm_grid.json','independent_scale.json','pm25_season_protocol.json']+[f'{p}_{n}.json' for p in ['replicate','attainable','protocol'] for n in ['pm25_jan','pm25_apr','pm25_jul','pm25_oct']],
 'validation':['generality.json','benchmark_degree.json','boundary.json','witness.json','topological_case_step48.json'],'transfer':['dendrogram_demo.json'],'protocols':['protocol_olr.json','protocol_pm25.json','sfc_baseline_protocol.json','source_pm25_doi.json']}
 records=[]
 for group,files in membership.items():
  folder=OUT/'evidence'/group;folder.mkdir(parents=True,exist_ok=True)
  for name in files:
   source=ROOT/'results'/name;target=folder/name;obj=read(name)
   if name in ['eval_projection.json','filling.json','pointcert.json','native_merge_errors.json','final_performance.json']:
    target.write_text(json.dumps({n:obj[n] for n in PAPER_DATASETS},indent=2)+'\n')
   else:shutil.copy2(source,target)
   records.append(dict(role=group,source=str(source.relative_to(ROOT)),source_sha256=digest(source),snapshot=str(target.relative_to(ROOT)),snapshot_sha256=digest(target)))
 claims=dict(frames=sum(reps[n]['certificate']['frames'] for n in PAPER_DATASETS),conflict_frames={n:reps[n]['certificate']['conflict_frames'] for n in PAPER_DATASETS},motion={n:{m:event(ev[n],m) for m in ['ST-MTM','A','R 20%']} for n in PAPER_DATASETS},filling_discrepancy=max(r['measured_vs_closed_form_max'] for n in PAPER_DATASETS for r in fill[n]),frontier={n:fronts[n]['ours'] for n in PAPER_DATASETS})
 (OUT/'claims.json').write_text(json.dumps(claims,indent=2)+'\n')
 subprocess.run([sys.executable,str(ROOT/'experiments/publication2027/figures.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'experiments/publication2027/supplement_tables.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'experiments/publication2027/layout_figures.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'experiments/publication2027/domain_filling_figures.py')],check=True)
 figures=[]
 for name in ['fig_teaser','fig_concept','fig_topo_price','fig_displacement_compact','fig_frontier_compact','fig_witness','fig_method_overview','olr_temporal_methods','pm25_temporal_methods','fig_teaser_focus','fig_method_visual','fig_diagnosis_tradeoff','fig_motion_scalar_cost','fig_linked_cases','fig_full_domain_filling']:
  fresh=name in ['fig_concept','fig_displacement_compact','fig_frontier_compact','fig_method_overview','fig_teaser_focus','fig_method_visual','fig_diagnosis_tradeoff','fig_motion_scalar_cost','fig_linked_cases','fig_full_domain_filling']
  source=(PAPER if fresh else ROOT/'paper/pacificvis2027')/'figures'/f'{name}.pdf'
  if name.endswith('temporal_methods'):source=ROOT/'results/visualizations'/f'{name}.pdf'
  if not source.exists():source=PAPER/'figures'/f'{name}.pdf'
  if not fresh and source.resolve()!=(PAPER/'figures'/source.name).resolve():shutil.copy2(source,PAPER/'figures'/source.name)
  figures.append(dict(figure=name,source=str(source.relative_to(ROOT)),sha256=digest(source),execution='replotted from evidence' if fresh else 'retained generated figure'))
 manifest=dict(active_datasets=list(PAPER_DATASETS),frames=claims['frames'],scope='new tables and grouped evidence; numerical reruns recorded separately under runs/',records=records,figures=figures,generated_tables={str(p.relative_to(ROOT)):digest(p) for p in tabs.glob('*.tex')},source_sha256={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__),ROOT/'analysis/dataset_suite.py',*sorted((ROOT/'experiments/publication2027').glob('*.py')),ROOT/'analysis/fig_witness.py',ROOT/'analysis/fig_teaser.py',ROOT/'analysis/fig_concept.py',ROOT/'tools/update_paper_evidence.py']})
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(f'Built {len(records)} evidence records, four tables, comparison CSV, claims and manifest.')
if __name__=='__main__':main()
