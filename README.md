# CD-MTM: Certificate-Driven Merge Tree Maps

This directory is the clean submission workspace for the PacificVis paper
**“Certified Position–Topology Trade-offs for Hierarchy-Constrained 1-D Layouts.”**
Its name follows the paper's optimization pipeline, *Certificate-Driven Merge
Tree Maps* (CD-MTM).

The earlier X/Y dual-view study is intentionally excluded. The final paper uses
one task-defined scalar reference direction, reports the unavoidable positional
certificate, and optionally relaxes hierarchy while measuring the resulting
topological cost.

## Directory layout

| Path | Purpose |
|---|---|
| `paper/pacificvis2027/` | Anonymized manuscript, VGTC style files, figures, and review PDF |
| `paper/proofs.tex` | Extended proofs for the supplement |
| `src/cdmtm/` | Certificate, layout, rendering, and baseline implementation |
| `analysis/` | Final evaluation, robustness, frontier, and figure scripts |
| `results/` | Curated JSON records used by the final manuscript |
| `tests/` | Independent certificate and projected-motion checks |
| `data/` | Raw-data instructions and a local link to public inputs |
| `tools/` | Reproducible supplement builder |

## Quick verification

From this directory, using Python 3.10 or newer:

```sh
python3 -m pip install -e .
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The main paper-facing runs are:

```sh
PYTHONPATH=src python3 -W ignore analysis/evaluation.py era5 era5_2014 wildfire ring
PYTHONPATH=src python3 -W ignore analysis/benchmark_degree.py
PYTHONPATH=src python3 -W ignore analysis/independent_scale.py
PYTHONPATH=src python3 -W ignore analysis/topological_case.py
```

These write to `results/`. Raw ERA5 and wildfire inputs are public datasets and
are not copied into the submission archive; see `data/README.md`.

Build the anonymous reproducibility archive with:

```sh
python3 tools/build_supplement.py
```

The original `RA-MTM` directory remains unchanged as the historical workspace.

