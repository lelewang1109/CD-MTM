"""Native raster costs must be measured rather than inferred from method names."""
from pathlib import Path
from types import SimpleNamespace
import sys,unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
from native_merge_errors import measure

class Frame:
    def __init__(self,sign):self.values=sign*np.array([0.,1.,5.])
    def lca(self,a,b):return 2

class NativeMergeTests(unittest.TestCase):
    def test_changed_barrier_is_detected_for_join_and_split(self):
        for kind,sign in [('join',1),('split',-1)]:
            sc=dict(trees=[SimpleNamespace(kind=kind)],frames=[Frame(sign)],ids=[[0,1]],
                    fields=sign*np.array([[[0.,5.,1.]]]))
            exact=measure(sc,sign*np.array([[0.],[5.],[1.]]),[np.array([0,2])])
            bad=measure(sc,sign*np.array([[0.],[7.],[1.]]),[np.array([0,2])])
            self.assertEqual(exact['max_share'],0.)
            self.assertAlmostEqual(bad['max_share'],.4)
            self.assertAlmostEqual(bad['mean_share'],.4)

if __name__=='__main__':unittest.main()
