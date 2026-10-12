"""Run the shared evidence chain; default membership comes from dataset_suite.

Example: PYTHONPATH=src python3 tools/run_paper_suite.py --datasets olr pm25
The stdout/stderr logs and status manifest identify incomplete runs explicitly.
"""
from pathlib import Path
import argparse,sys,subprocess,json,hashlib,platform,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'))
from dataset_suite import PAPER_DATASETS
STAGES=('replicate','evaluation','attainable','filling','robustness','pointcert','persistence','witness_stats','result_tables','native_merge_errors')

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--datasets',nargs='+',choices=PAPER_DATASETS,default=list(PAPER_DATASETS))
 p.add_argument('--stages',nargs='+',choices=STAGES,default=list(STAGES))
 a=p.parse_args();out=ROOT/'results/revised_suite';out.mkdir(parents=True,exist_ok=True)
 manifest=dict(datasets=a.datasets,stages=a.stages,status='running',python=sys.version,platform=platform.platform(),runs=[],
  source_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for d in ('analysis','src','experiments') for f in (ROOT/d).rglob('*.py')})
 def save(): (out/('run_manifest_'+'_'.join(a.datasets)+'.json')).write_text(json.dumps(manifest,indent=2))
 save()
 for n in a.datasets:
  for stage in a.stages:
   log=out/f'{n}_{stage}.log';start=time.perf_counter()
   if stage=='replicate':
    code="import sys;sys.path.insert(0,'analysis');import replicate as r;r.run(sys.argv[1])"
    cmd=[sys.executable,'-W','ignore','-c',code,n]
   else:cmd=[sys.executable,'-W','ignore',f'analysis/{stage}.py',n]
   print(f'Running {n}: {stage}',flush=True)
   with log.open('w') as f:ret=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
   row=dict(dataset=n,stage=stage,exit_code=ret.returncode,seconds=time.perf_counter()-start,log=str(log.relative_to(ROOT)))
   manifest['runs'].append(row);save()
   if ret.returncode:
    manifest['status']='failed';save();print(log.read_text()[-5000:]);raise SystemExit(ret.returncode)
   print(f'Completed {n}: {stage} ({row["seconds"]:.1f}s)',flush=True)
 manifest['status']='complete';save()

if __name__=='__main__':main()
