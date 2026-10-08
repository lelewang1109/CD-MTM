"""Pair-level merge errors for the ERA5 step-48 case in the paper.

Run: PYTHONPATH=src python3 -W ignore analysis/topological_case.py
The optimal barrier filling is evaluated analytically; output values are hPa.
"""
from itertools import combinations
from pathlib import Path
import json

import numpy as np

import attainable as at
import relax_hierarchy as rh
import replicate as rp


def main():
    ds = rp.LOADERS['era5']()
    sc = ds['sc']
    frame, cap = 48, .2
    run = rh.run(ds, cap, make_figure=False, return_internal=True)
    order = np.asarray(run['_internal']['results']['R_relaxed']['_rows'][frame]['order'], int)
    fr, ids = sc['frames'][frame], sc['ids'][frame]
    values = at.lca_matrix(fr, ids, 'join')
    n = len(order)
    delta = float(at.Filling(n).delta(order[None], values)[0])
    barriers = np.array([min(values[order[i], order[j]] for i in range(k + 1)
                             for j in range(k + 1, n)) for k in range(n - 1)]) + delta
    leaves = np.diag(values)[order]
    barriers = np.maximum(barriers, np.maximum(leaves[:-1], leaves[1:]))
    pairs = []
    for i, j in combinations(range(n), 2):
        a, b = int(order[i]), int(order[j])
        true = float(values[a, b])
        shown = float(max(barriers[i:j]))
        pairs.append(dict(leaf_ranks=[a, b], leaf_values_hPa=[float(values[a, a]), float(values[b, b])],
                          true_merge_hPa=true, displayed_merge_hPa=shown, error_hPa=shown - true))
    pairs.sort(key=lambda row: -abs(row['error_hPa']))
    result = dict(dataset='era5', frame=frame, merge_gap_cap_fraction=cap,
                  full_sequence_runtime_seconds=run['seconds'], order=order.tolist(),
                  optimal_filling_delta_hPa=delta, pairs=pairs)
    out = Path(__file__).resolve().parent / 'output' / 'topological_case_step48.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print('maximum pair error:', pairs[0])


if __name__ == '__main__':
    main()
