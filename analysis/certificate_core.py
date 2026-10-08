"""Small, dependency-light primitives for the paper's continuous certificates.

Unlike the historical prototype's hill climb, free_tau returns a proved optimum
over all orders (up to floating-point arithmetic), or explicitly refuses an
enumeration that exceeds its resource limit. It never silently returns a
heuristic as an exact certificate.
"""
from functools import lru_cache
from itertools import islice, permutations
from math import factorial

import numpy as np


class EnumerationLimit(RuntimeError):
    """The requested exact computation exceeds its declared order budget."""


def order_tau(orders, widths, references, origin, canvas, gap, rho):
    """Fixed-order closed form, vectorized in O(batch * n) space and time."""
    orders = np.asarray(orders, dtype=int)
    if orders.ndim == 1:
        orders = orders[None, :]
    w = np.asarray(widths, dtype=float)[orders]
    q = np.asarray(references, dtype=float)[orders]
    if not w.shape[1]:
        raise ValueError('A layout must have at least one leaf.')
    n = w.shape[1]
    h = rho * w / 2
    left = np.cumsum(w, axis=1) - w / 2 + gap * np.arange(n)
    right = w.sum(axis=1, keepdims=True) - np.cumsum(w, axis=1) + w / 2 + gap * np.arange(n - 1, -1, -1)
    result = np.maximum.reduce([
        np.zeros(len(orders)),
        (origin + left - q - h).max(axis=1),
        (q - h - origin - canvas + right).max(axis=1),
    ])
    if n > 1:
        prefix = np.maximum.accumulate(q - left - h, axis=1)
        pair = (prefix[:, :-1] + left[:, 1:] - q[:, 1:] - h[:, 1:]) / 2
        result = np.maximum(result, pair.max(axis=1))
    result[w.sum(axis=1) + (n - 1) * gap > canvas + 1e-12] = np.inf
    return result


def free_tau(widths, references, p, *, max_orders=50_000_000):
    """Exact continuous free optimum, with a sound order-independent shortcut.

    The per-leaf canvas constraints give a lower bound. If the reference-sorted
    order attains it, it proves optimality without enumerating. Otherwise every
    permutation is inspected in bounded-memory chunks. Cache keys include all
    model inputs; no dataset-name or frame-index caches can become stale.
    """
    return _free_tau_cached(tuple(map(float, widths)), tuple(map(float, references)),
                            float(p.canvas_origin), float(p.canvas), float(p.gap),
                            float(p.rho), int(max_orders))


@lru_cache(maxsize=8192)
def _free_tau_cached(widths, references, origin, canvas, gap, rho, max_orders):
    w, q = np.asarray(widths), np.asarray(references)
    if len(w) != len(q) or not len(w):
        raise ValueError('Non-empty widths and references must have equal length.')
    if np.any(w < 0) or gap < 0 or not 0 <= rho <= 1 or canvas <= 0:
        raise ValueError('Invalid layout geometry.')
    if not np.isfinite(w).all() or not np.isfinite(q).all():
        raise ValueError('Layout inputs must be finite.')
    if w.sum() + (len(w) - 1) * gap > canvas + 1e-12:
        return float('inf'), True
    h = rho * w / 2
    lower = max(0., float(np.max(origin + w / 2 - q - h)),
                float(np.max(q - h - origin - canvas + w / 2)))
    best = float(order_tau(np.argsort(q, kind='stable'), w, q, origin, canvas, gap, rho)[0])
    # Exact equality is deliberate: an epsilon-based shortcut could falsely
    # certify a merely close feasible upper bound.
    if best <= lower:
        return best, True
    count = factorial(len(w))
    if count > max_orders:
        raise EnumerationLimit(f'{len(w)} leaves require {count} orders; limit is {max_orders}.')
    it = permutations(range(len(w)))
    while True:
        chunk = list(islice(it, 20_000))
        if not chunk:
            break
        best = min(best, float(order_tau(chunk, w, q, origin, canvas, gap, rho).min()))
        if best <= lower:
            break
    return best, True


def prune_to_initial_score(nodes, score, gaps, tolerance):
    """Keep the total score increase within tolerance of the initial flattening.

    The initial benchmark is fixed: repeated removals cannot accumulate one
    tolerance allowance each. score is the rounded display-model DP optimum.
    """
    kept = list(nodes)
    initial = score(kept)
    for node in sorted(kept, key=lambda v: -gaps[v]):
        candidate = [v for v in kept if v != node]
        if score(candidate) <= initial + tolerance:
            kept = candidate
    return kept


def distance_change_error_bound(error_i_t, error_j_t, error_i_s, error_j_s):
    """Sufficient error bound for a pair's *projected* distance change."""
    return sum(abs(x) for x in (error_i_t, error_j_t, error_i_s, error_j_s))
