"""Report the declared motion setting and all evaluated controls without winner selection."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
from dataset_suite import PROXY_DATASETS
from pm25_seasons import PERIODS,PLAN

def main():
 source=ROOT/'results/eval_projection.json';j=json.loads(source.read_text());rows=[]
 for n in [*PROXY_DATASETS,*PERIODS]:
  if n not in j:continue
  d=j[n];v={x['method']:x for x in d['proxy'] if x['k']==2 and x['eps']==.02}
  if not v:continue
  if not v['R 20%'].get('clear'):
   rows.append(dict(dataset=n,setting=dict(k=2,eps=.02),clear=0,
    total_errors={k:None for k in v if not k.startswith('oracle')},best_methods=[],
    R20_best=None,R20_minus_ST=None,R20_minus_A=None,bootstrap_comparisons=[],
    topology_R20=d['dstar']['R 20%'],exact_projection_2d_error=None))
   continue
  candidates={k:x['error'] for k,x in v.items() if not k.startswith('oracle')}
  best=min(candidates.values());r=v['R 20%'];a=v['A'];s=v['ST-MTM']
  comparisons=[x for x in d['paired'] if x['method']=='R 20%' and x['k']==2 and x['eps']==.02 and x['other'] in ('ST-MTM','A','Hilbert','Morton')]
  rows.append(dict(dataset=n,setting=dict(k=2,eps=.02),clear=r['clear'],
    total_errors=candidates,best_methods=[k for k,x in candidates.items() if abs(x-best)<1e-12],
    R20_best=abs(r['error']-best)<1e-12,R20_minus_ST=r['error']-s['error'],R20_minus_A=r['error']-a['error'],
    bootstrap_comparisons=comparisons,topology_R20=d['dstar']['R 20%'],
    exact_projection_2d_error=v['oracle q']['error']))
 out=dict(metric='2-D motion proxy total error (reversal + miss); lower is better',
  main_methods='Fixed kappa=20%, k=2, eps=2%; caps/axes are not selected separately for each dataset',
  controls='oracle q/x are projection references, excluded from feasible-method ranking; fixed-axis control remains included',
  inference='Exploratory seasonal runs are reported in full; sparse cases and uncorrected multiple comparisons do not establish universal superiority',
  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),results=rows,
  all_main_R20_best=all(x['R20_best'] is True for x in rows if x['dataset'] in PROXY_DATASETS))
 (ROOT/'results/method_performance_audit.json').write_text(json.dumps(out,indent=2))
 lines=['# Method performance audit','',out['metric'], '', '| Dataset | Cases | ST-MTM | A | R20 | Best feasible method(s) |', '|---|---:|---:|---:|---:|---|']
 for x in rows:
  v=x['total_errors'];fmt=lambda m: f'{100*v[m]:.1f}%' if v[m] is not None else '--'
  lines.append(f"| {x['dataset']} | {x['clear']} | {fmt('ST-MTM')} | {fmt('A')} | {fmt('R 20%')} | {', '.join(x['best_methods']) or 'No clear events'} |")
 lines+=['',out['main_methods'],out['controls'],out['inference'],'','No guarantee of best performance follows from these records.']
 (ROOT/'notes/method-performance-audit.md').write_text('\n'.join(lines)+'\n')
 print('\n'.join(lines))
if __name__=='__main__':main()
