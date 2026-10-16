# PacificVis 2027 publication experiment suite

This is the preferred entry point for the restructured conference manuscript.
It reuses the scientific implementations under `src/rgmtm/` and `analysis/`;
its purpose is reproducible orchestration, evidence checks, and publication exports.
Run commands from the RG-MTM root using Python 3.10+ with the pinned dependencies.

```sh
python -m pip install -e .
PYTHONPATH=src python -m unittest discover -s tests -v
# Five numerical stages for all six sequences; requires prepared raw inputs.
PYTHONPATH=src python experiments/publication2027/run.py
# Full ten-stage scientific chain (longer; exact frontiers can be expensive).
PYTHONPATH=src python experiments/publication2027/run.py --stages replicate evaluation attainable filling robustness pointcert persistence witness_stats result_tables native_merge_errors
# Tables, figures and organized snapshots from result files.
PYTHONPATH=src python experiments/publication2027/build.py
```

The default stages are `evaluation`, `filling`, `pointcert`, `result_tables`, and
`native_merge_errors`. This revision runs all five for ERA5, wildfire, OLR,
PM2.5 January, Ring, and Gaussians. Older replication, exact-frontier, sensitivity,
and scalability computations are retained evidence, not described as new runs.
To select a sequence or stages use `--datasets era5 olr --stages evaluation filling`.

| Scientific role | Entry point | Source evidence |
|---|---|---|
| RQ1: unavoidable displacement | `analysis/replicate.py`, `pointcert.py` | `replicate_*.json`, `pointcert.json` |
| RQ2: alignment and scalar cost | `evaluation.py`, `result_tables.py`, `native_merge_errors.py` | `final_performance.json`, `native_merge_errors.json`, `eval_projection.json` |
| Exact attainable frontiers | `attainable.py` | `attainable_*.json` |
| Optimal filling validation | `filling.py` | `filling.json` |
| RQ3: geometric motion proxy | `evaluation.py` | default k=2, epsilon=2% rows in `eval_projection.json` |
| Direction / extraction / persistence | `robustness.py`, `sensitivity.py`, `persistence.py` | separately retained sensitivity records |
| Seasonal selection audit | `tools/run_pm25_seasons.py` | January, April, July, October records |
| Diagnosis scalability / transfer | `generality.py`, `benchmark_degree.py` | retained benchmark and transfer records |

`run.py` records unique timestamped runs, logs, exit codes, source hashes, and
completion status. A failed run stops and remains labelled failed. It does not
silently fabricate missing data. Shared aggregate files are updated sequentially.
Do not run two writers against the same result directory concurrently.

`build.py` rejects stale positional/native evidence and mismatched frame counts.
It creates `results/publication2027/evidence/{main,sensitivity,validation,transfer,protocols}`,
a 42-row unrounded main comparison CSV, a claim ledger, and a manifest. Main
aggregate snapshots filter out retired datasets. Original records remain intact.
Figures and supplementary tables have independent generators and editable SVGs.

The latest manuscript and matching supplement PDFs are in `publications/`; editable sources, historical drafts, and writing notes remain local. Historical experimental figures/tables are in `results/legacy_publication/`. The public code/results package excludes manuscript directories.

Raw observations are excluded from the source bundle. See `data/README.md` for
acquisition, required local data, source hashes, and preprocessing. The bundle can
regenerate figures/tables from saved results; full numerical reruns additionally
require those prepared data. ST-MTM is a reimplementation of the supplied preprint,
not the authors' executable, and our processed datasets differ from its originals.

## Layout revision (2026-10-14)

`layout_figures.py` draws five updated main-paper figures from numerical evidence.
Default execution uses verified bundled render arrays and needs no raw observations.
Use `PYTHONPATH=src python experiments/publication2027/layout_figures.py --prepare`
to recompute ERA5/OLR columns and refresh those arrays. The new images share scalar
scales within each dataset and use the same interval geometry for A/R. Paired
confidence intervals come from saved moving-block-bootstrap records. OLR's case
frame is the first maximum-H frame, selected independently of motion-proxy outcome.
CSV values, selection rules, source hashes and array hashes are in `figure_data/`.
The manuscript has nine body pages, seven figures and two main tables; detailed
counts and all six frontiers are supplementary.

The full-domain filling revision adds main Section 4.5 and Supplement S2.5.
`domain_filling_figures.py` generates a five-leaf augmented-tree illustration with
regular arc samples, checks all 120 leaf orders, and verifies rendered merge
errors and optimal-budget feasibility. It also supplies the expanded method
overview used by `layout_figures.py`. The synthetic numeric export and source
hashes are in `figure_data/domain_filling_example.json`. The regular `build.py`
regenerates these assets without changing the real-data algorithms or outcomes.

## Current RG-MTM exports

Run `PYTHONPATH=src python tools/build_rgmtm_figures.py` for the active PNG/SVG figure set. Historical builders above regenerate their original asset paths. Current no-figure tables use `python tools/build_nofigure_paper_tables.py` and write source ledgers to `results/manuscript_tables/`. `package.py` packages public code, experimental results, and figures; no raw observations are included.
