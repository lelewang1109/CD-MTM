"""Generate paper tables and aggregate prose strictly from completed experiment JSON.

Reject missing evidence, wrong dataset membership, or inconsistent frame counts.
Retired ERA5 evidence is never used when aggregating the revised paper.
"""
from pathlib import Path
import sys,json,hashlib,re,runpy,shutil,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
from dataset_suite import REAL_DATASETS,PAPER_DATASETS,PROXY_DATASETS,LABELS
PAPER=ROOT/'paper/pacificvis2027';OUT=ROOT/'results'
from result_tables import METHODS

def read(file):
 p=OUT/file
 if not p.exists():raise FileNotFoundError(f'Missing evidence: {p}')
 return json.loads(p.read_text())
def percent(x,d=1):return f'{100*x:.{d}f}'+r'\%'
def proxy(d,method,mode='proxy'):
 rows=[x for x in d[mode] if x['method']==method and x['k']==2 and x['eps']==.02]
 if len(rows)!=1:raise ValueError(f'Expected one completed motion row: {d.get("dataset")} / {method} / {mode}')
 return rows[0]
def tabular(cols,header,rows,caption,label,notes='',wide=False):
 env='table*' if wide else 'table'
 return '\n'.join([rf'\begin{{{env}}}[t]',rf'\caption{{{caption}}}',rf'\label{{{label}}}',r'\centering\footnotesize',
 r'\setlength{\tabcolsep}{3pt}',rf'\begin{{tabular}}{{{cols}}}\toprule',header+r'\\\midrule',
 *[r' & '.join(map(str,row))+r'\\' for row in rows],r'\bottomrule\end{tabular}',
 (r'\par\smallskip{\footnotesize\raggedright '+notes+r'\par}') if notes else '',rf'\end{{{env}}}'])

