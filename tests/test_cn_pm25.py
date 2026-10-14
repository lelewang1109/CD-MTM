"""Validate the local-source contract independently of the scientific pipeline."""
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
import numpy as np
from netCDF4 import Dataset
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import prepare_cn_pm25 as cn

class LocalPM25Contract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  (cn.ROOT/"tmp").mkdir(parents=True,exist_ok=True)

 def file(self,path,t,units='µg/m3',hour='10:30:00'):
  with Dataset(path,'w') as d:
   for k in ['lat','lon']:d.createDimension(k,2)
   for k,a in [('lat',[35,30]),('lon',[110,105])]:d.createVariable(k,'f8',(k,))[:]=a
   tv=d.createVariable('time','f8',());tv.units='days since 2000-01-01 '+hour;tv.assignValue(t)
   v=d.createVariable('PM2.5','f8',('lat','lon'),fill_value=np.nan);v.units=units
   v.fill_method='griddata_linear_then_nearest';v[:]=[[1,np.nan],[3,4]]
 def test_preserves_values_missing_cells_and_upstream_metadata(self):
  from datetime import datetime,timedelta
  with tempfile.TemporaryDirectory(dir=cn.ROOT/"tmp") as tmp:
   root=Path(tmp);source=root/'raw';source.mkdir();out=root/'subset.nc'
   for t in range(60):self.file(source/((datetime(2000,1,1)+timedelta(days=t)).strftime('%Y%m%d')+'.nc'),t)
   with patch.dict(cn.ps.SPECS,{'pm25_fixture60':dict(cn.ps.SPECS['pm25'],end='2000-02-29')}),patch.object(cn.ps,'path_for',return_value=out):m=cn.prepare(source,'pm25_fixture60')
   self.assertEqual(len(m['source_files']),60);self.assertEqual(m['subset_sha256'],cn.ps.digest(out))
   with Dataset(out) as d:
    self.assertEqual(d.upstream_fill_method,'griddata_linear_then_nearest')
    self.assertTrue(np.ma.is_masked(d['PM2.5'][0,0,1]))
    self.assertEqual(d['PM2.5'][0,1,1],4)
 def test_thirty_day_control_preserves_declared_period(self):
  from datetime import datetime,timedelta
  with tempfile.TemporaryDirectory(dir=cn.ROOT/"tmp") as tmp:
   root=Path(tmp);source=root/'raw';source.mkdir();out=root/'subset.nc'
   for t in range(30):self.file(source/((datetime(2000,1,1)+timedelta(days=t)).strftime('%Y%m%d')+'.nc'),t)
   spec=dict(cn.ps.SPECS['pm25'],start='2000-01-01',end='2000-01-30')
   with patch.dict(cn.ps.SPECS,{'pm25_trial':spec}),patch.object(cn.ps,'path_for',return_value=out):
    m=cn.prepare(source,'pm25_trial');lat,lon,f,dates,meta=cn.ps.read_source('pm25_trial')
   self.assertEqual(len(dates),30);self.assertEqual(dates[-1],'2000-01-30')
   self.assertEqual(len(m['source_files']),30)
 def test_rejects_wrong_units_and_nonmatching_timestamp(self):
  with tempfile.TemporaryDirectory(dir=cn.ROOT/"tmp") as tmp:
   root=Path(tmp)
   for opts in ({'units':'kg/kg'},{'hour':'00:00:00'}):
    self.file(root/'20000101.nc',0,**opts)
    with self.assertRaises(ValueError):cn.prepare(root)
 def test_missing_required_file_is_an_error(self):
  with tempfile.TemporaryDirectory(dir=cn.ROOT/"tmp") as tmp:
   with self.assertRaises(FileNotFoundError):cn.prepare(Path(tmp))
if __name__=='__main__':unittest.main()
