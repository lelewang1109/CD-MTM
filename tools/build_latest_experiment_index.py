"""Index and verify saved public experiments; never rerun numerical experiments."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/latest"
DATASETS = ("era5", "wildfire", "olr", "pm25", "ring", "gaussians")


def snapshot():
    performance = json.loads((ROOT / "results/final_performance.json").read_text())
    images = json.loads((ROOT / "results/figures/manifest.json").read_text())
    control = json.loads((ROOT / "results/publication2027/bisector_control/bisector_highres_x_three_methods.json").read_text())
    frames = {name: performance[name]["frames"] for name in DATASETS}
    assert sum(frames.values()) == 342
    groups = {}
    for label, directory in (("core_code", "src/rgmtm"), ("analysis", "analysis"),
                             ("experiment_code", "experiments/publication2027")):
        groups[label] = sorted(p for p in (ROOT / directory).rglob("*.py") if "__pycache__" not in p.parts)
    for label, directory in (("organized_results", "results/publication2027"),
                             ("public_metrics", "results/public_metrics_20261016"),
                             ("current_figures", "results/figures")):
        groups[label] = sorted(p for p in (ROOT / directory).rglob("*")
                               if p.is_file() and p.suffix in {".json", ".csv", ".npz", ".png", ".svg", ".md"})
    groups["primary_records"] = [ROOT / "results" / name for name in (
        "final_performance.json", "final_performance.csv", "eval_projection.json", "native_merge_errors.json",
        "filling.json", "pointcert.json", "protocol_olr.json", "protocol_pm25.json",
        *[f"replicate_{name}.json" for name in DATASETS], *[f"attainable_{name}.json" for name in DATASETS])]
    groups["evaluation_and_export_code"] = [ROOT / "tools" / name for name in (
        "evaluate_public_metrics.py", "check_public_metrics.py", "evaluate_reference_task_metrics.py",
        "build_rgmtm_figures.py", "verify_rgmtm_migration.py", "check_public_export.py",
        "build_latest_experiment_index.py")]
    files = {str(p.relative_to(ROOT)): dict(group=group, bytes=p.stat().st_size,
             sha256=hashlib.sha256(p.read_bytes()).hexdigest())
             for group, paths in groups.items() for p in paths}
    return dict(scope="Saved experiments and current PNG/SVG figures; no numerical rerun or manuscript publication",
                datasets=list(DATASETS), frames=frames, total_frames=sum(frames.values()),
                bisector_control_frames=control["frames"], current_figure_groups=len(images["figures"]),
                group_counts={name: len(paths) for name, paths in groups.items()}, files=files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check the committed manifest against current bytes")
    args = parser.parse_args()
    manifest = snapshot()
    path = OUT / "manifest.json"
    if args.check:
        if json.loads(path.read_text()) != manifest:
            raise SystemExit("Experiment snapshot changed; inspect the changes and rebuild the index before upload.")
        print(f"Latest experiment snapshot verified: {len(manifest['files'])} files, "
              f"{manifest['total_frames']} main frames, {manifest['current_figure_groups']} figure groups.")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        print(f"Indexed {len(manifest['files'])} saved experiment/code/figure files; no numerical experiment rerun.")


if __name__ == "__main__":
    main()
