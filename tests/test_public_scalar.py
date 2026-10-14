"""Independent public-input contract checks using small local NetCDF fixtures."""
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
import numpy as np
from netCDF4 import Dataset,date2num
from datetime import datetime,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analysis'))
import public_scalar as ps
from dataset_suite import PAPER_DATASETS,REAL_DATASETS

class PublicInputContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  (ps.ROOT/"tmp").mkdir(parents=True,exist_ok=True)

 def fixture(self,path,*,missing_day=False,units='degC'):
  with Dataset(path,'w') as d:
   for k,n in [('time',60),('lat',2),('lon',2)]:d.createDimension(k,n)
   for k,v in [('lat',[30,25]),('lon',[161,160])]:d.createVariable(k,'f8',(k,))[:]=v
   t=d.createVariable('time','f8',('time',));t.units='days since 2024-06-01'
   t[:]=np.arange(60)+(np.arange(60)>=30 if missing_day else 0)
   f=d.createVariable('sst','f4',('time','lat','lon'),fill_value=-9999);f.units=units
   f[:]=np.broadcast_to([[1,2],[3,4]],(60,2,2))
 def test_membership_has_one_era5_and_no_retired_ocean_input(self):
  self.assertNotIn('oisst',PAPER_DATASETS)
  self.assertEqual(sum(n.startswith('era5') for n in PAPER_DATASETS),1)
  self.assertEqual(set(REAL_DATASETS),{'era5','wildfire','olr','pm25'})
 def test_descending_coordinates_are_sorted_with_values(self):
  with tempfile.TemporaryDirectory(dir=ps.ROOT/"tmp") as tmp:
   path=Path(tmp)/'fixture.nc';self.fixture(path)
   with patch.object(ps,'path_for',return_value=path):
    lat,lon,f,dates,meta=ps.read_source('oisst')
   np.testing.assert_array_equal(lat,[25,30]);np.testing.assert_array_equal(lon,[160,161])
   np.testing.assert_array_equal(f[0],[[4,3],[2,1]])
   self.assertEqual(len(dates),60);self.assertEqual(len(meta['sha256']),64)
 def test_missing_day_and_wrong_units_are_rejected(self):
  with tempfile.TemporaryDirectory(dir=ps.ROOT/"tmp") as tmp:
   path=Path(tmp)/'fixture.nc'
   for opts in ({'missing_day':True},{'units':'K'}):
    self.fixture(path,**opts)
    with patch.object(ps,'path_for',return_value=path),self.assertRaises(ValueError):ps.read_source('oisst')

if __name__=='__main__':unittest.main()
