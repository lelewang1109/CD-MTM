"""Independent optimization checks for the paper's scientific guarantees."""
import itertools
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from certificate_core import (EnumerationLimit, distance_change_error_bound,
                              free_tau, order_tau, prune_to_initial_score)
import theory


def independent_lp(order, w, q, p):
    """Variables are centers z, anchors u, and tau; do not reuse paper code."""
    n = len(w)
    A, b = [], []
    for i in range(n):
        for sign in (-1, 1):
            row = np.zeros(2 * n + 1); row[i] = sign; row[n + i] = -sign
            A.append(row); b.append(p.rho * w[i] / 2)
            row = np.zeros(2 * n + 1); row[n + i] = sign; row[-1] = -1
            A.append(row); b.append(sign * q[i])
    for i, j in zip(order[:-1], order[1:]):
        row = np.zeros(2 * n + 1); row[i] = 1; row[j] = -1
        A.append(row); b.append(-(w[i] + w[j]) / 2 - p.gap)
    bounds = [(p.canvas_origin + x / 2, p.canvas_origin + p.canvas - x / 2) for x in w]
    bounds += [(None, None)] * n + [(0, None)]
    result = linprog(np.r_[np.zeros(2 * n), 1.], A_ub=A, b_ub=b, bounds=bounds, method='highs')
    return result.fun if result.success else np.inf


class PaperCertificates(unittest.TestCase):
    def test_fixed_and_free_match_independent_linear_programs(self):
        rng = np.random.default_rng(20260929)
        for _ in range(12):
            n = 4; w = rng.uniform(.02, .15, n); q = rng.uniform(-.1, 1.1, n)
            p = SimpleNamespace(canvas_origin=0., canvas=1., gap=.01, rho=float(rng.uniform()))
            orders = list(itertools.permutations(range(n)))
            exact = np.array([independent_lp(o, w, q, p) for o in orders])
            cf = order_tau(orders, w, q, 0., 1., .01, p.rho)
            np.testing.assert_allclose(cf, exact, atol=1e-9)
            value, certified = free_tau(w, q, p)
            self.assertTrue(certified)
            self.assertAlmostEqual(value, float(exact.min()), places=9)

    def test_no_silent_heuristic_above_resource_limit(self):
        p = SimpleNamespace(canvas_origin=0., canvas=1., gap=.01, rho=0.)
        with self.assertRaises(EnumerationLimit):
            free_tau(np.full(7, .1), np.full(7, .5), p, max_orders=1)

    def test_sorted_shortcut_is_certified_even_for_large_inputs(self):
        p = SimpleNamespace(canvas_origin=0., canvas=100., gap=0., rho=0.)
        value, certified = free_tau(np.ones(100), np.arange(100) + .5, p, max_orders=1)
        self.assertEqual(value, 0.)
        self.assertTrue(certified)

    def test_relaxed_grid_bound_never_exceeds_continuous_optimum(self):
        rng = np.random.default_rng(71)
        orders = [(0, 1, 2), (1, 0, 2), (2, 0, 1), (2, 1, 0)]
        for _ in range(25):
            w = rng.uniform(.02, .15, 3); q = rng.uniform(-.1, 1.1, 3)
            p = SimpleNamespace(canvas_origin=0., canvas=1., gap=.017, rho=.5)
            optimum = min(independent_lp(o, w, q, p) for o in orders)
            self.assertLessEqual(theory.tau_lower(w, q, ((0, 1), 2), p, 128), optimum + 1e-8)

    def test_pruning_uses_one_total_tolerance(self):
        # Each removal costs .4; a moving baseline would allow all removals.
        score = lambda kept: .4 * (3 - len(kept))
        kept = prune_to_initial_score([0, 1, 2], score, {0: 3, 1: 2, 2: 1}, .5)
        self.assertEqual(kept, [1, 2])
        self.assertLessEqual(score(kept), .5)

    def test_projected_motion_margin(self):
        rng = np.random.default_rng(72)
        for _ in range(100):
            q = rng.normal(size=4); e = rng.normal(size=4); u = q + e
            truth = abs(q[2] - q[3]) - abs(q[0] - q[1])
            reading = abs(u[2] - u[3]) - abs(u[0] - u[1])
            bound = distance_change_error_bound(*e)
            self.assertLessEqual(abs(reading - truth), bound + 1e-12)
            if abs(reading) > bound:
                self.assertEqual(np.sign(reading), np.sign(truth))


if __name__ == '__main__':
    unittest.main()
