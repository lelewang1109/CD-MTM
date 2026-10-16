# RG-MTM: Reference-Guided Merge Tree Maps

**Making Position–Topology Trade-offs Explicit** — a restructured research draft
for the PacificVis 2027 Conference Paper Track.

RG-MTM diagnoses how far feature anchors must move when a merge-tree hierarchy
is kept, and measures the scalar merge-level cost of optional relaxation. It
preserves the selected extrema and their values. The contribution is a quantified
trade-off, with mixed geometric motion-proxy benefits across datasets.

## Start here

- 当前论文与附录：[无图正文](paper/pacificvis2027-no-figures/main.pdf)、[配套附录](paper/pacificvis2027-no-figures/supplement.pdf)。
- RG-MTM 实验图片：[统一图片索引](results/figures/README.md)（PNG / SVG，含生成脚本及来源哈希）。
- 最新有图版源码：[`paper/pacificvis2027-content-draft/`](paper/pacificvis2027-content-draft/README.md)。
- 当前优化主线（无图版）源码：[`paper/pacificvis2027-no-figures/`](paper/pacificvis2027-no-figures/)。
- Experiment code and commands: [`experiments/publication2027/`](experiments/publication2027/README.md).
- Scientific reproduction: [`experiments/publication2027/REPRODUCING.md`](experiments/publication2027/REPRODUCING.md).
- Organized results and provenance: [`results/publication2027/`](results/publication2027/README.md).
- Raw-data acquisition/preparation: [`data/README.md`](data/README.md).

`paper/pacificvis2027/` 与 `paper/pacificvis2027-restructured/` 仅保留既有实验脚本和哈希清单依赖的图表资产。旧正文、旧附录、旧编译输出和旧源码包已归档。实验复现文档内旧论文编译段及 `experiments/publication2027/package.py` 面向已归档的旧排版，不作为当前论文打包入口；当前论文编译见工作区论文说明。数值实验和图表重建入口保留。

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
packed reference sorting, and RG-MTM-P / RG-MTM-R. Native curves retain
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

`src/rgmtm/` contains the certificate, interval layout, rendering, and baseline
implementations. `analysis/` contains shared preprocessing, exact frontiers,
filling, motion evaluation, and controls. `experiments/publication2027/` supplies
publication orchestration. `results/` retains original computation evidence;
`results/publication2027/` is the organized active snapshot. `paper/` contains
editable LaTeX sources and generated PDFs. `notes/` preserves the research audit
and earlier documentation history.

## Naming and repository migration

The repository is **RG-MTM** and the installable distribution is `rg-mtm`. Import the core implementation from `rgmtm`, including `rgmtm.reference_guided`. Preserving and relaxed modes are **RG-MTM-P** and **RG-MTM-R**. Historical records keep the keys `A` and `R 20%`; `src/rgmtm/names.py` defines the display mapping.

```sh
git clone https://github.com/lelewang1109/RG-MTM.git
cd RG-MTM
python -m pip install -e .
PYTHONPATH=src python tools/build_rgmtm_figures.py
PYTHONPATH=src python tools/verify_rgmtm_migration.py
```

The current figure set is generated in `results/figures/rgmtm_*`. Original numeric files, arrays, and historical paper images remain unchanged. `provenance/rgmtm_rename_20261016.json` records exact reversible source edits; validators distinguish historical source hashes from a new numerical run. The separate RA-MTM project retains its own name and Git repository.
