# Final analysis entry points

The scripts in this directory reproduce the paper's evaluations and figures.
They share scalar-reference helpers in `task_reference.py`; its earlier X/Y
comparison driver has been removed. Outputs are written to `../results/`.

Primary entry points:

- `evaluation.py`: RQ1–RQ3 evaluation on the two ERA5 periods, wildfire, Ring,
  and Gaussian data.
- `benchmark_degree.py`: bounded-degree certificate scaling experiment.
- `independent_scale.py`: certificate-only 150 km extraction check.
- `topological_case.py`: pair-level merge-error case study.
- `attainable.py`, `frontier.py`, and `filling.py`: exact position–topology
  frontier and optimal filling checks.
- `fig_*.py`: manuscript figure generators.

