"""Rebuild editorial tables from saved evidence; no scientific experiment rerun."""
from pathlib import Path
import json,csv,hashlib
C=Path(__file__).resolve().parents[1];P=C/'paper/pacificvis2027-no-figures';D=C/'results/manuscript_tables';D.mkdir(parents=True,exist_ok=True)
NAMES=['era5','wildfire','olr','pm25','ring','gaussians'];SHORT=dict(zip(NAMES,['ERA5','Fire','OLR','PM2.5','Ring','Gaussians']));MS=['TMTM','ST-MTM','A','R 20%']
def read(n):return json.loads((C/'results'/n).read_text())
perf=read('final_performance.json');ev=read('eval_projection.json');fill=read('filling.json');ledger=[];e_rows=[]
lines=[r'\begin{table*}[t]',r'\caption{Normalized Reference-Order Error (NROE), motion-event error rate (ME), and Normalized Merge-Level Error (NMLE).}\label{tab:tradeoff}',r'\centering\footnotesize\setlength{\tabcolsep}{4pt}',r'\begin{tabular}{lrrrrrrrrrrr}\toprule',r' & & \multicolumn{2}{c}{TMTM} & \multicolumn{2}{c}{ST-MTM} & \multicolumn{2}{c}{RG-MTM-P (ours)} & \multicolumn{4}{c}{RG-MTM-R (ours)}\\',r'\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-12}',r'Data & $N_{\rm clear}$ & NROE$\downarrow$ & ME$\downarrow$ & NROE$\downarrow$ & ME$\downarrow$ & NROE$\downarrow$ & ME$\downarrow$ & NROE$\downarrow$ & ME$\downarrow$ & NMLE$_{\rm mean}\downarrow$ & NMLE$_{\rm max}\downarrow$\\\midrule']
for n in NAMES:
 vals=[];record={'dataset':n,'frames':perf[n]['frames'],'methods':{}}
 for m in MS:
  row=next(z for z in ev[n]['proxy'] if z['method']==m and z['k']==2 and z['eps']==.02)
  p=100*perf[n]['methods'][m]['mean'];clear=row['clear'];err=round(row['error']*clear) if clear else None
  vals.extend([f'{p:.2f}',f"{row['error']:.3f}" if clear else '--'])
  record['methods'][m]={'P_pct':p,'motion_errors':err,'clear_events':clear,'ME_rate':row['error'] if clear else None}
 f=next(x for x in fill[n] if x['cap']==.2)
 # Use measured raster values, rather than presenting the theoretical optimum as a measurement.
 vals.extend([f"{100*f['mean_opt_share']:.2f}",f"{100*f['D_opt_share']:.2f}"])
 record['R_measured_D_mean_pct']=100*f['mean_opt_share'];record['R_measured_D_max_pct']=100*f['D_opt_share']
 counts={x['clear_events'] for x in record['methods'].values()};assert len(counts)==1
 lines.append(SHORT[n]+' & '+str(counts.pop())+' & '+' & '.join(vals)+r'\\')
 rep=read(f'replicate_{n}.json');L=rep['certificate']['axis'];a=rep['tradeoff']['0.0'];r=rep['tradeoff']['0.2']
 e={m:{'E_pool_pct':100*x['ref_err_mean']/L,'E_p95_pct':100*x['ref_err_p95']/L,'E_max_pct':100*x['ref_err_max']/L} for m,x in [('A',a),('R 20%',r)]}
 record['achieved_reference']=e;record['source_files']=['results/final_performance.json','results/eval_projection.json','results/filling.json',f'results/replicate_{n}.json']
 ledger.append(record)
 e_rows.append(SHORT[n]+' & '+' & '.join(f'{v:.2f}' for m in ['A','R 20%'] for v in [e[m]['E_pool_pct'],e[m]['E_max_pct']])+r'\\')
