"""Reproduce compared maps once; cache numeric arrays with input/source hashes.

Caches are regenerable, excluded from Git, and loaded without pickle. Shared
rendering is also used by the existing new-dataset and SFC figure entry points.
"""
from hashlib import sha256
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'results/visualization_cache'


def fingerprint(dataset, sources=None):
    sc = dataset['sc']; h = sha256()
    for key in ('fields', 'coords'):
        a = np.ascontiguousarray(sc[key])
        h.update(str((a.shape, a.dtype.str)).encode()); h.update(a.tobytes())
    h.update(json.dumps(sc['tracks'], default=lambda x: int(x), sort_keys=True).encode())
    h.update(json.dumps({k: dataset[k] for k in ('name', 'native_span', 'nominal', 'domain_area')},
                        default=lambda x: float(x), sort_keys=True).encode())
    for key in ('lo', 'hi'):
        if key in dataset:
            h.update(np.ascontiguousarray(dataset[key]).tobytes())
    if sources is None:
        sources = sorted(p for directory in ('analysis', 'src', 'experiments')
                         for p in (ROOT / directory).rglob('*.py')
                         if 'panels' not in p.parts and not p.stem.startswith('fig_')
                         and ('visualization' not in p.parts or p.name == 'rendering.py'))
    for path in sources:
        h.update(str(path).encode()); h.update(Path(path).read_bytes())
    return h.hexdigest()


def render_reference_maps(dataset):
    """A keeps the tree; R uses κ=20% and the paper's optimal barrier filling."""
    import relax_hierarchy as rh
    import filling as fl
    result = rh.run(dataset, .2, make_figure=False, return_internal=True)['_internal']
    sc = dataset['sc']; output = {}
    for name, key in (('A', 'A_full_hierarchy'), ('R 20%', 'R_relaxed')):
        rows = result['results'][key]['_rows']
        matrix, skeletons, _ = rh.render(sc, rows, result['p'], dataset['nominal'])
        matrix = matrix.astype(float).copy()
        if name == 'R 20%':
            for t, (frame, skeleton) in enumerate(zip(sc['frames'], skeletons)):
                matrix[:, t], _ = fl.optimal_fill(matrix[:, t], list(skeleton.ordering),
                                                skeleton.anchors, frame, sc['trees'][0].kind)
        output[name] = matrix
    return output


def temporal_maps(dataset, refresh=False):
    """Six actual sample/render matrices; each method retains its native length."""
    from experiments import era5 as ep
    import general_method as gm
    from rgmtm.baselines import space_filling as sfc
    token = fingerprint(dataset); CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f'{dataset["name"]}-{token}.npz'
    if path.exists() and not refresh:
        with np.load(path, allow_pickle=False) as saved:
            return {key: saved[key] for key in saved.files}
    sc = dataset['sc']; span = dataset['native_span']
    params = gm.Parameters(canvas=span, canvas_origin=float(min(dataset['lo'][0], 0.)),
        width_scale=.5 * span / dataset['domain_area'], gap=span / 240,
        extra_budget=span / 120, rho=.5)
    output = {}
    for method in ('TMTM', 'ST-MTM'):
        kwargs = dict(canvas=span, length=dataset['nominal'], refine_raster=False, strict_checks=False)
        if dataset['name'] == 'ring':
            kwargs['stmtm_parameters'] = ep.b2.LayoutParameters.from_preset('ring')
        output[method] = ep.run_method(sc, method, params, **kwargs)['maps']
    output.update(render_reference_maps(dataset))
    for curve in ('Hilbert', 'Morton'):
        output[curve] = sfc.linearize(sc['fields'], curve)
    for key, value in output.items():
        if value.ndim != 2 or value.shape[1] != len(sc['fields']) or not np.isfinite(value).all():
            raise ValueError(f'Invalid rendered map: {key}')
    np.savez_compressed(path, **output)
    return output