def main():
 reps={n:read(f'replicate_{n}.json') for n in PAPER_DATASETS}
 fronts={n:read(f'attainable_{n}.json') for n in PAPER_DATASETS}
 ev=read('eval_projection.json');fill=read('filling.json');rob=read('robustness.json');witness=read('witness.json')
 for n in PAPER_DATASETS:
  assert n==reps[n]['dataset']==fronts[n]['dataset']
  assert len(reps[n]['certificate']['H_per_frame'])==len(reps[n]['certificate']['F_per_frame'])==reps[n]['certificate']['frames']
  assert all(x['frames']==reps[n]['certificate']['frames'] for x in fill[n])
 for n in PROXY_DATASETS:assert ev[n]['dataset']==n
 for n in REAL_DATASETS:assert n in rob and n in witness
 short=dict(era5='ERA5',wildfire='Fire',olr='OLR',ring='Ring',gaussians='Gaussians',pm25='PM2.5')
 pos=read('final_performance.json')
 for n in PAPER_DATASETS:
  for source,digest in pos[n]['source_sha256'].items():
   if hashlib.sha256((ROOT/source).read_bytes()).hexdigest()!=digest:
    raise ValueError(f'Stale positional evidence for {n}: {source}; rerun result_tables.py')
 for n in PAPER_DATASETS:
  assert pos[n]['frames']==reps[n]['certificate']['frames']
  assert all(m in pos[n]['methods'] and m in ev[n]['hidden'] for m,_ in METHODS)
  assert len({proxy(ev[n],m)['clear'] for m,_ in METHODS})==1
 def cell(value,best,digits=2):
  if value is None:return '--'
  formatted=f'{100*value:.{digits}f}'
  return r'\textbf{'+formatted+'}' if best is not None and round(100*value,digits)==round(100*best,digits) else formatted
 native=read('native_merge_errors.json')
 for n in PAPER_DATASETS:
  assert all(native[n][m]['frames']==reps[n]['certificate']['frames'] for m in ('TMTM','ST-MTM','fixed-X anchored'))
  for source,digest in native[n]['source_sha256'].items():
   if hashlib.sha256((ROOT/source).read_bytes()).hexdigest()!=digest:raise ValueError(f'Stale native merge evidence: {n} / {source}')
 kept=['TMTM','ST-MTM','A']
 actual=['TMTM','ST-MTM','Hilbert','Morton','q-sort (packed)','A','R 20%']
 labels=dict(METHODS)
 labels.update({'A':'CD-MTM (tree kept)','R 20%':r'CD-MTM, $\kappa=20\%$','q-sort (packed)':'Packed sort (control)'})
 # Full interval-model certificate and width-free cross-method comparison are
 # separate panels: their values have distinct feasible sets.
 positionrows=[[r'\multicolumn{7}{l}{\textit{(a) Full interval-model certificate}}']]
 certificate={}
 for n in PAPER_DATASETS:
  c=reps[n]['certificate'];f=np.asarray(c['F_per_frame']);h=np.asarray(c['H_per_frame'])
  certificate[n]=dict(packing_mean=float(f.mean()),hierarchy_mean=float(h.mean()),
                      total_mean=float((f+h).mean()),total_max=float((f+h).max()))
 for key,label in [('packing_mean',r'Packing $\overline{\tau_{\free}}/L$'),('hierarchy_mean',r'Hierarchy $\overline{H}/L$'),('total_mean',r'Total bound $\overline{\tau^*}/L$'),('total_max',r'Worst-frame bound $\max_t\tau^*_t/L$')]:
  positionrows.append([label]+[cell(certificate[n][key],None) for n in PAPER_DATASETS])
 positionrows.append([r'\midrule\multicolumn{7}{l}{\textit{(b) Hierarchy-consistent orders: width-free comparison}}'])
 positionrows.append([r'Point bound $\overline{\tau^*_{\mathrm{pt}}}/L$']+[cell(pos[n]['bound_mean'],None) for n in PAPER_DATASETS])
 for m in kept:
  positionrows.append([labels[m]]+[cell(pos[n]['methods'][m]['mean'],min(pos[n]['methods'][k]['mean'] for k in kept)) for n in PAPER_DATASETS])
 positionrows.append([r'\midrule Frames']+[reps[n]['certificate']['frames'] for n in PAPER_DATASETS])
 positiontable=tabular('l'+'r'*len(PAPER_DATASETS),'Quantity / method & '+' & '.join(short[n] for n in PAPER_DATASETS),positionrows,
  r'Unavoidable position error under the original hierarchy (\% of reference extent $L$).','tab:position',
  r'(a) $\tau^*=\tau_{\free}+H$: packing constraints and additional hierarchy cost under the shared interval model; bars denote temporal means. (b) Mean framewise minimax order error under monotone calibration, removing widths/gaps; compare with the point bound, not (a). Raster ties use stable source-feature order. Bold marks lowest method error in (b), including displayed ties.',wide=True)
 def topology(n,m):
  if m in ('TMTM','ST-MTM','fixed-X anchored'):return native[n][m]
  if m=='A':
   f=next(x for x in fill[n] if x['cap']==0)
   return dict(mean_share=f['mean_opt_share'],max_share=f['D_opt_share'])
  return ev[n]['dstar'][m]
 toporows=[]
 for m in actual:
  row=[labels[m]]
  for n in PAPER_DATASETS:row.extend([cell(pos[n]['methods'][m]['mean'],None),cell(topology(n,m)['mean_share'],None)])
  if m=='A':row[0]=r'\midrule '+row[0]
  toporows.append(row)
 groups='Method & '+' & '.join(r'\multicolumn{2}{c}{'+short[n]+'}' for n in PAPER_DATASETS)
 group_rules=''.join(r'\cmidrule(lr){'+f'{2+2*i}-{3+2*i}'+'}' for i in range(len(PAPER_DATASETS)))
 subheader=' & '+' & '.join([r'$P$ & $D$']*len(PAPER_DATASETS))
 topotable=tabular('l'+'rr'*len(PAPER_DATASETS),groups+r'\\'+group_rules+subheader,toporows,
  r'Position improvement and its merge-level cost (\%; lower is better for each metric).','tab:tradeoff',
  r'$P$: mean framewise minimax order error / reference extent $L$, as in Table~\ref{tab:position}(b). $D$: mean framewise maximum tracked-extremum merge-level error / scalar range. TMTM, ST-MTM, Hilbert and Morton use rendered scalar barriers; CD-MTM and packed sort use optimal barrier filling (R verified against rendering). Rendering protocols differ on the same input; worst-frame costs are supplementary.',wide=True)
 # Keep spatial/motion validation available without adding main performance tables.
 spatialrows=[]
 for m,label in METHODS:
  row=[label]
  for n in PAPER_DATASETS:
   v=proxy(ev[n],m);stress=ev[n]['hidden'][m]['stress']
   row.extend([cell(stress,None,1),cell(v.get('error') if v.get('clear') else None,None,1)])
  spatialrows.append(row)
 spatialrows.append([r'\midrule Frames / events']+[x for n in PAPER_DATASETS for x in (str(ev[n]['hidden']['A']['neighbourhood_frames']),str(proxy(ev[n],'A')['clear']))])
 spatialtable=tabular('l'+'rr'*len(PAPER_DATASETS),groups+r'\\'+' & '+' & '.join(['Stress & Motion']*len(PAPER_DATASETS)),spatialrows,
  r'Supplementary spatial distance stress and motion error (\%).','tab:spatial',
  r'Stress: mean Kruskal stress-1 $\times100$ on frames with at least three extrema. Motion: reversal + miss at $k=2$, 2\% change threshold. The last row gives stress frames / clear events; -- denotes undefined motion error when no events exist. These are geometric proxies, not human accuracy.',wide=True)
 (PAPER/'spatial_motion_controls.tex').write_text(spatialtable+'\n')
 with (OUT/'final_performance.csv').open('w',newline='') as handle:
  writer=csv.writer(handle,lineterminator='\n')
  writer.writerow(['dataset','method','position_order_error_mean_pct','point_certificate_mean_pct','packing_certificate_mean_pct','hierarchy_certificate_mean_pct','full_certificate_mean_pct','merge_error_mean_pct','merge_error_max_pct','spatial_stress_pct','motion_error_pct','clear_events'])
  for n in PAPER_DATASETS:
   for m,_ in METHODS:
    v=proxy(ev[n],m);stress=ev[n]['hidden'][m]['stress'];d=topology(n,m) if m!='oracle q' else None
    writer.writerow([n,m,100*pos[n]['methods'][m]['mean'],100*pos[n]['bound_mean'],100*certificate[n]['packing_mean'],100*certificate[n]['hierarchy_mean'],100*certificate[n]['total_mean'],100*d['mean_share'] if d else '',100*d['max_share'] if d else '',100*stress if stress is not None else '',100*v['error'] if v['clear'] else '',v['clear']])
 diagnosticrows=[]
 for n in PAPER_DATASETS:
  for m in actual:
   d=topology(n,m)
   diagnosticrows.append([short[n],labels[m],f"{100*d['max_share']:.2f}",f"{100*d['mean_share']:.2f}",f"{d['segments_mean']:.1f}" if 'segments_mean' in d else '--'])
 diagnostic=tabular('llrrr','Data & Method & Max merge \% & Mean merge \% & Runs',diagnosticrows,
  'Supplementary worst-frame merge costs and native fragmentation.','tab:merge_diagnostics',
  'The same merge-cost protocols as main Table 2 are used. Mean is the temporal mean of framewise maxima; max is the worst frame. Runs apply to native curve source supports. Exact projection has no rendered scalar topology.')
 (PAPER/'performance_diagnostics.tex').write_text(diagnostic+'\n')
 shares=[reps[n]['certificate']['conflict_share'] for n in REAL_DATASETS]
 max_fill=max(x['measured_vs_closed_form_max'] for n in PAPER_DATASETS for x in fill[n])
 sigmaolr=read('protocol_olr.json')['sigma_km']
 sigmapm=read('protocol_pm25.json')['sigma_km']
 pmst=proxy(ev['pm25'],'ST-MTM');pma=proxy(ev['pm25'],'A');pmr=proxy(ev['pm25'],'R 20%')
 pmc=reps['pm25']['certificate'];pmt=ev['pm25']['dstar']['R 20%']
 pmprose=(f"PM2.5 has {pmc['conflict_frames']}/{pmc['frames']} conflict frames and {pmr.get('clear',0)} clear 2-D motion events. "
          + (f"At $\\kappa=20\\%$, total proxy error is {percent(pmst['error'])} for ST-MTM, {percent(pma['error'])} for A, and {percent(pmr['error'])} for R; R's maximum merge-level distortion is {percent(pmt['max_share'])} of the processed concentration range. " if pmr.get('clear') else "There are no clear events at this setting; no motion-error rate is inferred. ")
          +f"Hilbert has {percent(proxy(ev['pm25'],'Hilbert')['error'])} total error and Morton {percent(proxy(ev['pm25'],'Morton')['error'])}; R therefore ties Morton on only seven events. This sparse, selected comparison is descriptive.")
 seasontext=''
 seasonplan=OUT/'pm25_season_protocol.json'
 if seasonplan.exists():
  plan=json.loads(seasonplan.read_text())
  if plan['status']=='complete':
   rows=[]
   for n in plan['periods']:
    values=[proxy(ev[n],m) for m in ('ST-MTM','A','R 20%')]
    rows.append([n.split('_')[-1].title(),values[-1]['clear'],*[f"{100*v['error']:.1f}" if v.get('clear') else '--' for v in values]])
   season_table=tabular('lrrrr','Month & Cases & ST-MTM & A & R20',rows,
     r'Exploratory PM2.5 seasonal controls: total motion error (\%).','tab:pm_seasons')
   (PAPER/'seasonal_controls.tex').write_text(season_table)
   seasontext=r"\textbf{Seasonal control.} January, April, July and October 2000 each use 30 consecutive days, the same domain, and a common 100\,km scale fixed from extrema counts across all 120 frames before evaluation. All four eight-stage runs and the original January--February sequence remain in the supplement. The main display uses January after this comparison; sparse cases and selection do not establish universal superiority."
 frames=sum(reps[n]['certificate']['frames'] for n in PAPER_DATASETS)
 text=r'''\section{Evaluation of Diagnosis and Trade-offs}\label{sec:eval}
The two primary questions are \textbf{RQ1}, unavoidable position error under the original hierarchy, and \textbf{RQ2}, the merge-level cost of improving positions. \textbf{RQ3} tests geometric motion readings and \textbf{RQ4} tests transfer to dendrograms as secondary validation. Four real sequences and two synthetic controls test these questions; the winter case illustrates interpretation without measuring human performance.

\subsection{Datasets, baselines, and validation protocol}
'''+positiontable+topotable+r'''

\textbf{Pressure data.} We retain ERA5 mean sea-level pressure for 1999-11-17--2000-01-14, sampled every 12 hours over the North Atlantic and Europe (25--80\textdegree N, 40\textdegree W--50\textdegree E)~\cite{Hersbach:2020:ERA5}. A $49\times49$ equal-area grid and 250\,km Gaussian smoothing define join-tree minima. Smoothing is performed on a buffered domain; only extrema of that extended field inside the window are retained, and other cropped basins are filled to their spill levels. These are processed-field minima, not independently validated cyclone centres.

\textbf{Fire and synthetic controls.} Australian fire radiative power, November--December 2019, uses 30 two-day frames on a $64\times64$ grid of $\log(1+\mathrm{FRP})$~\cite{Franke:2021:1DP}. A weak background removes zero plateaus; the smallest common smoothing scale with at most 12 maxima permits exact frontiers. Ring and the three-Gaussian scene are synthetic controls.

\textbf{Radiation fields.} Daily NOAA OLR CDR (PSL Ver01Rev02)~\cite{NOAA:OLR} covers 2024-06-01--2024-07-30 over 15\textdegree S--20\textdegree N, 60--150\textdegree E. Join-tree minima represent low radiation, not validated convective systems. A $49\times49$ equal-area grid uses five-cell buffers, priority-flood cropping, and no added imputation; a global-extremum fallback is logged. The fixed ladder (100, 150, 200, 250, 350, 500, 700, 1000\,km) selects the smallest common scale with at most eight extrema, independently of performance: '''+f'{sigmaolr:g}'+r'''\,km. Source hashes and preprocessing trials are recorded.

\textbf{PM2.5 concentration.} The integrated China dataset (V2, 10-km grid)~\cite{Dong:2026:PM25} supplies 30 fields, 2000-01-01--2000-01-30, over 28--38\textdegree N, 102--114\textdegree E. Files carry 10:30 timestamps without an explicit averaging interval. The same buffered grid and eight-extremum rule select '''+f'{sigmapm:g}'+r'''\,km smoothing for split-tree maxima. Values retain $\mu$g\,m$^{-3}$ units. Metadata record upstream linear-then-nearest filling; we add no imputation. Per-file hashes identify the local snapshot. January was chosen for the main display after the exploratory seasonal comparison; its performance is a selected case, not an independent validation.

\textbf{Methods.} TMTM and our reimplementation of ST-MTM represent existing tree-preserving maps. Hilbert and Morton provide native sample-domain linearizations, as in TMTM~\cite{Koepp:2023:TMTM}; they retain every processed grid sample in a fixed order across time. Our canonical 2-D curves use a minimal power-of-two indexing square, discard exterior cells, and fix x=column, y=row without orientation tuning. Extremum anchors use sample ranks; pairwise native merge errors use maxima/minima along the unchanged sequence, with no optimal refilling. CD-MTM is our certificate-driven reference-anchored pipeline. Its tree-preserving mode (A in the saved records) retains the hierarchy; its relaxed mode (R) uses $\kappa\in\{2\%,20\%,\infty\}$ of the scalar range. A sorted, packed baseline drops hierarchy while sharing R's interval geometry and secondary objective; exact projection places anchors directly at their references. Every method uses the same processed fields, trees, supports, and correspondences. Width, gap, canvas, slack and eccentricity rules are shared by A, R and packed sorting across datasets; native curves have no feature-interval constraints. The automatic direction is fitted from the full sequence; fixed directions and exact projection are supplementary controls, not competing CD-MTM variants.

\textbf{Checks.} The shared pipeline checks interval legality, widths, gaps, canvas, eccentricity, positional budget, and rendered merge levels. For each sequence, the exact frontier is enumerated over all leaf orders; $F_T(0)=\tau^*$ is checked independently. Across the '''+str(frames)+r''' evaluated frames, the largest normalized discrepancy between measured barrier-filling error and its closed form is '''+f'{max_fill:.2g}'+r''', including the strict-extremum clearance. Full-layout scalability remains limited by order enumeration; the large-leaf benchmark concerns certificate diagnosis.

\subsection{RQ1: Unavoidable position error under topology constraints}\label{sec:rq1}
\begin{figure*}[t]
\centering\includegraphics[width=\linewidth]{fig_rq1}
\caption{Packing cost $\tau_{\free}$ (grey) and hierarchy cost $H$ (orange) per frame for the four real sequences; dotted: $\theta=2\%$ of the axis. Their sum is the minimum possible maximum positional error.}
\label{fig:rq1}
\end{figure*}

Figure~\ref{fig:rq1} separates packing from the additional cost of subtree contiguity; Table~\ref{tab:position}(a) quantifies the unavoidable error $\tau^*=\tau_{\free}+H$ and separates packing from hierarchy costs; panel (b) compares hierarchy-consistent orders under the width-free model. Conflict shares span '''+percent(min(shares),0)+'--'+percent(max(shares),0)+r''' under these extraction protocols, not as general incidence estimates.

A conflict needs at least three leaves and depends on both the hierarchy and the chosen reference. The retained ERA5 sequence has conflicts in 34\% of frames and fire in 63\%; these values are not used to select the new domains or their smoothing scales. Eight fixed directions and thresholds of 1\%, 2\%, and 5\% are evaluated for all four real sequences in the supplement. Witness triples explain the conflicting features where present. Persistence simplification is tested separately: it can remove conflicts by deleting extrema, whereas flattening retains them and changes merge relations. All rates refer to the resulting processed fields.

\subsection{RQ2: Position improvement and topological cost}\label{sec:cost}
\begin{figure*}[!t]
\centering\includegraphics[width=\linewidth]{fig_frontier_exact}
\caption{Exact attainable frontier $F$ (blue), certified lower bound $\Phi$ (dashed), and R for the six evaluated sequences. Filled points use optimal barrier filling; open points use LCA filling. The vertical axis reports mean fixed-order position optimum, excluding layout slack.}
\label{fig:frontier}
\end{figure*}

Barrier filling attains $\delta^*(\pi)$ for each order while keeping extremum values, for both join and split trees. Table~\ref{tab:tradeoff} reports mean merge-level costs, with worst-frame costs in the supplement: the $\kappa=20\%$ merge-gap threshold is not a distortion bound. Packed sorting drops hierarchy entirely. Sequences without triggered conflicts test preservation and offer no relaxation benefit. The bound $\Phi$ ignores fixed leaf heights and need not be attainable.

Table~\ref{tab:tradeoff} pairs position error with merge-level cost. Native-curve fragmentation, neighbourhood preservation, temporal changes, frontier excess and pruning controls remain supplementary diagnostics. These support interpretation of the trade-off; they are not additional primary performance criteria.

\subsection{RQ3: Geometric motion error and projection loss}\label{sec:motion}
We simulate approach/separation readings over $k=2$ steps: 24\,h for ERA5, four days for fire, and two days for OLR and PM2.5. These are comparable step windows, not equal physical durations. A clear 2-D event changes extremum distance by more than 2\% of the domain diagonal. A reversal reads its opposite; a miss reads no change; total error is their sum. Projected-reference events instead use 2\% of the reference-axis extent. Paired comparisons use circular moving-block bootstrap over time with $k+2$-step blocks; results with sparse cases are descriptive.

Against the projected reference, the exact-projection baseline has zero error by construction. Its 2-D error can remain positive because motion orthogonal to one direction is lost. The projected and 2-D definitions select different clear events, so subtracting their rates does not isolate projection loss. The proxy assumes known feature identities and anchors; it does not measure human performance.

On the retained ERA5 period, R at $\kappa=20\%$ reduces total 2-D proxy error from ST-MTM's 41.3\% to 18.3\%, with maximum merge-level distortion of 26.1\% of the scalar range. On fire it reduces reversals from 21.4\% to 6.2\% but total error only from 35.7\% to 31.2\%: some reversals become misses. The supplementary spatial controls report all six sequences and their actual clear-case counts, including results with no relaxation. The method therefore offers a measured position--topology trade-off rather than guaranteed dominance of ST-MTM or reference sorting.

On OLR, A and R at $\kappa=20\%$ both have 5.4\% total 2-D proxy error, while R incurs maximum merge-level distortion of 33.6\% of the value range. Better positional alignment therefore need not improve this motion proxy.

'''+pmprose+'\n\n'+seasontext+r'''

The supplement reports three change thresholds, four step windows, fixed-direction relaxation, and per-feature diagnostic flags for each active real sequence. These are exploratory analyses without multiplicity correction; the original multi-period ERA5 aggregates are not carried into the revised evaluation.

'''
 text+=r'''\begin{figure*}[!t]
\centering\includegraphics[width=\linewidth]{fig_witness}
\caption{Retained ERA5 winter case. The tree-preserving map shows witness triples, the spatial field and projected extrema explain the conflict, and the relaxed map ($\kappa=20\%$) discloses achieved position and merge-level errors.}
\label{fig:witness}
\end{figure*}

'''
 # Preserve the established winter case and RQ4; replace only the old experimental section.
 main=PAPER/'main.tex';src=main.read_text()
 src=re.sub(r'\\begin\{figure\*\}\[t\]\s*\\centering\s*\\includegraphics\[width=\\linewidth\]\{fig_rq1\}.*?\\end\{figure\*\}', '', src, flags=re.S)
 start=src.index(r'\input{experiments_revised}') if r'\input{experiments_revised}' in src else src.index(r'\section{Evaluation of Diagnosis and Trade-offs}')
 end=src.index(r'\subsection{Illustrative case: a winter pressure conflict}',start)
 (PAPER/'experiments_revised.tex').write_text(text.rstrip()+'\n')
 src=src[:start]+r'\input{experiments_revised}'+ '\n\n'+src[end:]
 src=re.sub(r'Under the evaluated extraction protocols, hierarchy conflicts affect .*? sequences\.',lambda _: 'Under the evaluated extraction protocols, hierarchy conflicts affect '+percent(min(shares),0)+'--'+percent(max(shares),0)+' of frames across pressure, wildfire, outgoing-radiation, and PM2.5 sequences.',src)
 src=src.replace('It captures 0.71 of the squared tracked motion in ERA5 2013/14 and 0.89 in 1999/2000.','It captures 0.89 of the squared tracked motion in the retained ERA5 1999/2000 sequence.')
 src=src.replace('On the real datasets, the best witness explains a median of 86--94\\% of $\\tau^*$ in conflict frames, so one triple accounts for most of the optimum in the median conflict frame.',
  'On the retained ERA5 and fire sequences, the best witness explains median fractions of '+percent(witness['era5']['median'],0)+' and '+percent(witness['wildfire']['median'],0)+' of $\\tau^*$, respectively; sequences without conflicts do not contribute a witness statistic.')
 src=re.sub(r' SST has only four clear 2-D motion cases and \d+ of 60 frames use the logged global-extremum fallback; its no-conflict result concerns this sparse extraction, not ocean fields in general\.', '', src)
 src=src.replace('pressure and wildfire examples reduce geometric motion-proxy error at measurable topological cost.','the multi-domain evaluation distinguishes useful relaxations from cases that retain the original hierarchy.')
 src=src.replace('Fire data: Franke et al.~\\cite{Franke:2021:1DP} (CC BY 4.0); ERA5: Copernicus~\\cite{Hersbach:2020:ERA5}; coastlines: Natural Earth (public domain).',
  'Fire data: Franke et al.~\\cite{Franke:2021:1DP} (CC BY 4.0); ERA5: Copernicus~\\cite{Hersbach:2020:ERA5}; OLR: NOAA~\\cite{NOAA:OLR}, provided by NOAA PSL, Boulder, Colorado, USA; coastlines: Natural Earth (public domain).')
 src=src.replace('coastlines: Natural Earth (public domain).','PM2.5: integrated China dataset V2~\cite{Dong:2026:PM25} (CC BY 4.0); coastlines: Natural Earth (public domain).') if 'PM2.5: integrated China' not in src else src
 src=src.replace(r'SST and OLR: NOAA~\cite{NOAA:OISST,NOAA:OLR}',r'OLR: NOAA~\cite{NOAA:OLR}')
 src=src.replace(r'(\cref{tab:spatial})',r'(supplementary spatial controls)').replace(r'(\cref{tab:hidden})',r'(supplementary spatial controls)')
 main.write_text(src)
 files=[f'replicate_{n}.json' for n in PAPER_DATASETS]+[f'attainable_{n}.json' for n in PAPER_DATASETS]+[f'protocol_{n}.json' for n in ('olr','pm25')]+['final_performance.json','native_merge_errors.json','eval_projection.json','filling.json','robustness.json','witness.json','sfc_baseline_protocol.json']
 if seasontext:files+=['pm25_season_protocol.json','method_performance_audit.json']+[f'replicate_{n}.json' for n in plan['periods']]
 audit=dict(active_real=list(REAL_DATASETS),active_all=list(PAPER_DATASETS),retired=['era5_2014','oisst'],frames=frames,
  conflict_share_range=[min(shares),max(shares)],source_sha256={f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in files})
 (OUT/'revised_paper_evidence.json').write_text(json.dumps(audit,indent=2))
 runpy.run_path(str(ROOT/'analysis/fig_rq1.py'),run_name='__main__')
 import attainable
 attainable.plot()
 for figure in ('fig_rq1.pdf','fig_frontier_exact.pdf'):
  shutil.copy2(OUT/figure,PAPER/'figures'/figure)
 print('Generated two consolidated main performance tables, supplementary diagnostics, prose and evidence hashes.')

if __name__=='__main__':main()
