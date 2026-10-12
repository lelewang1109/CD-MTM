"""Check certificate semantics independently using a small conflicting hierarchy."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from result_tables import position_metrics
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from update_paper_evidence import proxy


class PositionTableTests(unittest.TestCase):
    def test_hierarchy_lower_bound_and_relaxed_order(self):
        q = np.array([0., 2., 1.])
        r = position_metrics({'kept': [np.array([0., 1., 2.])],
                              'sorted': [np.array([0., 2., 1.])]},
                             [q], [((0, 1), 2)], 2.)
        self.assertAlmostEqual(r['bound_mean'], .25)
        self.assertAlmostEqual(r['methods']['kept']['mean'], .25)
        self.assertEqual(r['methods']['sorted']['mean'], 0.)

    def test_incomplete_or_duplicate_evidence_is_rejected(self):
        with self.assertRaises(ValueError):
            proxy({'dataset': 'fixture', 'proxy': []}, 'A')
        row = {'method': 'A', 'k': 2, 'eps': .02, 'clear': 0}
        self.assertEqual(proxy({'proxy': [row]}, 'A')['clear'], 0)
        with self.assertRaises(ValueError):
            proxy({'proxy': [row, row]}, 'A')

    def test_scaling_and_invalid_frames(self):
        r = position_metrics({'a': [np.array([0., 1.])]},
                             [np.array([2., 0.])], [(0, 1)], 4.)
        self.assertEqual(r['methods']['a']['mean'], .25)
        with self.assertRaises(ValueError):
            position_metrics({'a': []}, [np.array([0.])], [0], 1.)
        with self.assertRaises(ValueError):
            position_metrics({}, [], [], 0.)

if __name__ == '__main__':
    unittest.main()
