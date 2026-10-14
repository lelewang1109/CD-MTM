# Organized publication evidence

- `main_comparison.csv`: 42 unrounded rows, six datasets × seven main methods.
- `claims.json`: frame counts, conflict counts, default proxy rows, filling residuals, exact-frontier checks.
- `manifest.json`: source and snapshot hashes, figure provenance, and table hashes.
- `runs/<UTC timestamp>/manifest.json`: executed stages and per-stage status, logs, runtime, source/result hashes.
- `evidence/main/`: six-sequence replication/frontier records and active-only aggregate snapshots.
- `evidence/sensitivity/`: direction, persistence, extraction, parameter, and seasonal controls. These are retained computations unless their stage appears in the new run manifest.
- `evidence/validation/`: formal examples, witnesses, binary/degree benchmarks and boundary checks.
- `evidence/transfer/`: dendrogram diagnosis, separate from scalar-field evaluation.
- `evidence/protocols/`: prepared-data and native-curve conventions.

This folder organizes evidence without deleting or renaming original results.
The main suite has 342 frames. PM2.5 January is exploratory and has seven default
motion events. Gaussian has zero events: its motion error is undefined. Position
order error, full interval certificates, and achieved anchor displacement are
separate quantities. Scalar-cost means do not bound worst-frame cost; kappa is an
eligibility threshold rather than an achieved-distortion guarantee.

Regenerate with `PYTHONPATH=src python experiments/publication2027/build.py`.
