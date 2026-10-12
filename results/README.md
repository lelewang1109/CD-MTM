# Experiment evidence and visualization outputs

The main suite has six sequences / 342 frames: ERA5 1999/2000, wildfire,
OLR, January 2000 PM2.5, Ring and Gaussians. Main membership is defined by
`../analysis/dataset_suite.py`. Older records are kept for traceability, not
included automatically in main aggregates.

- `final_performance.json`: current per-frame order-only positional deviation and hierarchy lower bounds for every method; drives the width-free comparisons.
- `eval_projection.json`: motion errors, paired bootstrap, neighbourhood costs,
  R/packed-sort optimal-filling costs, and actual native Hilbert/Morton merge costs.
- `replicate_*.json`: frame/feature counts, packing and hierarchy certificates.
- `attainable_*.json`: exact attainable frontiers and achieved R operating points.
- `protocol_*.json`: source hashes, grid, extraction and preprocessing rules.
- `sfc_baseline_protocol.json`: fixed native ordering and actual barrier semantics.
- `revised_paper_evidence.json`: exact sources/hashes used by manuscript tables.
- `method_performance_audit.json`: declared-setting rankings, including undefined rates.
- `pm25_season_protocol.json`: four frozen 30-day seasonal controls.
- `archive/pm25_janfeb/`: superseded main period, retained for the selection audit.
- `revised_suite/`: completion manifests and per-stage logs; retired OISST outputs have been removed.

[The visualization gallery](visualizations/README.md) contains ten figures in
PNG/PDF/SVG, a combined PDF booklet, and `manifest.json` with evidence, source
and export hashes. Numeric caches under `visualization_cache/` are excluded
from Git and the supplement and can be regenerated from the same inputs.

PM2.5's January display was selected after seasonal evaluation. Its seven events
are descriptive. Gaussian has no clear events at k=2, ε=2%; this is undefined
performance, not a zero-error success. Native curve costs are measured on unchanged
scalar samples; R's costs follow optimal refilling. These are explicitly different
rendering protocols, applied to the same processed input fields.

Earlier `paper_stats.json`, `quality.json` and other historical-window records
are not sources for current manuscript claims. Historical documentation is in
`../notes/experiment-documentation-history.md`.

The two main tables follow the paper's two core contributions: unavoidable
position error under topology constraints and merge-level cost when position
is improved. `spatial_motion_controls.tex` retains the auxiliary geometric
validation. `native_merge_errors.json` measures TMTM/ST-MTM/Fixed-X scalar
barriers at the evaluated anchors; nominal-resolution checks are also saved.
