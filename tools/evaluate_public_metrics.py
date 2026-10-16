"""Re-evaluate the retained six-sequence suite using ST-MTM Sec. 5.2 metrics.

Writes a separate, reproducible evaluation; never edits the manuscript, legacy
results, source fields, or layout parameters. No result-driven parameter search.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy.spatial.distance import pdist, squareform

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "analysis"), str(ROOT / "src"), str(ROOT)]

import replicate as rp
import general_method as gm
import relax_hierarchy as rh
from experiments import era5 as ep
from rgmtm.baselines import stmtm as b2
from rgmtm.reference_points import reference_points_from_frames

DATASETS = ("era5", "wildfire", "olr", "pm25", "ring", "gaussians")
METHODS = ("TMTM", "ST-MTM", "RG-MTM-P", "RG-MTM-R")
OUT = ROOT / "results/public_metrics_20261016"
PROTOCOL = {
    "source": "Local ST-MTM preprint, Section 5.2, PDF page 8",
    "metrics": ["SNS", "TW", "TD"],
    "landmarks": "Unweighted leaf-arc support centroids, aligned to exact leaf IDs",
    "display_positions": "Actual raster anchors, all methods on a fixed [0,1] full canvas per sequence",
    "sns": "Frame mean of min_alpha sum(d_ij-alpha*abs(x_i-x_j))^2 / sum(d_ij^2), no square root",
    "sns_eligibility": "n >= 2 and nonzero original pair distances; n >= 3 mean also reported",
    "tw": "Standard rank-penalized trustworthiness; k=1 primary for every dataset/method",
    "tw_eligibility": "0 < k < n/2; k=3 and k=5 secondary, only on eligible frames",
    "ties": "Stable leaf-row order in both distance rankings; tied frames counted; no-tie sensitivity reported",
    "td": "SUM of absolute matched-anchor displacement over consecutive frames, not an average",
    "td_units": "Full-canvas widths (one fixed affine raster/canvas mapping per method/sequence); also common 2048-pixel units",
    "td_caution": "Measures stability, not correctness of motion; compare methods within each dataset",
    "parameters": "Existing main configurations unchanged: RG-MTM-R eligibility 0.2*scalar range; ST temporal settings retained",
    "decision": "No universal acceptance threshold; report wins/ties/losses against each baseline without a combined score",
    "excluded": "No runtime or publication-number replication claim; source preprint uses different preprocessing/resolution",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_sha(array):
    array = np.ascontiguousarray(array)
    return hashlib.sha256(str((array.shape, array.dtype.str)).encode() + array.tobytes()).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def avg(values):
    return float(np.mean(values)) if values else None


def distance_ties(distances):
    return any(len(np.unique(np.delete(row, i))) < len(row) - 1
               for i, row in enumerate(distances))


def standard_metrics(centroids, positions, tracks):
    frame_rows = []
    sums = {"sns": [], "sns_n3": [], "tw1": [], "tw3": [], "tw5": [], "tw1_no_ties": []}
    steps = []
    for t, (points, u, identities) in enumerate(zip(centroids, positions, tracks)):
        n = len(u)
        assert points.shape == (n, 2) and len(identities) == n
        assert len(set(identities)) == n and np.isfinite(u).all()
        d0 = squareform(pdist(points))
        d1 = abs(u[:, None] - u[None, :])
        tied = distance_ties(d0) or distance_ties(d1)
        record = dict(frame=t, features=n, distance_ties=tied,
                      sns=None, tw1=None, tw3=None, tw5=None,
                      matched_steps=0, td_step=0.0)
        if n >= 2 and float(np.sum(d0 * d0)) > 0:
            record["sns"] = b2.scale_normalized_stress(d0, u)
            sums["sns"].append(record["sns"])
            if n >= 3:
                sums["sns_n3"].append(record["sns"])
        for k in (1, 3, 5):
            if k < n / 2:
                score = b2.trustworthiness(points, u, k)
                assert -1e-12 <= score <= 1 + 1e-12
                record[f"tw{k}"] = score
                sums[f"tw{k}"].append(score)
                if k == 1 and not tied:
                    sums["tw1_no_ties"].append(score)
        if t:
            lookup = {identity: i for i, identity in enumerate(tracks[t - 1])}
            step = [abs(float(u[i] - positions[t - 1][lookup[identity]]))
                    for i, identity in enumerate(identities) if identity in lookup]
            steps.extend(step)
            record["matched_steps"] = len(step)
            record["td_step"] = float(sum(step))
        frame_rows.append(record)
    summary = dict(
        frames=len(positions), features_min=min(map(len, positions)), features_max=max(map(len, positions)),
        SNS=avg(sums["sns"]), SNS_frames=len(sums["sns"]),
        SNS_n3=avg(sums["sns_n3"]), SNS_n3_frames=len(sums["sns_n3"]),
        TW1=avg(sums["tw1"]), TW1_frames=len(sums["tw1"]),
        TW3=avg(sums["tw3"]), TW3_frames=len(sums["tw3"]),
        TW5=avg(sums["tw5"]), TW5_frames=len(sums["tw5"]),
        TW1_no_ties=avg(sums["tw1_no_ties"]), TW1_no_ties_frames=len(sums["tw1_no_ties"]),
        distance_tie_frames=sum(r["distance_ties"] for r in frame_rows),
        TD=float(sum(steps)), TD_common2048px=float(sum(steps)) * 2047,
        matched_steps=len(steps), TD_per_match=avg(steps),
    )
    assert abs(summary["TD"] - sum(r["td_step"] for r in frame_rows)) < 1e-10
    return summary, frame_rows


def pad(rows, width, dtype=float, missing=np.nan):
    trailing = np.asarray(rows[0]).shape[1:]
    result = np.full((len(rows), width) + trailing, missing, dtype=dtype)
    for t, row in enumerate(rows):
        result[t, :len(row)] = row
    return result


def baseline_positions(dataset, method):
    sc = dataset["sc"]
    span = dataset["native_span"]
    params = gm.Parameters(canvas=span, canvas_origin=float(min(dataset["lo"][0], 0.)),
                           width_scale=.5 * span / dataset["domain_area"],
                           gap=span / 240, extra_budget=span / 120, rho=.5)
    kwargs = dict(canvas=span, length=dataset["nominal"], refine_raster=False, strict_checks=False)
    if dataset["name"] == "ring":
        kwargs["stmtm_parameters"] = ep.b2.LayoutParameters.from_preset("ring")
    result = ep.run_method(sc, method, params, **kwargs)
    physical = [np.asarray(row["pixel_x"], float) for row in result["rows"]]
    length = result["maps"].shape[0]
    if method == "TMTM":
        # pixel_x has already been decoded to span units. Gauge translation
        # and reflection are fixed for the entire sequence; undo for canvas.
        scale, shift = result["gauge"]["scale"], result["gauge"]["shift"]
        fractions = [(u - shift) / scale / span for u in physical]
        if scale < 0:
            fractions = [1 - u for u in fractions]
    else:
        fractions = []
        reflected = result["gauge"]["scale"] < 0
        for skeleton, leaves in zip(result["records"]["discrete"], sc["ids"]):
            lookup = {leaf: i for i, leaf in enumerate(skeleton["ordering"])}
            u = np.asarray(skeleton["anchors"], float)[[lookup[leaf] for leaf in leaves]] / (length - 1)
            fractions.append(1 - u if reflected else u)
    return fractions, physical, dict(raster_length=length, construction="existing baseline runner", gauge=result["gauge"])


def evaluate_dataset(name, output):
    start = time.perf_counter()
    print(f"START {name}: load unchanged input", flush=True)
    ds = rp.LOADERS[name]()
    sc = ds["sc"]
    centroids = reference_points_from_frames(sc["frames"], sc["ids"], kind="centroid")
    for expected, actual in zip(sc["centers"], centroids):
        np.testing.assert_allclose(expected, actual, atol=1e-12)
    ext = reference_points_from_frames(sc["frames"], sc["ids"], kind="extremum")
    matrices, physical, metadata = {}, {}, {}
    for method in METHODS[:2]:
        print(f"  {name} {method}", flush=True)
        matrices[method], physical[method], metadata[method] = baseline_positions(ds, method)
    print(f"  {name} RG-MTM-P/R, fixed existing parameters", flush=True)
    run = rh.run(ds, .2, make_figure=False, return_internal=True)
    internal = run["_internal"]
    parameters = internal["p"]
    for method, key in (("RG-MTM-P", "A_full_hierarchy"), ("RG-MTM-R", "R_relaxed")):
        rows = internal["results"][key]["_rows"]
        length = internal["results"][key]["raster_length"]
        raw = [np.asarray(row["x"], float) for row in rows]
        # Exactly the reference renderer's rounding, in original leaf-row order.
        u = [np.rint((x - parameters.canvas_origin) * (length - 1) / parameters.canvas) / (length - 1) for x in raw]
        matrices[method] = u
        physical[method] = raw
        metadata[method] = dict(raster_length=length, canvas_origin=parameters.canvas_origin,
                                canvas=parameters.canvas, construction="existing rh.run threshold policy")
    records, frames = [], []
    old = json.loads((ROOT / "results/eval_projection.json").read_text())[name]
    old_keys = {"RG-MTM-P": "A", "RG-MTM-R": "R 20%"}
    validation = {}
    for method in METHODS:
        U = matrices[method]
        assert all(np.all((u >= -1e-10) & (u <= 1 + 1e-10)) for u in U)
        summary, per_frame = standard_metrics(centroids, U, sc["tracks"])
        records.append(dict(dataset=name, method=method, **summary))
        frames.extend(dict(dataset=name, method=method, **row) for row in per_frame)
        # Verify deterministic reconstruction against two distinct retained
        # old diagnostics on their original extremum/native-coordinate basis.
        from evaluation import hidden_costs
        oldkey = old_keys.get(method, method)
        span = max(float(max(u.max() for u in physical[method]) - min(u.min() for u in physical[method])), 1e-9)
        recalculated = hidden_costs(sc, ext, physical[method], span)
        checks = {}
        for key in ("stress", "jitter", "order_flip_rate", "nn_preservation"):
            actual, expected = recalculated[key], old["hidden"][oldkey][key]
            checks[key] = None if actual is None or expected is None else abs(actual - expected)
            if actual is not None and expected is not None:
                assert abs(actual - expected) < 2e-7, (name, method, key, actual, expected)
        validation[method] = checks
        print(f"  RESULT {method}: SNS={summary['SNS']:.6f}, TW1={summary['TW1']:.6f}, TD={summary['TD']:.6f}", flush=True)
    width = max(map(len, sc["ids"]))
    arrays = dict(centroids=pad(centroids, width), extrema=pad(ext, width),
                  feature_ids=pad(sc["ids"], width, int, -1), tracks=pad(sc["tracks"], width, int, -1),
                  count=np.asarray(list(map(len, sc["ids"]))), dates=np.asarray(sc.get("dates", [str(t) for t in range(len(sc["ids"]))])))
    for i, method in enumerate(METHODS):
        arrays[f"u{i}"] = pad(matrices[method], width)
    np.savez_compressed(output / f"{name}_landmarks.npz", **arrays)
    result = dict(dataset=name, protocol=PROTOCOL, methods=metadata, results=records,
                  reconstruction_checks=validation,
                  input_sha256={k: array_sha(sc[k]) for k in ("fields", "coords")},
                  landmarks_sha256=sha(output / f"{name}_landmarks.npz"), seconds=time.perf_counter() - start)
    write_json(output / f"{name}.json", result)
    write_csv(output / f"{name}_frames.csv", frames)
    print(f"DONE {name} {result['seconds']:.1f}s", flush=True)
    return result


def aggregate(output):
    loaded = [json.loads((output / f"{name}.json").read_text()) for name in DATASETS if (output / f"{name}.json").exists()]
    records = [r for d in loaded for r in d["results"]]
    write_csv(output / "summary.csv", records)
    comparisons = []
    for d in loaded:
        by_method = {r["method"]: r for r in d["results"]}
        for ours in METHODS[2:]:
            for baseline in METHODS[:2]:
                for metric, sign in (("SNS", -1), ("TW1", 1), ("TD", -1)):
                    a, b = by_method[ours][metric], by_method[baseline][metric]
                    difference = a - b
                    outcome = "tie" if abs(difference) < 1e-10 else "better" if sign * difference > 0 else "worse"
                    comparisons.append(dict(dataset=d["dataset"], ours=ours, baseline=baseline,
                                            metric=metric, ours_value=a, baseline_value=b, difference=difference,
                                            outcome=outcome, descriptive_only=True))
    write_csv(output / "comparisons.csv", comparisons)
    # On tied distance frames, stable-ID tie resolution is explicit. A separate
    # sensitivity uses the SAME untied frames for all methods in each dataset.
    common_untied = []
    for d in loaded:
        name = d["dataset"]
        with np.load(output / f"{name}_landmarks.npz", allow_pickle=False) as arrays:
            values = {method: [] for method in METHODS}
            for t, count in enumerate(arrays["count"]):
                n = int(count)
                if n < 3:
                    continue
                points = arrays["centroids"][t, :n]
                positions = [arrays[f"u{i}"][t, :n] for i in range(len(METHODS))]
                if distance_ties(squareform(pdist(points))) or any(distance_ties(abs(u[:, None] - u[None, :])) for u in positions):
                    continue
                for method, u in zip(METHODS, positions):
                    values[method].append(b2.trustworthiness(points, u, 1))
            common_untied.extend(dict(dataset=name, method=method, TW1=avg(scores), frames=len(scores))
                                 for method, scores in values.items())
    write_csv(output / "tw_common_untied.csv", common_untied)
    sources = sorted(p for folder in ("src", "analysis", "experiments") for p in (ROOT / folder).rglob("*.py"))
    manifest = dict(protocol=PROTOCOL, datasets=[d["dataset"] for d in loaded],
                    total_frames=sum(d["results"][0]["frames"] for d in loaded),
                    runtime=dict(python=sys.version, numpy=np.__version__, platform=platform.platform()),
                    evaluator_sha256=sha(__file__), source_sha256={str(p.relative_to(ROOT)): sha(p) for p in sources},
                    retained_evaluation_sha256=sha(ROOT / "results/eval_projection.json"),
                    outputs_sha256={p.name: sha(p) for p in output.iterdir() if p.suffix in ("csv", "npz", "json") and p.name != "manifest.json"})
    write_json(output / "manifest.json", manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("datasets", nargs="*")
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--aggregate", action="store_true")
    args = parser.parse_args()
    if any(name not in DATASETS for name in args.datasets):
        parser.error("unknown dataset; choose from " + ", ".join(DATASETS))
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "protocol.json", PROTOCOL)
    if not args.aggregate:
        for name in args.datasets or DATASETS:
            evaluate_dataset(name, args.output)
    aggregate(args.output)


if __name__ == "__main__":
    main()
