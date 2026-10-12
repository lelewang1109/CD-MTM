"""Download NOAA subsets and record source URLs and content hashes.

Prefer NCSS subsets. A throttled NCSS can be replaced by the same NOAA annual
file, cached locally and subset identically. Publication inputs are immutable.
"""
from pathlib import Path
import sys,json,urllib.request,urllib.parse,time,shutil
import numpy as np
from netCDF4 import Dataset,num2date
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'analysis'),str(ROOT/'src')]
import public_scalar as ps

def download(url,path):
 tmp=path.with_suffix(path.suffix+'.part');path.parent.mkdir(parents=True,exist_ok=True)
 try:
  with urllib.request.urlopen(url,timeout=45) as r,tmp.open('wb') as f:
   shutil.copyfileobj(r,f,1024*1024)
  with Dataset(tmp) as d:assert d.variables
  tmp.replace(path)
 finally:
  if tmp.exists():tmp.unlink()

def annual_subset(name,source,out):
 spec=ps.SPECS[name];bounds=spec['download']
 with Dataset(source) as d,Dataset(out,'w') as o:
  lat=np.asarray(d['lat'][:]);lon=np.asarray(d['lon'][:]);tv=d['time']
  dates=np.array([str(x)[:10] for x in num2date(tv[:],tv.units)])
  ti=np.where((dates>=spec['start'])&(dates<=spec['end']))[0]
  yi=np.where((lat>=bounds['south'])&(lat<=bounds['north']))[0];xi=np.where((lon>=bounds['west'])&(lon<=bounds['east']))[0]
  if not len(ti) or not len(yi) or not len(xi):raise ValueError('Empty requested subset')
  o.setncatts({k:d.getncattr(k) for k in d.ncattrs()})
  for key,idx in [('time',ti),('lat',yi),('lon',xi)]:
   o.createDimension(key,len(idx));v=o.createVariable(key,'f8',(key,));src=d[key]
   v.setncatts({k:src.getncattr(k) for k in src.ncattrs() if k!='_FillValue'});v[:]=src[idx]
  src=d[spec['variable']];v=o.createVariable(spec['variable'],'f4',('time','lat','lon'),zlib=True)
  v.setncatts({k:src.getncattr(k) for k in src.ncattrs() if k not in ('_FillValue','scale_factor','add_offset','missing_value')})
  for k,t in enumerate(ti):
   f=np.ma.asarray(src[int(t)])
   if f.ndim==3 and f.shape[0]==1:f=f[0]
   v[k]=f[np.ix_(yi,xi)]

def fetch(name):
 spec=ps.SPECS[name];out=ps.path_for(name);manifest=out.with_suffix('.json')
 if out.exists():
  ps.read_source(name)
  if not manifest.exists():
   manifest.write_text(json.dumps(dict(name=name,url='https://downloads.psl.noaa.gov/Datasets/'+spec['remote'],transport='annual-file subset',sha256=ps.digest(out),spec=spec),indent=2))
  record=json.loads(manifest.read_text());record['spec']=spec;manifest.write_text(json.dumps(record,indent=2))
  print(name,'verified cache',ps.digest(out),flush=True);return
 query=dict(var=spec['variable'],**spec['download'],horizStride=1,time_start=spec['start']+'T00:00:00Z',
             time_end=spec['end']+'T23:59:59Z',timeStride=1,accept='netcdf4')
 url='https://psl.noaa.gov/thredds/ncss/grid/Datasets/'+spec['remote']+'?'+urllib.parse.urlencode(query)
 try:
  print(name,'requesting NCSS subset',flush=True);download(url,out);transport='NCSS'
 except Exception as e:
  print(name,'NCSS unavailable:',str(e),'using annual source',flush=True)
  url='https://downloads.psl.noaa.gov/Datasets/'+spec['remote']
  raw=out.parent/'raw'/Path(spec['remote']).name
  if not raw.exists():download(url,raw)
  annual_subset(name,raw,out);transport='annual-file subset'
 ps.read_source(name)
 manifest.write_text(json.dumps(dict(name=name,url=url,transport=transport,sha256=ps.digest(out),spec=spec),indent=2))
 print(name,'downloaded and validated',out,flush=True)

if __name__=='__main__':
 for n in sys.argv[1:] or ['olr']:
  if n not in ('oisst','olr'):raise SystemExit('NOAA downloader supports oisst/olr only; PM2.5 uses tools/prepare_cn_pm25.py')
  fetch(n)
