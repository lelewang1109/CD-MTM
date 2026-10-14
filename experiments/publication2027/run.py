"""Recompute scientific evidence without rewriting manuscript prose.
Run from any directory: python experiments/publication2027/run.py [--datasets ...].
Default: the six active sequences, five numerical stages. Other stages are explicit.
"""
from pathlib import Path
import argparse, hashlib, json, os, platform, subprocess, sys, time
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analysis'))
from dataset_suite import PAPER_DATASETS
STAGES = ('replicate', 'evaluation', 'attainable', 'filling', 'robustness',
          'pointcert', 'persistence', 'witness_stats', 'result_tables', 'native_merge_errors')
DEFAULT = ('evaluation', 'filling', 'pointcert', 'result_tables', 'native_merge_errors')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--datasets', nargs='+', choices=PAPER_DATASETS, default=list(PAPER_DATASETS))
    p.add_argument('--stages', nargs='+', choices=STAGES, default=list(DEFAULT))
    a = p.parse_args()
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = ROOT / 'results/publication2027/runs' / stamp
    out.mkdir(parents=True, exist_ok=False)
    manifest = dict(status='running', started_utc=stamp, datasets=a.datasets, stages=a.stages,
        python=sys.version, platform=platform.platform(), runs=[],
        source_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
                      for folder in ('src', 'analysis', 'experiments')
                      for f in sorted((ROOT/folder).rglob('*.py'))})
    def save():
        (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    save()
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT/'src') + os.pathsep + str(ROOT)
    env['MPLBACKEND'] = 'Agg'
    for name in a.datasets:
        for stage in a.stages:
            log = out/f'{name}_{stage}.log'
            cmd = [sys.executable, '-W', 'ignore', str(ROOT/'analysis'/f'{stage}.py'), name]
            if stage == 'replicate':
                cmd = [sys.executable, '-W', 'ignore', '-c',
                       "import sys;sys.path.insert(0,'analysis');import replicate;replicate.run(sys.argv[1])", name]
            print(f'Running {name}: {stage}', flush=True)
            start = time.perf_counter()
            with log.open('w') as f:
                code = subprocess.run(cmd, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
            manifest['runs'].append(dict(dataset=name, stage=stage, exit_code=code,
                seconds=time.perf_counter()-start, log=str(log.relative_to(ROOT))))
            if code:
                manifest['status']='failed'; save()
                print(log.read_text()[-4000:]); raise SystemExit(code)
            save()
            print(f'Completed {name}: {stage}', flush=True)
    manifest['status']='complete'
    manifest['finished_utc']=time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    manifest['result_sha256']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
                             for f in sorted((ROOT/'results').glob('*.json'))}
    save()
    print(f'Completed; manifest: {out / "manifest.json"}', flush=True)

if __name__ == '__main__': main()
