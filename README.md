# CD-MTM: Certificate-Driven Merge Tree Maps

**Making Position–Topology Trade-offs Explicit** — a restructured research draft
for the PacificVis 2027 Conference Paper Track.

CD-MTM diagnoses how far feature anchors must move when a merge-tree hierarchy
is kept, and measures the scalar merge-level cost of optional relaxation. It
preserves the selected extrema and their values. The contribution is a quantified
trade-off, with mixed geometric motion-proxy benefits across datasets.

## Start here

- New manuscript and supplement: [`paper/pacificvis2027-restructured/`](paper/pacificvis2027-restructured/README.md).
- Read the current [main paper](paper/pacificvis2027-restructured/main.pdf) and [supplement](paper/pacificvis2027-restructured/supplement.pdf).
- Experiment code and commands: [`experiments/publication2027/`](experiments/publication2027/README.md).
- Clean-checkout reproduction: [`experiments/publication2027/REPRODUCING.md`](experiments/publication2027/REPRODUCING.md).
- Organized results and provenance: [`results/publication2027/`](results/publication2027/README.md).
- Research and writing audit in Chinese: [`notes/research-restructure-20261013.md`](notes/research-restructure-20261013.md).
- Raw-data acquisition/preparation: [`data/README.md`](data/README.md).

The earlier manuscript remains in `paper/pacificvis2027/` for traceability.
The new paper has modular prose and separately generated tables; rebuilding
scientific evidence does not replace its text.

## Main experiments

| Dataset | Frames | Tree | Purpose |
|---|---:|---|---|
| ERA5 pressure, 1999/2000 | 118 | Join | Atmospheric minima and illustrated conflict |
| Australian fire, 2019 | 30 | Split | More complex feature configurations |
| NOAA OLR, June–July 2024 | 60 | Join | Additional domain and no motion-proxy benefit case |
| China PM2.5, January 2000 | 30 | Split | Selected, sparse descriptive case |
| Ring | 40 | Split | Synthetic expanding geometry |
| Gaussians | 64 | Split | Synthetic hierarchy/position control |

Membership is defined in `analysis/dataset_suite.py`: six sequences / 342 frames.
The 2013/14 ERA5 period and OISST are excluded from main aggregates. Four PM2.5
months are a separate exploratory selection audit. Gaussian motion error is
undefined at the default setting because no clear events occur.

The main methods are TMTM, a reimplementation of ST-MTM, native Hilbert and Morton,
packed reference sorting, and tree-preserving/relaxed CD-MTM. Native curves retain
all processed samples and do not receive optimal filling. This rendering-policy
difference is explicit in the paper. Fixed-X and exact projection are controls.

## Reproduce

Use Python 3.10+ and the pinned dependencies:

```sh
python -m pip install -e .
PYTHONPATH=src python -m unittest discover -s tests -v
# Recompute five critical numerical stages on all six prepared sequences:
PYTHONPATH=src python experiments/publication2027/run.py
# Regenerate tables, quantitative figures, organized records and provenance:
PYTHONPATH=src python experiments/publication2027/build.py
# Verify source/figure hashes and numerical manuscript claims:
PYTHONPATH=src python experiments/publication2027/validate.py
```

There are 25 scientific/contract tests. Full numerical runs require prepared raw
inputs; saved records suffice to regenerate publication tables and figures.
The runner writes timestamped status manifests and logs. Exact-frontier,
sensitivity, scalability, and transfer records retained from prior runs are
identified separately. See the experiment README for the explicit ten-stage run.

The organized export includes a 42-row unrounded comparison CSV, a claim ledger,
source/snapshot hashes, and separate `main`, `sensitivity`, `validation`, `transfer`,
and `protocols` folders. No original result files or raw observations are removed.

## Reading the results

Full interval certificates, width-free calibrated order error, and achieved anchor
displacement measure different feasible sets. Scalar-cost means do not bound the
worst frame, and the relaxation eligibility threshold is not an error guarantee.
The motion proxy assumes known identities and is not a participant study. Improved
reference alignment may worsen two-dimensional stress or provide no proxy benefit.

The retained [visualization gallery](results/visualizations/README.md) provides
additional spatial/tree views, six-method temporal maps, fragmentation, and
geometric diagnostics. The new publication figures have PDF, PNG, and SVG exports.
The source reference papers are held locally under `references/`; their text and
figures are not redistributed in the new source bundle.

## Implementation

`src/cdmtm/` contains the certificate, interval layout, rendering, and baseline
implementations. `analysis/` contains shared preprocessing, exact frontiers,
filling, motion evaluation, and controls. `experiments/publication2027/` supplies
publication orchestration. `results/` retains original computation evidence;
`results/publication2027/` is the organized active snapshot. `paper/` contains
editable LaTeX sources and generated PDFs. `notes/` preserves the research audit
and earlier documentation history.
