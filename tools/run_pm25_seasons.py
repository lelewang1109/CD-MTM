"""Compare four predefined 30-day months without selecting a winning subset.

Freeze a common smoothing scale based only on extrema counts across all
120 frames, then run the eight unchanged evidence stages for every month.
Seasonal entries stay outside the main paper membership.
"""
from pathlib import Path
import sys,json,subprocess,time,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'analysis'),str(ROOT/'tools')]
import pm25_seasons as seasons, public_scalar as ps,prepare_cn_pm25 as cn
from run_paper_suite import STAGES

def main():
 seasons.register(fixed=False)
 for n in seasons.PERIODS:cn.prepare(ROOT.parent/'data/real/CN-Reanalysis/2000',n)
 trials=[]
 for sigma in ps.SIGMAS_KM:
  counts={}
  for n in seasons.PERIODS:
   ps.SPECS[n]['fixed_sigma_km']=sigma
   try:
    *_,p=ps.prepare_fields(n);counts[n]=max(x['leaves_max'] for x in p['sigma_trials'])
   except ValueError as e:
    if 'No fixed smoothing scale meets leaf limit' not in str(e):raise
    counts[n]='exceeds limit'
  trials.append(dict(sigma_km=sigma,maximum_extrema=counts))
  if all(isinstance(x,int) and x<=ps.MAX_LEAVES for x in counts.values()):break
 else:raise ValueError('No shared tractable scale')
 plan=dict(periods=seasons.PERIODS,frames_per_month=30,shared_sigma_km=sigma,trials=trials,
  selection='four predefined seasons; all results reported; not selected for performance',
  status='running',runs=[],source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'analysis').rglob('*.py')})
 def save():seasons.PLAN.write_text(json.dumps(plan,indent=2))
 save();out=ROOT/'results/revised_suite';out.mkdir(exist_ok=True)
 for n in seasons.PERIODS:
  for stage in STAGES:
   log=out/f'{n}_{stage}.log';print(n,stage,flush=True);start=time.perf_counter()
   code="import sys,runpy;sys.path.insert(0,'analysis');import pm25_seasons as s;s.register();"
   if stage=='replicate':code+="import replicate as r;r.run(sys.argv[1])"
   else:code+=f"sys.argv=['analysis/{stage}.py',sys.argv[1]];runpy.run_path(sys.argv[0],run_name='__main__')"
   with log.open('w') as f:r=subprocess.run([sys.executable,'-W','ignore','-c',code,n],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
   plan['runs'].append(dict(dataset=n,stage=stage,exit_code=r.returncode,seconds=time.perf_counter()-start,log=str(log.relative_to(ROOT))))
   if r.returncode:plan['status']='failed';save();print(log.read_text()[-4000:]);raise SystemExit(r.returncode)
   save()
 plan['status']='complete';save()
 print('All four seasonal comparisons complete',flush=True)
if __name__=='__main__':main()
