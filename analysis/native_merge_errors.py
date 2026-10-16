"""Measure baseline scalar barriers at the exact anchors used in evaluation.

No synthetic zero is assigned to a nominal raster. Original source trees and
processed fields are shared with the positional/motion evaluation.
"""
from pathlib import Path
import sys, json, hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'))
import replicate as rp
import general_method as gm
import relax_hierarchy as rh
import attainable as at
from experiments import era5 as ep
from rgmtm.baselines.space_filling import merge_levels_on_line
from rgmtm.error_budget import solve_sequence
from rgmtm.reference_points import reference_points_from_frames
from dataset_suite import PAPER_DATASETS


def measure(sc, matrix, anchors):
    kind=sc['trees'][0].kind
    errors=[]
    for t,(frame,ids,ranks) in enumerate(zip(sc['frames'],sc['ids'],anchors)):
        true=at.lca_matrix(frame,ids,kind)*(-1 if kind=='split' else 1)
        native=merge_levels_on_line(matrix[:,t],ranks,kind)
        errors.append(float(np.max(np.abs(native-true))))
    span=float(np.ptp(sc['fields']))
    return dict(max_share=max(errors)/span,mean_share=float(np.mean(errors))/span,
                per_frame_share=[x/span for x in errors],frames=len(errors),
                definition='native scalar barriers at displayed extremum anchors; includes diagonal extremum values')


def main():
    path=ROOT/'results/native_merge_errors.json'
    saved=json.loads(path.read_text()) if path.exists() else {}
    for name in (sys.argv[1:] or PAPER_DATASETS):
        print('Measuring native baselines:',name,flush=True)
        ds=rp.LOADERS[name]();sc=ds['sc'];span=ds['native_span']
        p=gm.Parameters(canvas=span,canvas_origin=float(min(ds['lo'][0],0.)),
                        width_scale=.5*span/ds['domain_area'],gap=span/240,
                        extra_budget=span/120,rho=.5)
        output={}
        for method in ('TMTM','ST-MTM'):
            kw=dict(canvas=span,length=ds['nominal'],refine_raster=False,strict_checks=False)
            if name=='ring':kw['stmtm_parameters']=ep.b2.LayoutParameters.from_preset('ring')
            run=ep.run_method(sc,method,p,**kw)
            size=run['maps'].shape[0];scale=run['gauge']['scale'];shift=run['gauge']['shift']
            if method=='TMTM':
                anchors=[np.rint((r['pixel_x']-shift)/scale*(size-1)/span).astype(int) for r in run['rows']]
            else:
                anchors=[np.asarray(d['anchors'],int)[[d['ordering'].index(leaf) for leaf in ids]]
                         for d,ids in zip(run['records']['discrete'],sc['ids'])]
            if scale<0:anchors=[size-1-a for a in anchors]
            output[method]=measure(sc,run['maps'],anchors)
            output[method]['nominal_topology_failed_frames']=sum(r['nominal_topology_failed'] for r in run['checks'])
        ext=reference_points_from_frames(sc['frames'],sc['ids'],kind='extremum')
        rows=solve_sequence(sc['centers'],sc['areas'],sc['hier'],p,reference_axis=0,
                            feature_ids=sc['tracks'],reference_points=ext)
        matrix,skeletons,_=rh.render(sc,rows,p,ds['nominal'])
        anchors=[np.asarray(s.anchors)[[s.ordering.index(leaf) for leaf in ids]] for s,ids in zip(skeletons,sc['ids'])]
        output['fixed-X anchored']=measure(sc,matrix,anchors)
        output['source_sha256']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
              for f in [Path(__file__),ROOT/'experiments/era5.py',ROOT/'src/rgmtm/baselines/space_filling.py',ROOT/f'results/replicate_{name}.json']}
        saved[name]=output;path.write_text(json.dumps(saved,indent=2)+'\n')
        print('Saved',name,{m:round(100*v['max_share'],3) for m,v in output.items() if m!='source_sha256'},flush=True)

if __name__=='__main__':main()
