# CD-MTM: Certificate-Driven Merge Tree Maps

Code, experiment records and figures for **CD-MTM: Diagnosing and Exploring
Position–Topology Trade-offs in Merge Tree Maps**, prepared for PacificVis 2027.
The method diagnoses positional conflict imposed by hierarchy, optionally
relaxes merge relations, and reports the achieved position–topology trade-off.

## Datasets and comparison methods

| Dataset | Main period | Frames | Tree |
|---|---|---:|---|
| ERA5 pressure | 1999-11-17–2000-01-14 | 118 | join |
| Australian wildfire | November–December 2019 | 30 | split |
| NOAA OLR | 2024-06-01–2024-07-30 | 60 | join |
| China PM2.5 | 2000-01-01–2000-01-30 | 30 | split |
| Ring | synthetic | 40 | split |
| Gaussians | synthetic | 64 | split |

The active suite contains **six sequences / 342 frames**, defined once in
[`analysis/dataset_suite.py`](analysis/dataset_suite.py). OISST and ERA5 2013/14
are excluded from main aggregates and default runs. PM2.5 uses the integrated
China dataset V2, DOI [10.57760/sciencedb.35623](https://doi.org/10.57760/sciencedb.35623).
Its January display was selected after seasonal comparison; all four seasonal
runs and the original January–February records remain available. Seven clear
January events support a descriptive case, not general superiority.

The main visual comparison includes **TMTM, ST-MTM, A, R (κ=20%), Hilbert and
Morton**. Hilbert/Morton traverse every processed grid sample in a fixed canonical
orientation and preserve its value. They receive no optimal refilling. R uses
optimal barrier filling; additional caps, fixed directions and packed sorting
remain in the saved evaluation. The baseline implementations and source caveats
are recorded in [`notes/january-pm25-and-sfc-baselines.md`](notes/january-pm25-and-sfc-baselines.md).

## Visualization gallery

[Browse all 10 figures and captions](results/visualizations/README.md) ·
[Combined PDF booklet](results/visualizations/visualization-gallery.pdf) ·
[Figure-generation architecture](analysis/visualization/README.md)

The gallery covers spatial fields and trees, six-method temporal maps, native
curve fragmentation, motion-error components, measured topology–motion trade-offs,
neighbourhood preservation, and time-window sensitivity. Each figure has a PNG,
PDF and SVG export. Undefined rates remain undefined; scalar images use a common
color scale within each dataset. Editable SVG axes and labels accompany raster
scalar matrices.

![PM2.5 six-method temporal comparison](results/visualizations/pm25_temporal_methods.png)

![Motion-error comparison](results/visualizations/motion_error_comparison.png)

## Reproduce

Use Python 3.10 or newer and install the pinned dependencies:

```sh
python3 -m pip install -e .
PYTHONPATH=src python3 -m unittest discover -s tests -v
# Quantitative figures require saved JSON only:
PYTHONPATH=src python3 tools/build_visualization_gallery.py --metrics-only --out tmp/gallery-metrics
# Full default gallery uses locally prepared OLR and PM2.5 inputs:
PYTHONPATH=src python3 tools/build_visualization_gallery.py
```

There are 21 independent tests, including native sample preservation, actual
barrier semantics, no-event handling and cache invalidation. Numeric visualization
caches are generated from input/source hashes, excluded from Git and loaded
without pickle.

Raw inputs are excluded from Git. Acquisition and upstream preprocessing are
explained in [`data/README.md`](data/README.md). Prepare the new real sequences with:

```sh
python3 tools/fetch_public_scalar.py olr
python3 tools/prepare_cn_pm25.py --source-dir ../data/real/CN-Reanalysis/2000
PYTHONPATH=src python3 tools/run_paper_suite.py --datasets olr pm25
```

The shared eight-stage runner covers replication, evaluation, exact frontiers,
filling, robustness, point certificates, persistence and witnesses. Running it
without `--datasets` selects all six main sequences. To refresh the manuscript's
computed tables and reproducible supplement:

```sh
python3 tools/audit_method_performance.py
PYTHONPATH=src python3 tools/update_paper_evidence.py
python3 tools/build_supplement.py
```

The [review manuscript](paper/pacificvis2027/review-preview.pdf) has nine body
pages and two reference pages. [Paper source instructions](paper/pacificvis2027/README.md)
explain compilation. The visualization booklet remains a separate supplementary
artifact, so the main paper's page allocation stays intact.

## Structure

| Path | Purpose |
|---|---|
| `src/cdmtm/` | Certificate, layout, rendering and baseline implementations |
| `analysis/` | Shared dataset protocol, evaluation, exact frontier and robustness |
| `analysis/visualization/` | Method catalogue, numeric rendering cache and figure families |
| `tools/` | Experiment, gallery and supplement entry points |
| `results/` | Evidence JSON, provenance manifests and exported figures |
| `paper/` | Manuscript, proofs and publication figures |
| `tests/` | Independent scientific and reproducibility checks |

Historical documentation is preserved in
[`notes/experiment-documentation-history.md`](notes/experiment-documentation-history.md).

### Consolidated manuscript results

The manuscript now uses two main tables: certificate-calibrated order deviation
and 2-D distance stress / motion proxy error, both across six datasets and all
main comparison methods. Native curve fragmentation and merge costs are
supplementary diagnostics. Reproduce with:

```sh
PYTHONPATH=src python3 analysis/result_tables.py
PYTHONPATH=src python3 tools/update_paper_evidence.py
```

`results/final_performance.csv` is the flat, unrounded export behind both tables;
`results/final_performance.json` stores per-frame positional results and provenance.
Retired dataset exports and obsolete duplicate bundles were removed; the PM2.5
seasonal selection audit and raw inputs are retained.
