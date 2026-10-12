"""Exploratory seasonal controls, kept outside the main suite and its aggregates."""
from pathlib import Path
import json
from functools import partial
import public_scalar as ps
PERIODS={'pm25_jan':('2000-01-01','2000-01-30'),
         'pm25_apr':('2000-04-01','2000-04-30'),
         'pm25_jul':('2000-07-01','2000-07-30'),
         'pm25_oct':('2000-10-01','2000-10-30')}
PLAN=ps.ROOT/'results/pm25_season_protocol.json'
def register(fixed=True):
 plan=json.loads(PLAN.read_text()) if fixed and PLAN.exists() else {}
 for name,(start,end) in PERIODS.items():
  ps.SPECS[name]=dict(ps.SPECS['pm25'],start=start,end=end)
  if 'shared_sigma_km' in plan:ps.SPECS[name]['fixed_sigma_km']=plan['shared_sigma_km']
 import replicate as rp
 rp.LOADERS.update({n:partial(ps.load,n) for n in PERIODS})
