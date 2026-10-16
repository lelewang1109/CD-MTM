"""Additional paper tables generated from declared evidence, never from prose."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'analysis'))
from dataset_suite import PAPER_DATASETS,REAL_DATASETS
PAPER=ROOT/'results/legacy_publication/pacificvis2027-restructured'
SHORT=dict(era5='ERA5',wildfire='Fire',olr='OLR',pm25='PM2.5',ring='Ring',gaussians='Gaussians')
def read(name):return json.loads((ROOT/'results'/name).read_text())
def longtable(cols,header,rows,caption):
 return '\n'.join([r'\begingroup\small\setlength{\tabcolsep}{4pt}',rf'\begin{{longtable}}{{{cols}}}',rf'\caption{{{caption}}}\\\toprule',header+r'\\\midrule\endfirsthead',r'\toprule '+header+r'\\\midrule\endhead',r'\bottomrule\endfoot',*[' & '.join(map(str,r))+r'\\' for r in rows],r'\end{longtable}\endgroup'])
def main():
 ev=read('eval_projection.json');pos=read('final_performance.json');nat=read('native_merge_errors.json');fill=read('filling.json')
 sections=[];rows=[]
 labels={'A':'RG-MTM-P','R 20%':'RG-MTM-R','q-sort (packed)':'Packed sort','fixed-X anchored':'Fixed X','oracle q':'Exact projection'}
 for n in PAPER_DATASETS:
  for m in ['TMTM','ST-MTM','Hilbert','Morton','A','R 20%','q-sort (packed)','fixed-X anchored','oracle q']:
   v=next(v for v in ev[n]['proxy'] if v['method']==m and v['k']==2 and v['eps']==.02)
   if m in ['TMTM','ST-MTM','fixed-X anchored']:d=nat[n][m]
   elif m=='A':
    f=next(f for f in fill[n] if f['cap']==0);d=dict(mean_share=f['mean_opt_share'],max_share=f['D_opt_share'])
   elif m=='oracle q':d=None
   else:d=ev[n]['dstar'][m]
   stress=ev[n]['hidden'][m]['stress']
   rows.append([SHORT[n],labels.get(m,m),f"{100*pos[n]['methods'][m]['mean']:.2f}",f"{100*d['mean_share']:.2f}" if d else '--',f"{100*d['max_share']:.2f}" if d else '--',f'{stress:.3f}' if stress is not None else '--',v['clear'],f"{100*v['error']:.1f}" if v['clear'] else '--'])
 sections.append(longtable('llrrrrrr',r'Data & Method & $P$ \% & Mean $D$ \% & Max $D$ \% & Stress & Events & Error \%',rows,'Expanded numerical comparison. Position is order-only; stress is Kruskal stress-1; motion error is reversal plus miss. Exact projection has no scalar topology.'))
 rows=[]
 for n in PAPER_DATASETS:
  d=read(f'attainable_{n}.json');t=d['tightness'];o=next(x for x in d['ours'] if x['cap']==.2)
  rows.append([SHORT[n],d['max_leaves'],f"{t['tight_within_half_pixel']}/{t['breakpoints']}",f"{100*t['gap_max']:.2f}",f"{o['frames_pareto_optimal']}/{o['frames']}",f"{100*o['excess_over_attainable_max_share']:.2f}"])
 sections.append(longtable('lrrrrr',r'Data & Max leaves & Tight breaks & Max $F-\Phi$ \% & R20 on $F$ & Max excess \%',rows,'Retained exact-frontier checks. Half a pixel defines tightness. Selected-order optima exclude secondary-layout slack.'))
 rows=[]
 for n in PAPER_DATASETS:
  for f in fill[n]:rows.append([SHORT[n],str(f['cap']) if f['cap']!=float('inf') else r'$\infty$',f"{100*f['D_lca_share']:.2f}",f"{100*f['D_opt_share']:.2f}",f"{f['measured_vs_closed_form_max']:.2g}"])
 sections.append(longtable('llrrr',r'Data & $\kappa$/range & LCA max \% & Optimal max \% & Formula residual',rows,'Recomputed scalar filling checks. The residual includes strict-extremum clearance and is normalized as recorded.'))
 rows=[]
 for n in ['pm25_jan','pm25_apr','pm25_jul','pm25_oct']:
  c=read(f'replicate_{n}.json')['certificate'];vals=[next(v for v in ev[n]['proxy'] if v['method']==m and v['k']==2 and v['eps']==.02) for m in ['ST-MTM','A','R 20%']]
  rows.append([n.split('_')[-1].title(),c['frames'],c['conflict_frames'],vals[0]['clear'],*[f"{100*v['error']:.1f}" if v['clear'] else '--' for v in vals]])
 sections.append(longtable('lrrrrrr','Month & Frames & Conflicts & Events & ST-MTM & Tree kept & Relaxed',rows,'Retained exploratory PM2.5 seasonal audit: motion error percentages. January was selected for display after this comparison.'))
 rows=[];rob=read('robustness.json')
 for n in REAL_DATASETS:
  fixed=[x['share_theta_2'] for x in rob[n] if not str(x['direction']).startswith('auto')]
  rows.append([SHORT[n],f'{100*min(fixed):.1f}',f'{100*max(fixed):.1f}'])
 sections.append(longtable('lrr','Data & Minimum conflict \% & Maximum conflict \%',rows,'Retained direction sensitivity: conflict shares at 2\% across eight fixed directions.'))
 (PAPER/'tables/supplement_generated.tex').write_text('\n\n'.join(sections)+'\n')
 print('Generated supplementary comparisons, frontier, filling, seasonal and direction tables.')
if __name__=='__main__':main()
