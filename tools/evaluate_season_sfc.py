"""Refresh every exploratory month's motion evaluation with both native SFCs."""
from pathlib import Path
import sys,subprocess,json,time,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
from pm25_seasons import PERIODS
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--defer-merge',action='store_true',help='Save isolated records; merge only after other evaluation writers finish')
args=parser.parse_args()
out=ROOT/'results/revised_suite';records=out/'season_sfc_records';records.mkdir(parents=True,exist_ok=True)
manifest=dict(status='running',runs=[],merge_deferred=args.defer_merge,
 source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ('analysis','src') for p in (ROOT/d).rglob('*.py')})
for n in PERIODS:
 print('SFC seasonal evaluation',n,flush=True);start=time.perf_counter();log=out/f'{n}_evaluation_sfc.log'
 code="import sys;from pathlib import Path;sys.path.insert(0,'analysis');import pm25_seasons as s;s.register();import evaluation as e;e.OUT=Path('results/revised_suite/season_sfc_records');sys.argv=['analysis/evaluation.py',sys.argv[1]];e.main()"
 with log.open('w') as f:r=subprocess.run([sys.executable,'-W','ignore','-c',code,n],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 manifest['runs'].append(dict(dataset=n,exit_code=r.returncode,seconds=time.perf_counter()-start,log=str(log.relative_to(ROOT))))
 if r.returncode:manifest['status']='failed'
 (out/'season_sfc_manifest.json').write_text(json.dumps(manifest,indent=2))
 if r.returncode:print(log.read_text()[-3000:]);raise SystemExit(r.returncode)
if not args.defer_merge:
 target=ROOT/'results/eval_projection.json';data=json.loads(target.read_text());data.update(json.loads((records/'eval_projection.json').read_text()));target.write_text(json.dumps(data,indent=1))
manifest['status']='complete';(out/'season_sfc_manifest.json').write_text(json.dumps(manifest,indent=2))
