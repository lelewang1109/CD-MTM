import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from evaluation import windows


class ProjectionProxyTests(unittest.TestCase):
    def test_orthogonal_motion_separates_projected_and_two_dimensional_truth(self):
        sc = {'tracks': [['a', 'b'], ['a', 'b']]}
        ext = [np.array([[0., 0.], [2., 10.]]), np.array([[0., 0.], [3., 0.]])]
        qs = [np.array([0., 2.]), np.array([0., 3.])]
        two_d = windows(sc, ext, qs, 3., 1, .02, 20., qs, .1)
        projected = windows(sc, ext, qs, 3., 1, .02, 20., qs, .1,
                            truth_mode='projected', axis_extent=10.)
        self.assertEqual(two_d['truth'].tolist(), [-1])
        self.assertEqual(projected['truth'].tolist(), [1])
        self.assertEqual(two_d['rev'].tolist(), [True])
        self.assertEqual(projected['correct'].tolist(), [True])


if __name__ == '__main__':
    unittest.main()