lines.extend([r'\bottomrule\end{tabular}',r'\par\smallskip{\footnotesize\raggedright NROE is $P$ (\% of reference extent); NMLE is $D$ (\% of processed scalar range). ME is the fraction of reversals plus misses among the shared $N_{\rm clear}$ events, displayed in $[0,1]$ to three decimals; -- means no clear events. The motion protocol uses two steps and 2\% thresholds. RG-MTM-R uses $\kappa/\Delta_F=0.20$, an eligibility threshold rather than an error cap. NMLE uses measured filled-raster barriers; the other three methods have zero measured pairwise merge error. No combined score or statistical ranking is implied.\par}',r'\end{table*}'])
(P/'tables/comparison_revision.tex').write_text('\n'.join(lines)+'\n')
e=[r'\begin{table}[H]',r'\caption{Achieved continuous reference displacement (\% of $L$).}\label{tab:achieved_reference}',r'\centering\begin{tabular}{lrrrr}\toprule',r' & \multicolumn{2}{c}{RG-MTM-P} & \multicolumn{2}{c}{RG-MTM-R, $\kappa=20\%$}\\',r'Data & $E_{\rm pool}$ & $E_\infty$ & $E_{\rm pool}$ & $E_\infty$\\\midrule',*e_rows,r'\bottomrule\end{tabular}',r'\par\smallskip\footnotesize $E_{\rm pool}$ pools all retained feature-frame anchors; $E_\infty$ is the largest absolute continuous anchor error. These use the saved layouts and do not measure a newly computed layout. Raster rounding and scalar correction are separate. The retained baseline record also reports the pooled 95th percentile.',r'\end{table}']
(P/'tables/achieved_reference_supp.tex').write_text('\n'.join(e)+'\n')
sourcefiles=sorted({x for row in ledger for x in row['source_files']})
(D/'数值与来源.json').write_text(json.dumps({'scope':'existing result reanalysis; no numerical experiment rerun','main_metrics_use':'NROE (P) temporal frame mean; E pooled features; NMLE (D) actual measured barriers; ME decimal rate with clear-event counts','metric_display_names':{'P':'Normalized Reference-Order Error (NROE)','D':'Normalized Merge-Level Error (NMLE)'},'records':ledger,'display_names':{'A':'RG-MTM-P','R 20%':'RG-MTM-R'},'source_sha256':{x:hashlib.sha256((C/x).read_bytes()).hexdigest() for x in sourcefiles}},ensure_ascii=False,indent=2))
with (D/'主表原始数值.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['dataset','method','P_pct','motion_errors','clear_events','R_D_mean_pct_measured','R_D_max_pct_measured','source_method_key','ME_rate'])
 for rec in ledger:
  for m,o in rec['methods'].items():w.writerow([rec['dataset'],{'A':'RG-MTM-P','R 20%':'RG-MTM-R'}.get(m,m),o['P_pct'],o['motion_errors'],o['clear_events'],rec['R_measured_D_mean_pct'] if m=='R 20%' else 0,rec['R_measured_D_max_pct'] if m=='R 20%' else 0,m,o['ME_rate']])
periods=['1999-11-17--2000-01-14','Nov.--Dec. 2019','2024-06-01--2024-07-30','2000-01-01--2000-01-30','Synthetic expansion','Synthetic motion']
grids=[49,64,49,49,14,64];kinds=['Join','Split','Join','Split','Split','Split'];sigma=['250','50.7','500','100','--','--']
data=[r'\begin{table}[H]',r'\caption{Evaluated fields. Leaf counts refer to the processed extrema and merge trees.}\label{tab:data}',r'\centering\footnotesize\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{llrllll}\toprule',r'Data & Period / construction & Frames & Grid & Leaves & Tree & Smoothing\\\midrule']
for i,n in enumerate(NAMES):
 rep=read(f'replicate_{n}.json')['certificate'];lo,hi=rep['leaves']
 data.append(f"{SHORT[n]} & {periods[i]} & {rep['frames']} & ${grids[i]}\\times{grids[i]}$ & {lo}--{hi} & {kinds[i]} & {sigma[i]}"+(' km' if sigma[i]!='--' else '')+r'\\')
data.extend([r'\bottomrule\end{tabular}',r'\par\smallskip{\footnotesize\raggedright Six sequences, 342 frames. ERA5 is sampled every 12 hours; fire uses two-day aggregates; OLR and PM2.5 supply one sample per day. Smoothing denotes the fixed Gaussian scale. January PM2.5 is exploratory.\par}',r'\end{table}'])
(P/'tables/datasets_supp.tex').write_text('\n'.join(data)+'\n')
# Standard metrics are a separate completed re-evaluation of the same fixed
# configurations. This generator only reads its saved outputs.
pub=C/'results/public_metrics_20261016'
if (pub/'summary.csv').exists():
 rows=list(csv.DictReader((pub/'summary.csv').open()))
 tab=[r'\begingroup\small\setlength{\tabcolsep}{5pt}',r'\begin{longtable}{llrrrrr}',r'\caption{Standard geometry and stability re-evaluation on the unchanged main configurations.}\label{tab:standard_geometry}\\\toprule',r'Data & Method & SNS$\downarrow$ & TW$_1\uparrow$ & TD$\downarrow$ & $N_{\rm SNS}$ & $N_{\rm TW}$\\\midrule\endfirsthead',r'\toprule Data & Method & SNS$\downarrow$ & TW$_1\uparrow$ & TD$\downarrow$ & $N_{\rm SNS}$ & $N_{\rm TW}$\\\midrule\endhead',r'\bottomrule\endfoot']
 for row in rows:
  tab.append(SHORT[row['dataset']]+' & '+row['method']+' & '+' & '.join(f"{float(row[k]):.4f}" for k in ['SNS','TW1','TD'])+' & '+row['SNS_frames']+' & '+row['TW1_frames']+r'\\')
 tab.extend([r'\end{longtable}',r'\noindent SNS and TW use support centroids. TD is summed in full-canvas-width units, not occupied-range-normalized mean displacement. $N$ columns count valid frames; TW uses $k=1$. All values are descriptive.\endgroup'])
 (P/'tables/standard_metrics_supp.tex').write_text('\n'.join(tab)+'\n')
 ranks=list(csv.DictReader((pub/'reference_tasks/rank_summary.csv').open()));motion=list(csv.DictReader((pub/'reference_tasks/motion_summary.csv').open()))
 tab=[r'\begingroup\small\setlength{\tabcolsep}{4pt}',r'\begin{longtable}{llrrrrr}',r'\caption{Standard order correlations and three-class geometric motion scores.}\label{tab:standard_tasks}\\\toprule',r'Data & Method & $\tau_b\uparrow$ & $\rho\uparrow$ & BA (\%)$\uparrow$ & F1 (\%)$\uparrow$ & Windows\\\midrule\endfirsthead',r'\toprule Data & Method & $\tau_b\uparrow$ & $\rho\uparrow$ & BA (\%)$\uparrow$ & F1 (\%)$\uparrow$ & Windows\\\midrule\endhead',r'\bottomrule\endfoot']
 for r in ranks:
  m=next(x for x in motion if x['dataset']==r['dataset'] and x['method']==r['method'] and x['scope']=='all_three_classes')
  scores=[f"{float(r[k]):.4f}" for k in ['Kendall_tau_b','Spearman_rho']]+[f"{100*float(m[k]):.1f}" if m[k] else '--' for k in ['balanced_accuracy','macro_F1']]
  tab.append(SHORT[r['dataset']]+' & '+r['method']+' & '+' & '.join(scores)+' & '+m['events']+r'\\')
 tab.extend([r'\end{longtable}',r'\noindent Correlations use the common $n\ge3$ frames and one fixed orientation calibration; BA and macro-F1 use all two-step tracked-pair windows, including unchanged truth. Gaussian has only unchanged labels and is not used to assess motion classification. PM2.5 has only ten windows. These are computational proxies, not participant responses.\endgroup'])
 (P/'tables/standard_tasks_supp.tex').write_text('\n'.join(tab)+'\n')
print('Generated named task-metric tables, dataset overview, standard cross-checks and unchanged-value source ledger')
