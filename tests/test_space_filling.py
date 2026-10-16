"""Independent geometry, value preservation, and barrier semantics checks."""
import unittest
import numpy as np
from rgmtm.baselines.space_filling import sample_order,linearize,inverse_order,merge_levels_on_line
class SpaceFillingContract(unittest.TestCase):
 def test_morton_known_quadrant_order(self):
  np.testing.assert_array_equal(sample_order((4,4),'Morton'),[0,1,4,5,2,3,6,7,8,9,12,13,10,11,14,15])
 def test_hilbert_known_order_and_adjacent_power_two_cells(self):
  np.testing.assert_array_equal(sample_order((4,4),'Hilbert'),[0,1,5,4,8,12,13,9,10,14,15,11,7,6,2,3])
  for side in [2,4,8,16]:
   o=sample_order((side,side),'Hilbert');x=o%side;y=o//side
   np.testing.assert_array_equal(abs(np.diff(x))+abs(np.diff(y)),np.ones(len(o)-1))
 def test_rectangular_and_nonpower_grids_preserve_all_samples(self):
  for shape in [(1,1),(3,5),(49,49),(14,14)]:
   f=np.arange(2*np.prod(shape)).reshape((2,*shape))
   for curve in ['Hilbert','Morton']:
    line=linearize(f,curve);inv=inverse_order(shape,curve)
    np.testing.assert_array_equal(line[inv].T.reshape(f.shape),f)
 def test_true_barriers_use_all_intermediate_samples(self):
  values=np.array([0,5,1,7,2]);anchors=[0,2,4]
  j=merge_levels_on_line(values,anchors,'join')
  self.assertEqual(j[0,1],5);self.assertEqual(j[0,2],7)
  s=merge_levels_on_line(-values,anchors,'split');np.testing.assert_array_equal(s,-j)
if __name__=='__main__':unittest.main()
