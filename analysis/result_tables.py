"""Reproducible, compact paper results; no method or dataset selection by score."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis'))
import evaluation as ev
import replicate as rp
from pointcert import tau_pt
from rgmtm.error_budget import leaf_orders
from dataset_suite import PAPER_DATASETS

METHODS = [('TMTM', 'TMTM'), ('ST-MTM', 'ST-MTM'), ('Hilbert', 'Hilbert'),
           ('Morton', 'Morton'), ('fixed-X anchored', 'Fixed-X'),
           ('q-sort (packed)', 'Packed sort'), ('A', 'RG-MTM-P (ours)'),
           ('R 20%', r'RG-MTM-R (ours), $\kappa=20\%$'), ('oracle q', 'Exact projection')]


def position_metrics(positions, references, hierarchies, extent):
    """Mean framewise minimax order error, normalized by the reference extent.

    This permits any monotone calibration and removes widths/gaps; it is an
    optimistic order-only error, not the displacement of the rendered pixels.
    """
    if extent <= 0 or not (len(references) == len(hierarchies)):
        raise ValueError('Invalid reference extent or frame counts')
    bound = [float(tau_pt(leaf_orders(h), q).min()) / extent
             for h, q in zip(hierarchies, references)]
    out = {}
    for method, frames in positions.items():
        if len(frames) != len(references):
            raise ValueError('Inconsistent method frame count')
        values = []
        for u, q in zip(frames, references):
            if len(u) != len(q) or not np.isfinite(u).all():
                raise ValueError('Invalid method anchors')
            values.append(float(tau_pt([np.argsort(u, kind='stable')], q)[0]) / extent)
        out[method] = {'mean': float(np.mean(values)), 'max': max(values), 'per_frame': values}
    return {'bound_mean': float(np.mean(bound)), 'bound_max': max(bound),
            'bound_per_frame': bound, 'methods': out}


def main():
    path = ROOT / 'results/final_performance.json'
    result = json.loads(path.read_text()) if path.exists() else {}
    for name in (sys.argv[1:] or PAPER_DATASETS):
        print('Computing final position results:', name, flush=True)
        ds = rp.LOADERS[name]()
        maps, _, reference, _, _, _ = ev.methods(ds)
        result[name] = position_metrics({k: v['u'] for k, v in maps.items()},
            reference['qs'], ds['sc']['hier'], reference['extent'])
        result[name]['frames'] = len(ds['sc']['frames'])
        result[name]['reference_extent'] = reference['extent']
        result[name]['definition'] = 'temporal mean of framewise order-only minimax monotone-calibration error / reference-axis extent'
        result[name]['source_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [ROOT/'analysis/evaluation.py', ROOT/'analysis/misreading.py',
                      ROOT/'analysis/result_tables.py', ROOT/f'results/replicate_{name}.json']}
        path.write_text(json.dumps(result, indent=2) + '\n')
        print('Saved', name, flush=True)

if __name__ == '__main__':
    main()
