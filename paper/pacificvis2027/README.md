# PacificVis 2027 conference-paper source

`main.tex` is the anonymized conference-track manuscript. Compile this
directory with the included VGTC class, pdfLaTeX, and BibTeX. The figures and
bibliography files are included. `../proofs.tex` contains the extended proofs.

From the repository root, verify the final implementation and run the four main
paper-facing analyses with:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -W ignore analysis/evaluation.py era5 era5_2014 wildfire ring
PYTHONPATH=src python3 -W ignore analysis/benchmark_degree.py
PYTHONPATH=src python3 -W ignore analysis/independent_scale.py
PYTHONPATH=src python3 -W ignore analysis/topological_case.py
```

The evaluation writes `results/eval_projection.json`. It reports 2-D and
projected-reference motion judgments, the packed reference-sorted baseline, and
the attainable topological cost for each method. Supporting scripts in
`analysis/` reproduce the frontier, robustness, sensitivity, and figure data.

Raw public inputs and their hashes are documented in `../../data/README.md`.
They are excluded from the anonymous archive. Build that archive from the
repository root with `python3 tools/build_supplement.py`.

Before submission, replace `\\onlineid{0}` with the PCS identifier, compile the
review PDF, and confirm that body material ends by page 9. The current review
PDF has nine body pages and one references-only page.
