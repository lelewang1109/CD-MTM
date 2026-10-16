"""Check bundle provenance, rerun completion and numerical manuscript claims."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'analysis'))
from provenance import verify_saved_file
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--require-complete-run',action='store_true');a=p.parse_args()
 out=ROOT/'results/publication2027';m=read(out/'manifest.json');checks=[]
 for r in m['records']:
  assert digest(ROOT/r['source'])==r['source_sha256'],r['source']
  assert digest(ROOT/r['snapshot'])==r['snapshot_sha256'],r['snapshot']
 for name,h in m['generated_tables'].items():assert digest(ROOT/name)==h,name
 for name,h in m['source_sha256'].items():verify_saved_file(ROOT,name,h)
 for r in m['figures']:assert digest(ROOT/r['source'])==r['sha256'],r['figure']
 figure_data=out/'figure_data';fm=read(figure_data/'figure_manifest.json')
 for n,h in fm['evidence_sha256'].items():assert digest(ROOT/'results'/n)==h,n
 for n,h in fm['render_exports'].items():
  assert digest(figure_data/f'{n}_render.npz')==h,n
  meta=read(figure_data/f'{n}_render.json')
  for source,source_hash in meta['source_sha256'].items():verify_saved_file(ROOT,source,source_hash)
 for n,h in fm['figures'].items():assert digest(ROOT/'paper/pacificvis2027-restructured/figures'/f'{n}.pdf')==h,n
 assert fm['selection']['era5']['frame']==48
 checks.append('All evidence, tables, numeric render exports and figure hashes match')
 c=read(out/'claims.json');ev=read(out/'evidence/main/eval_projection.json');pos=read(out/'evidence/main/final_performance.json')
 assert c['frames']==342
 assert c['conflict_frames']==dict(era5=40,wildfire=19,olr=7,pm25=5,ring=21,gaussians=47)
 expected={'era5':(104,43,19),'wildfire':(112,40,35),'olr':(56,12,3),'pm25':(7,3,2),'ring':(124,43,16),'gaussians':(0,0,0)}
 # Only claims used in the main narrative are asserted; the full CSV preserves all methods.
 for n,(clear,st,relaxed) in list(expected.items())[:4]:
  rows=c['motion'][n];assert rows['ST-MTM']['clear']==clear,n
  assert round(rows['ST-MTM']['error']*clear)==st,n
  assert round(rows['R 20%']['error']*clear)==relaxed,n
 assert c['motion']['gaussians']['A']['clear']==0
 assert c['filling_discrepancy']<1.2e-5
 assert round(100*pos['era5']['methods']['ST-MTM']['mean'],2)==16.28
 assert round(100*pos['era5']['methods']['A']['mean'],2)==3.77
 assert round(100*pos['era5']['methods']['R 20%']['mean'],2)==1.16
 for n in ['olr']:
  assert abs(c['motion'][n]['A']['error']-c['motion'][n]['R 20%']['error'])<1e-12
 paired=[r for r in ev['era5']['paired'] if r['method']=='R 20%' and r['other']=='ST-MTM' and r['k']==2 and r['eps']==.02][0]['err']
 assert round(100*paired['diff'],1)==-23.1
 assert [round(100*v,1) for v in paired['ci95']]==[-33.6,-12.8]
 on=sum(next(v for v in rows if v['cap']==.2)['frames_pareto_optimal'] for rows in c['frontier'].values())
 assert on==339,on
 checks.append('Main numerical claims agree with result files, including sparse and negative cases')
 runs=sorted((out/'runs').glob('*/manifest.json'))
 latest=read(runs[-1]) if runs else None
 if a.require_complete_run:
  assert latest and latest['status']=='complete','Numerical suite incomplete'
  assert latest['datasets']==m['active_datasets']
  assert len(latest['runs'])==30 and all(r['exit_code']==0 for r in latest['runs'])
  checks.append('All 30 declared rerun stages completed successfully')
 report=dict(status='passed',checks=checks,run_manifest=str(runs[-1].relative_to(ROOT)) if runs else None)
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('\n'.join(checks))
if __name__=='__main__':main()
