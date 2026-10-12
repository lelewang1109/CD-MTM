"""Prepare the fixed Jan--Feb 2000 PM2.5 subset from user-provided CN-Reanalysis.

No new missing-value imputation. Preserve the upstream fill metadata and
per-file SHA-256 values; the scalar timestamps must match the daily filenames.
"""
from pathlib import Path
import sys,argparse,json
import numpy as np
from netCDF4 import Dataset,num2date,date2num
from datetime import datetime,timedelta
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'))
import public_scalar as ps

def prepare(source,name='pm25'):
 spec=ps.SPECS[name]
 start=datetime.fromisoformat(spec['start']);end=datetime.fromisoformat(spec['end'])
 dates=[start+timedelta(days=t) for t in range((end-start).days+1)]
 fields=[];records=[];lat0=lon0=None;attrs0=None
 for day in dates:
  path=source/(day.strftime('%Y%m%d')+'.nc')
  if not path.exists():raise FileNotFoundError(path)
  with Dataset(path) as d:
   lat=np.array(d['lat'][:]);lon=np.array(d['lon'][:]);v=d['PM2.5']
   units=str(v.units).replace('µ','u').replace('μ','u')
   if units not in ('ug/m3','ug m-3'):raise ValueError(f'Unexpected PM2.5 units: {units}')
   if v.dimensions!=('lat','lon'):raise ValueError('Expected a 2-D PM2.5 field')
   tv=d['time'];stamp=num2date(tv[...],tv.units,calendar=getattr(tv,'calendar','standard'))
   if str(stamp)[:10]!=day.strftime('%Y-%m-%d') or str(stamp)[11:19]!='10:30:00':raise ValueError(f'Unexpected timestamp: {stamp}')
   iy=np.flatnonzero((lat>=24)&(lat<=42));ix=np.flatnonzero((lon>=98)&(lon<=118))
   a=np.ma.asarray(v[iy,ix],dtype=float).filled(np.nan)
   attrs={k:str(v.getncattr(k)) for k in v.ncattrs() if k!='_FillValue'}
   if lat0 is None:lat0=lat[iy];lon0=lon[ix];attrs0=attrs
   if not np.array_equal(lat0,lat[iy]) or not np.array_equal(lon0,lon[ix]) or attrs!=attrs0:raise ValueError('Source grids or variable metadata change across dates')
   if np.nanmin(a)<0:raise ValueError('Negative concentration')
   fields.append(a);records.append(dict(file=path.name,time=str(stamp),sha256=ps.digest(path),global_attributes={k:str(d.getncattr(k)) for k in d.ncattrs()}))
 out=ps.path_for(name);out.parent.mkdir(parents=True,exist_ok=True)
 with Dataset(out,'w') as d:
  for k,n in [('time',len(dates)),('lat',len(lat0)),('lon',len(lon0))]:d.createDimension(k,n)
  for k,a in [('lat',lat0),('lon',lon0)]:d.createVariable(k,'f8',(k,))[:]=a
  t=d.createVariable('time','f8',('time',));t.units='days since '+spec['start']+' 10:30:00';t.calendar='proleptic_gregorian';t[:]=np.arange(len(dates))
  v=d.createVariable('PM2.5','f8',('time','lat','lon'),zlib=True,fill_value=np.nan);v[:]=np.array(fields)
  for k,x in attrs0.items():v.setncattr(k,x)
  d.description='Subset of user-provided merged CN-Reanalysis; upstream PM2.5 filling retained.'
  d.source_collection='CN-Reanalysis/2000';d.source_doi='10.57760/sciencedb.35623';d.source_dataset_version='V2'
  d.source_citation_status='User identifies local files as the DOI-linked V2 integrated dataset; per-file hashes identify this local snapshot'
  d.upstream_fill_method=attrs0.get('fill_method','not specified')
  d.temporal_interpretation='One field per file at 10:30; averaging interval not established by metadata'
 manifest=dict(source_doi='10.57760/sciencedb.35623',source_dataset_version='V2',collection='CN-Reanalysis/2000',variable='PM2.5',source_files=records,subset_sha256=ps.digest(out),subset=str(out.relative_to(ROOT)),variable_attributes=attrs0,
  protocol=f"{spec['start']}--{spec['end']}; window 102--114 E, 28--38 N; fixed before evaluation; no added imputation")
 out.with_suffix('.json').write_text(json.dumps(manifest,indent=2))
 print(out)
 return manifest

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-dir',type=Path,default=ROOT.parent/'data/real/CN-Reanalysis/2000');a=p.parse_args();prepare(a.source_dir)
if __name__=='__main__':main()
