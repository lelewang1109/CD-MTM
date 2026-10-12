# Analysis entry points

Active membership is defined in `dataset_suite.py`: ERA5 1999/2000, wildfire,
OLR, January PM2.5, Ring and Gaussians, totalling 342 frames. Main PM2.5 was
selected after seasonal exploration; all seasonal controls remain saved.

The shared evidence chain is run by `../tools/run_paper_suite.py`. Its nine
stages are `replicate`, `evaluation`, `attainable`, `filling`, `robustness`,
`pointcert`, `persistence`, `witness_stats`, and `result_tables`.
The final stage computes all methods against the same width-free positional
certificate; `tools/update_paper_evidence.py` consumes it to create two main tables. `evaluation.py` contains both
2-D and projected motion references, native Hilbert/Morton merge costs,
fragmentation, neighbourhood costs and paired moving-block bootstrap results.

`public_scalar.py` supplies the common buffered equal-area preprocessing and
count-only smoothing rule for OLR/PM2.5. `pm25_seasons.py` and
`../tools/run_pm25_seasons.py` define the frozen four-month sensitivity control.
Protocol JSON records source hashes and preprocessing changes.

Figures are generated through the [shared visualization package](visualization/README.md):

```sh
PYTHONPATH=src python3 tools/build_visualization_gallery.py
PYTHONPATH=src python3 tools/build_visualization_gallery.py --metrics-only --out tmp/gallery-metrics
```

Run these commands from the repository root. The package separates method
metadata, render calculation, spatial/topological drawings, saved-record metrics,
and export/provenance. The legacy `fig_new_datasets.py` and
`fig_sfc_comparison.py` share its cached numeric renderer and are safe to import.
Other `fig_*` scripts remain entry points for the established manuscript figures.

`benchmark_degree.py` tests certificate scaling; `independent_scale.py` checks
certificate diagnosis at a finer extraction scale; `topological_case.py` provides
the exact-filling theory example. The scalable diagnosis benchmark does not imply
that the complete order-enumerating layout pipeline scales to the same leaf counts.

Historical configurations and earlier entry-point descriptions are retained in
`../notes/experiment-documentation-history.md`.
