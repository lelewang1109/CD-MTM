"""Reproducible degree stress test for the display-resolution positional DP.

Hold leaf count, reference positions, widths, and pixels fixed; only the root
degree changes. This isolates the subset-DP cost caused by hierarchy flattening.
Run: PYTHONPATH=src python3 analysis/benchmark_degree.py
"""
from pathlib import Path
import json
import platform
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theory as th
from cdmtm.error_budget import Parameters


def binary(items):
    if len(items) == 1:
        return items[0]
    k = len(items) // 2
    return [binary(items[:k]), binary(items[k:])]


def root_degree_tree(n, degree):
    # Flatten only root-adjacent binary nodes. Consecutive cases are therefore
    # nested relaxations of one tree, not unrelated partitions of the leaves.
    children = binary(list(range(n)))
    while len(children) < degree:
        i = next(i for i, child in enumerate(children) if isinstance(child, list))
        children = children[:i] + children[i] + children[i + 1:]
    return children


def main():
    n, pixels = 12, 96
    rng = np.random.default_rng(2027)
    q = rng.uniform(2, pixels - 2, n)
    w = np.ones(n)
    p = Parameters(canvas=float(pixels), canvas_origin=0., width_scale=1.,
                   gap=.25, rho=.5, extra_budget=0.)
    rows = []
    for degree in (2, 3, 4, 6, 8, 12):
        tree = root_degree_tree(n, degree)
        start = time.perf_counter()
        tau = th.dp_tau(w, q, tree, p, pixels, tol=.25)
        seconds = time.perf_counter() - start
        rows.append(dict(leaves=n, pixels=pixels, root_degree=degree,
                         subset_states=(1 << degree) - 1, tau=tau, seconds=seconds))
        print(f"degree={degree:2d} states={(1 << degree) - 1:5d} "
              f"tau={tau:.2f} time={seconds:.3f}s", flush=True)
    assert all(a['tau'] >= b['tau'] - .01 for a, b in zip(rows, rows[1:]))
    output = Path(__file__).resolve().parent / 'output' / 'benchmark_degree.json'
    output.write_text(json.dumps(dict(protocol='same widths/q/pixels; root arity varied',
                                      platform=platform.platform(), python=sys.version.split()[0],
                                      numpy=np.__version__, rows=rows), indent=2) + '\n')


if __name__ == '__main__':
    main()
