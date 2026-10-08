"""Certificate-only ERA5 sensitivity at fixed 150-km smoothing.

This preprocessing is independent of the <=11-leaf enumeration regime used
for full layouts/frontiers. It reports a rigorous lower bound on hierarchy
cost without claiming to solve the full method at the larger leaf counts.
Run: PYTHONPATH=src python3 -W ignore analysis/independent_scale.py
"""
from pathlib import Path
from math import factorial
import json
import time

import numpy as np

import certificate_core as cc
import era5_expanded as ee
import general_method as gm
import relax_hierarchy as rh
import theory as th
from cdmtm.reference_points import reference_points_from_frames


def evaluate(season):
    ds = ee.loader(season, f'era5_{season}_150km', sigma=150., max_leaves=None)
    sc = ds['sc']
    ext = reference_points_from_frames(sc['frames'], sc['ids'], kind='extremum')
    ref = gm.auto_reference(sc, ext, ds['lo'], ds['hi'])
    p = gm.universal_parameters(ref['origin'], ref['extent'], ds['domain_area'])
    theta = gm.THETA_FRACTION * p.canvas
    leaves, bounds, seconds = [], [], []
    for t, (frame, ids) in enumerate(zip(sc['frames'], sc['ids'])):
        w = p.width_scale * np.asarray(sc['areas'][t])
        q = np.asarray(ref['qs'][t])
        start = time.perf_counter()
        lower = th.tau_lower(w, q, th.to_tree(rh.node_tree(frame, ids)), p, 1024)
        seconds.append(time.perf_counter() - start)
        sorted_upper = float(cc.order_tau(np.argsort(q, kind='stable'), w, q,
                                          p.canvas_origin, p.canvas, p.gap, p.rho)[0])
        leaves.append(len(ids))
        bounds.append(max(0., lower - sorted_upper) / p.canvas)
    return dict(season=season, sigma_km=150, frames=len(leaves), leaves_max=max(leaves),
                leaves_mean=float(np.mean(leaves)), frames_above_free_enumeration_limit=sum(factorial(n) > 50_000_000 for n in leaves),
                certified_hierarchy_conflict_frames=sum(x > .02 for x in bounds),
                certified_hierarchy_conflict_share=float(np.mean(np.asarray(bounds) > .02)),
                hierarchy_cost_lower_max_share=float(max(bounds)),
                certificate_seconds_total=float(sum(seconds)), certificate_seconds_max=float(max(seconds)),
                resolution_pixels=1024,
                interpretation='Lower bound only: tau_hier >= relaxed DP bound and tau_free <= fixed q-sort tau.')


def main():
    result = {season: evaluate(season) for season in ('1999', '2014')}
    out = Path(__file__).resolve().parent / 'output' / 'independent_scale.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    for row in result.values():
        print(row, flush=True)


if __name__ == '__main__':
    main()
