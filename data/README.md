# Public input data

`data/real` is a local symbolic link to the shared public-data cache at
`/Users/lele/Desktop/MergeTreeMaps/data/real`. It is excluded from the
supplement because the cache is about 13 GB.

The final evaluation expects these files:

| Relative path | SHA-256 |
|---|---|
| `ERA5_MSLP/ERA5_MSLP_19991117_20000114_12h_arco_expanded.nc` | `77d91ddeb8d61c839065ef20e7290a53c5d77bab5782b7a08dfb62f7c7eadb2f` |
| `ERA5_MSLP/ERA5_MSLP_20131201_20140131_12h_arco_expanded.nc` | `72445bfb47c1a5980ff991b881c3a77ebf9031996bf99dced03d9c884c65df09` |
| `wildfire/wildfire.json` | `2a8dd31bf6d222d7de673c7e7b2af94550660f1996b0a5db256d97f2b9c2ed9f` |

The ERA5 subsets come from the public ARCO-ERA5 mirror. The wildfire input is
from Franke et al., Zenodo record 11234747. The manuscript documents the exact
extraction and preprocessing protocol.
# Geographic figure overlay

The figure scripts use Natural Earth 1:110m coastlines from the public-domain
Natural Earth vector dataset. The GeoJSON is stored at
`geo/ne_110m_coastline.geojson` and is bundled as a small figure dependency.
Source: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_coastline.geojson
SHA-256: `851f581ff5ffb844deed8ae1a9ce22e3c4bb3d74fa342cadb5d8e39b41ae7c3c`.
`tools/fetch_coastline.py` downloads and validates the line geometry; this overlay
does not participate in scalar-field extraction, layout, or evaluation.


## Revised main-paper inputs (2026-10-12)

Only ERA5 1999/2000 is active. OLR uses NOAA's Ver01Rev02 snapshot,
2024-06-01--2024-07-30, 15 S--20 N / 60--150 E, with join-tree extrema.
Download with `python3 tools/fetch_public_scalar.py olr` (full-source fallback
about 3.9 GB). Source: https://doi.org/10.7289/V5SJ1HH2.
The five-cell buffered 49×49 grid requires finite values; no new imputation is
performed. The predeclared smoothing ladder selects the first scale meeting
the eight-extremum limit independently of performance. The chosen scale is
500 km. Metadata, hashes and preprocessing changes are saved in the protocol.
OISST is retired and not required to reproduce the current main experiments.

## China PM2.5 and seasonal controls

The current main PM2.5 sequence is January 1–30, 2000 (30 daily fields), over
102–114 E / 28–38 N. Source: the integrated China PM2.5/elevation/meteorology
dataset V2, DOI [10.57760/sciencedb.35623](https://doi.org/10.57760/sciencedb.35623).
Files carry 10:30 timestamps without an explicit averaging interval. Upstream
linear-then-nearest filling is preserved and disclosed; no new imputation is added.
The 49×49 buffered equal-area grid and 100 km smoothing follow the frozen protocol.

```sh
python3 tools/prepare_cn_pm25.py --source-dir ../data/real/CN-Reanalysis/2000
PYTHONPATH=src python3 tools/run_paper_suite.py --datasets pm25
```

`results/protocol_pm25.json` records source-file hashes, the processed grid and
preprocessing changes. January has 5/30 hierarchy-conflict frames and 7 clear
k=2 motion events. R (κ=20%) and Morton tie at 28.6% total motion error;
ST-MTM/A/Hilbert are at 42.9%. The main suite totals six datasets / 342 frames.

January was selected for the main display after a four-month seasonal audit.
January, April, July and October each use 30 consecutive days, the same domain
and a common 100 km scale chosen from extrema counts before evaluation. All
four runs and original January–February records remain available; this selection
does not establish universal superiority. Raw PM2.5 files are excluded from Git
and supplementary source packages.

```sh
PYTHONPATH=src python3 tools/run_pm25_seasons.py
python3 tools/audit_method_performance.py
```

Older acquisition/configuration notes are retained in
`../notes/experiment-documentation-history.md`.
