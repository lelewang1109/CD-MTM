"""Fetch the Natural Earth 1:110m coastline expected by the figure scripts."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_coastline.geojson'
DEST = ROOT / 'data/geo/ne_110m_coastline.geojson'
with urlopen(URL, timeout=30) as response:
    raw = response.read()
data = json.loads(raw)
assert data['type'] == 'FeatureCollection' and len(data['features']) > 0
assert all(f['geometry']['type'] in ('LineString', 'MultiLineString') for f in data['features'])
DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_bytes(raw)
print(DEST, len(data['features']), 'features; sha256', sha256(raw).hexdigest())
