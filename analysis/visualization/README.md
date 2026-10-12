# Scientific visualization package

One entry point builds a gallery of OLR/PM2.5 fields, tree structure, six-method
temporal maps and native-curve fragmentation, followed by quantitative charts
for all six evaluated datasets:

```sh
PYTHONPATH=src python3 tools/build_visualization_gallery.py
# Charts from saved JSON only; raw inputs are unnecessary:
PYTHONPATH=src python3 tools/build_visualization_gallery.py --metrics-only --out tmp/gallery-metrics
```

Responsibilities:

- `catalog.py`: method names/colors, exact motion-setting lookup and undefined rates.
- `rendering.py`: actual TMTM/ST-MTM/A/R/Hilbert/Morton scalar matrices and numeric caching.
- `spatial.py`: processed fields, source leaf supports, compressed merge trees and fragmentation.
- `metrics.py`: saved-record motion, topology, neighbourhood and sensitivity comparisons.
- `gallery.py`: export, gallery documentation and provenance manifest.

The existing `fig_new_datasets.py` and `fig_sfc_comparison.py` reuse the same
renderer and have guarded entry points, so importing them does not create figures.
PNG, PDF and SVG exports share common per-dataset scalar scales. Heatmap heights
are normalized separately: a native sample rank is not a geographical coordinate.
No existing screenshot or rasterized paper figure is read as a drawing input.

The default qualitative datasets are OLR and PM2.5. `--datasets` can select other
active sequences; the quantitative charts always cover all six. Spatial snapshots
use first/middle/last times. Fragmentation examples use the first frame with the
largest extremum count, a structural illustration rule independent of error scores.

Numeric caches under `results/visualization_cache/` are excluded from Git and
the supplement. Their hashes include processed values, coordinates, tracking,
geometry settings and analysis/solver sources (drawing-only code does not invalidate numeric maps). Caches use NPZ with pickle disabled.
`manifest.json` records the evidence JSON hash, dataset fingerprints, drawing
source hashes and exported file hashes.

The main PM2.5 January display was selected after seasonal evaluation; its seven
clear events are descriptive. No-event rates are undefined, not zero. Sparse
events, different window-specific event sets, fitted projection and native versus
optimally filled maps are disclosed in the gallery captions. Bar heights alone
do not establish statistical superiority.

The combined `visualization-gallery.pdf` contains one page per figure. The
manifest also hashes this booklet; its captions and method caveats appear in
the gallery README alongside each individually downloadable figure.
