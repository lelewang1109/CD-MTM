"""Buffered, value-preserving extraction of NOAA and user-provided scalar-field sequences.

No metric-dependent preprocessing: choose the smallest fixed sigma for which
all frames fit the declared exhaustive-order limit. The entire ladder and
preprocessing differences are recorded; no silent feature cancellation.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from netCDF4 import Dataset, num2date
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
import era5_expanded as ee
from experiments import era5 as ep

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
 'pm25': dict(variable='PM2.5',units='ug m-3',kind='split',window=dict(lon=(102.,114.),lat=(28.,38.)),start='2000-01-01',end='2000-01-30',source_page='https://doi.org/10.57760/sciencedb.35623'),
 'oisst': dict(variable='sst', units='degC', kind='split', window=dict(lon=(160.,210.),lat=(25.,45.)),
               source_page='https://www.ncei.noaa.gov/products/optimum-interpolation-sst',
               remote='noaa.oisst.v2.highres/sst.day.mean.2024.nc',
               start='2024-06-01', end='2024-07-30', download=dict(west=150,east=220,south=15,north=50)),
 'olr': dict(variable='olr', units='W m-2', kind='join', window=dict(lon=(60.,150.),lat=(-15.,20.)),
             source_page='https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC00875',
             remote='olr_cdr_day/olr.day.mean.v2.nc',
             start='2024-06-01', end='2024-07-30', download=dict(west=45,east=165,south=-25,north=30)),
}
SIGMAS_KM = (100.,150.,200.,250.,350.,500.,700.,1000.)
GRID = 49
BUFFER = 5
MAX_LEAVES = 8

def path_for(name):
 spec=SPECS[name]
 return ROOT/'data/public_scalar'/f"{name}_{spec['start'].replace('-','')}_{spec['end'].replace('-','')}.nc"
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def read_source(name):
 spec=SPECS[name];path=path_for(name)
 if not path.exists():
  command='python3 tools/prepare_cn_pm25.py' if spec['variable']=='PM2.5' else f'python3 tools/fetch_public_scalar.py {name}'
  raise FileNotFoundError(f'{path}; run {command}')
 with Dataset(path) as d:
  lat=np.asarray(d['lat'][:],float);lon=np.asarray(d['lon'][:],float)
  tv=d['time'];dates=[str(t)[:10] for t in num2date(tv[:],tv.units)]
  f=np.ma.asarray(d[spec['variable']][:],dtype=float).filled(np.nan)
  if f.ndim==4 and f.shape[1]==1:f=f[:,0]
  if f.ndim!=3 or f.shape!=(len(dates),len(lat),len(lon)):raise ValueError('Unexpected scalar dimensions')
  # Extra source cells may include land; the buffered interpolation domain must be finite.
  if not np.isfinite(f).any():raise ValueError('All source values missing')
  if dates[0]!=spec['start'] or dates[-1]!=spec['end'] or len(dates)!=int((np.datetime64(spec['end'])-np.datetime64(spec['start']))/np.timedelta64(1,'D'))+1:raise ValueError('Expected every daily frame in the declared period')
  days=np.array(dates,dtype='datetime64[D]')
  if not np.all(np.diff(days)==np.timedelta64(1,'D')):raise ValueError('Non-contiguous time axis')
  iy=np.argsort(lat);ix=np.argsort(lon);lat=lat[iy];lon=lon[ix];f=f[:,iy][:,:,ix]
  attrs={k:str(d.getncattr(k)) for k in d.ncattrs()}
  units=str(d[spec['variable']].units)
  if name=='oisst' and units.lower() not in ('degc','degree_celsius','degrees_c','celsius','degree_c','degrees_celsius'):raise ValueError(f'Unexpected SST units: {units}')
  if spec['variable']=='PM2.5' and units.replace('µ','u').replace('μ','u') not in ('ug/m3','ug m-3'):raise ValueError(f'Unexpected PM2.5 units: {units}')
  if name=='olr' and 'w' not in units.lower():raise ValueError(f'Unexpected OLR units: {units}')
 if spec['variable']=='PM2.5':
  source_manifest=json.loads(path.with_suffix('.json').read_text())
  if source_manifest['subset_sha256']!=digest(path):raise ValueError('PM2.5 subset hash mismatch; regenerate from source')
  attrs['source_file_sha256']=json.dumps({x['file']:x['sha256'] for x in source_manifest['source_files']})
 return lat,lon,f,dates,dict(sha256=digest(path),source_units=units,source_attributes=attrs,
                            path=str(path.relative_to(ROOT)),source_page=spec['source_page'])

def prepare_fields(name, grid=GRID, max_leaves=MAX_LEAVES):
 spec=SPECS[name];lat,lon,raw,dates,meta=read_source(name)
 phi=np.deg2rad(np.mean(spec['window']['lat']));co=np.cos(phi);R=6371.
 bx=R*co*np.deg2rad(spec['window']['lon']);by=R*np.sin(np.deg2rad(spec['window']['lat']))/co
 dx=np.diff(bx)[0]/grid;dy=np.diff(by)[0]/grid;b=BUFFER
 X,Y=np.meshgrid(bx[0]+(np.arange(-b,grid+b)+.5)*dx,by[0]+(np.arange(-b,grid+b)+.5)*dy)
 pts=np.c_[np.rad2deg(np.arcsin(Y.ravel()*co/R)),np.rad2deg(X.ravel()/R/co)]
 big=np.array([RegularGridInterpolator((lat,lon),f,bounds_error=True)(pts).reshape(X.shape) for f in raw])
 if not np.isfinite(big).all():raise ValueError(f'{name}: buffered domain intersects missing/land cells; no imputation')
 sign=1 if spec['kind']=='join' else -1
 trials=[]
 for sigma in ((spec['fixed_sigma_km'],) if 'fixed_sigma_km' in spec else SIGMAS_KM):
  smooth=gaussian_filter(sign*big,(0,sigma/dy,sigma/dx),mode='reflect')
  markers=[ee.strict_minima(f)[b:b+grid,b:b+grid] for f in smooth]
  counts=[int(m.sum()) for m in markers]
  trials.append(dict(sigma_km=sigma,leaves_min=min(counts),leaves_max=max(counts)))
  if max(counts)<=max_leaves:break
 else:raise ValueError(f'No fixed smoothing scale meets leaf limit {max_leaves}: {trials}')
 fields=[];stats=[];plain=[]
 # Scale epsilon to the data range: below rendered and reported precision.
 eps=max(float(np.ptp(smooth))*1e-8,1e-10)
 for t,(f,m) in enumerate(zip(smooth,markers)):
  w=f[b:b+grid,b:b+grid].copy();fallback=not m.any()
  if fallback:
   m=m.copy();m[np.unravel_index(np.argmin(w),w.shape)]=True
  # Shared priority flood uses a module epsilon; restore it after each call.
  previous=ee.EPS
  try:
   ee.EPS=eps;g=ee.impose_minima(w,m)
  finally:ee.EPS=previous
  fields.append(sign*g);plain.append(sign*w)
  stats.append(dict(t=t,retained_extrema=int(m.sum()),fallback_global_extremum=fallback,
                    max_imposition=float((g-w).max()),mean_imposition=float((g-w).mean())))
 scale=120/float(np.hypot(np.diff(bx)[0],np.diff(by)[0]))
 x=X[b:b+grid,b:b+grid];y=Y[b:b+grid,b:b+grid]
 coords=np.c_[(x.ravel()-bx[0])*scale,(y.ravel()-by[0])*scale];area=dx*dy*scale**2
 protocol=dict(name=name,variable=spec['variable'],kind=spec['kind'],units=spec['units'],dates=[dates[0],dates[-1]],
   frames=len(dates),step_days=1,window=spec['window'],grid=grid,buffer_cells=b,sigma_km=sigma,
   sigma_ladder_km=list(SIGMAS_KM),sigma_trials=trials,exhaustive_leaf_limit=max_leaves,
   smoothing_selection=('shared seasonal sigma fixed before performance evaluation' if 'fixed_sigma_km' in spec else 'smallest common sigma meeting the predeclared leaf limit; no evaluation metric used'),
   projection='spherical Lambert cylindrical equal-area',standard_parallel_degrees=float(np.rad2deg(phi)),
   cell_area_layout=area,cell_area_km2=dx*dy,priority_flood_epsilon=eps,
   boundary_policy='keep interior extrema of buffered field; impose them in cropped field; fallback logged',
   feature_interpretation='extrema of processed scalar field; not independently validated objects',
   preprocessing=stats,**meta)
 return np.array(fields),coords,area,np.array(plain),dates,protocol

def load(name):
 fields,coords,area,plain,dates,protocol=prepare_fields(name)
 sc=ep.scene_from_fields(fields,coords,area,SPECS[name]['kind'],max_leaves=MAX_LEAVES)
 assert all(len(ids)==p['retained_extrema'] for ids,p in zip(sc['ids'],protocol['preprocessing']))
 sc.update(dates=dates,fields_smooth=plain,protocol=protocol)
 out=ROOT/'results';out.mkdir(exist_ok=True)
 (out/f'protocol_{name}.json').write_text(json.dumps(protocol,indent=2))
 return dict(name=name,sc=sc,lo=coords.min(0),hi=coords.max(0),domain_area=GRID**2*area,
             nominal=4096,cmap='RdBu_r',vrange=None,native_span=120.,meta=protocol)

def oisst():return load('oisst')
def olr():return load('olr')
def pm25():return load('pm25')
