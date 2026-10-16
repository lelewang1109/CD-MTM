"""Export the current RG-MTM figure set from saved data (PNG and editable SVG).

Historical paper assets and their hash manifests are never overwritten.
Run from the repository root: PYTHONPATH=src python tools/build_rgmtm_figures.py
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "analysis"),
                str(ROOT / "experiments/publication2027")]

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figstyle as fs
import layout_figures as layout
import domain_filling_figures as domain
from dataset_suite import PAPER_DATASETS, REAL_DATASETS, LABELS
from visualization import metrics
from rgmtm.names import METHOD_LABELS

CAPTIONS = {
    "fig_teaser_focus": "ERA5: RG-MTM-P and RG-MTM-R on the same reference axis.",
    "fig_method_visual": "Construction, scalar filling, and disclosed errors.",
    "fig_diagnosis_tradeoff": "Packing/hierarchy certificates and exact small-tree frontiers.",
    "fig_motion_scalar_cost": "Motion errors, paired exploratory intervals, and scalar costs.",
    "fig_linked_cases": "ERA5 and OLR cases; sequence-level counts and local windows.",
    "fig_full_domain_filling": "Synthetic augmented-tree samples and scalar correction.",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Exporter:
    def __init__(self, out):
        self.out = out
        self.items = []

    def save(self, fig, stem, caption=""):
        # Domain filling passes an output directory as its third argument.
        caption = caption if isinstance(caption, str) else ""
        caption = caption or CAPTIONS.get(stem, stem)
        stem = "rgmtm_" + stem.removeprefix("fig_")
        files = {}
        for extension in ("png", "svg"):
            path = self.out / f"{stem}.{extension}"
            fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
            files[path.name] = sha(path)
        plt.close(fig)
        self.items.append(dict(stem=stem, caption=caption, files=files))
        print("Exported", stem, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "results/figures")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    fs.apply()
    plt.rcParams.update({"svg.fonttype": "none", "svg.hashsalt": "rgmtm-current"})
    export = Exporter(args.out)
    layout.save = export.save
    domain.save = export.save
    arrays = {name: layout.load(name) for name in ("era5", "olr")}
    layout.teaser(arrays["era5"])
    domain.overview(args.out)
    layout.diagnosis_frontier()
    layout.motion_cost()
    selection = layout.cases(arrays)
    frame = domain.example()
    profiles = domain.render_checked(frame)
    domain.detail(frame, profiles)
    records = json.loads((ROOT / "results/eval_projection.json").read_text())
    metrics.motion_errors(records, PAPER_DATASETS, LABELS, export)
    metrics.topology_motion(records, REAL_DATASETS, LABELS, export)
    metrics.neighbourhoods(records, PAPER_DATASETS, LABELS, export)
    metrics.motion_sensitivity(records, PAPER_DATASETS, LABELS, export)
    subprocess.run([sys.executable, str(ROOT / "experiments/publication2027/rgmtm_bisector_figure.py"),
                    "--out", str(args.out)], check=True)
    stem = "rgmtm_bisector_absolute_position"
    export.items.append(dict(stem=stem, caption="Bisector control: TMTM, ST-MTM and RG-MTM-R in side-by-side panels with identical time ranges.",
        files={f"{stem}.{ext}": sha(args.out / f"{stem}.{ext}") for ext in ("png", "svg")}))
    evidence = [ROOT / "results/eval_projection.json",
                *sorted((ROOT / "results/publication2027/figure_data").glob("*_render.npz")),
                ROOT / "results/publication2027/bisector_control/bisector_highres_x_three_methods.npz"]
    sources = [Path(__file__), ROOT / "experiments/publication2027/layout_figures.py",
               ROOT / "experiments/publication2027/domain_filling_figures.py",
               ROOT / "experiments/publication2027/rgmtm_bisector_figure.py",
               ROOT / "src/rgmtm/names.py", *sorted((ROOT / "analysis/visualization").glob("*.py"))]
    manifest = dict(method="Reference-Guided Merge Tree Maps", modes=["RG-MTM-P", "RG-MTM-R"],
        scope="Presentation export from saved evidence; no real-data numerical rerun",
        method_labels=METHOD_LABELS, selection=selection, figures=export.items,
        evidence_sha256={str(p.relative_to(ROOT)): sha(p) for p in evidence},
        source_sha256={str(p.relative_to(ROOT)): sha(p) for p in sources})
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    lines = ["# RG-MTM 实验图片", "", "统一使用 RG-MTM-P / RG-MTM-R 名称；PNG 为预览，SVG 为可编辑矢量图。",
             "从保存的数值记录和绘图数组重建，未重跑真实数据实验。原论文图片及其溯源清单保留在历史路径。",
             "", "重建：`PYTHONPATH=src python tools/build_rgmtm_figures.py`。", "",
             "A → RG-MTM-P；R 20% → RG-MTM-R。原始 JSON 方法键保持。", ""]
    for item in export.items:
        stem = item["stem"]
        lines += [f"## {stem}", "", item["caption"], "", f"[SVG]({stem}.svg)", "", f"![{stem}]({stem}.png)", ""]
    (args.out / "README.md").write_text("\n".join(lines))
    print(f"Exported {len(export.items)} RG-MTM figures; source/evidence hashes saved.")


if __name__ == "__main__":
    main()
