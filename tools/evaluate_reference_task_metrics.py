"""Standard rank correlations and classification metrics on retained layouts.

Task targets (a fixed projected reference and geometric motion labels) are
explicit. These are not universal geometry scores or human-study results.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau, spearmanr

import evaluate_public_metrics as ev


PROTOCOL = {
    "rank_target": "Same automatic fixed direction as the existing RG-MTM, projected EXTREMUM positions",
    "rank_metrics": "SciPy Kendall tau-b and Spearman rho, frame means on common eligible n>=3 frames; n>=2 also reported",
    "orientation": "One optional whole-sequence reflection per method, determined by reference min/max anchors in the FIRST informative frame common to all methods; never choose reflection per frame or by whole-sequence score",
    "rank_main": "First-frame orientation-aligned scores; original orientation also reported",
    "motion_target": "Euclidean extremum-pair distance change over two steps; thresholds 2% domain diagonal and 2% method full-sequence occupied anchor range",
    "motion_main": "Three-class approach/unchanged/separate classification on ALL tracked-pair windows",
    "motion_eligibility": "At least two true classes; a sequence with only unchanged truth is not evidence of motion classification quality",
    "motion_supplement": "Clear-event subset, approach/separate with unchanged predictions counted as misses; accuracy is exactly 1-ME apart from any raster-rounding differences",
    "classification": "scikit-learn accuracy, balanced_accuracy, and macro F1; three-class F1 fixes labels [-1,0,1], clear-event F1 fixes [-1,1]",
    "interpretation": "Standard metric formulas with declared task targets; no participant responses, universal superiority threshold, or new tuning",
}


def mean(values):
    return float(np.mean(values)) if values else None


def load_landmarks(name):
    path = ev.OUT / f"{name}_landmarks.npz"
    with np.load(path, allow_pickle=False) as z:
        sizes = z["count"]
        extrema = [z["extrema"][t, :int(n)].copy() for t, n in enumerate(sizes)]
        tracks = [z["tracks"][t, :int(n)].tolist() for t, n in enumerate(sizes)]
        positions = [[z[f"u{i}"][t, :int(n)].copy() for t, n in enumerate(sizes)] for i in range(4)]
    return extrema, tracks, positions


def direction(extrema, tracks):
    previous, current = ev.gm.motion_pairs(dict(tracks=tracks), extrema)
    motion = current - previous
    _, vectors = np.linalg.eigh(motion.T @ motion)
    axis = vectors[:, -1]
    if np.sum(motion @ axis) < 0:
        axis = -axis
    return axis


def rank_scores(q, positions):
    first = None
    for t, targets in enumerate(q):
        if len(targets) < 2 or np.ptp(targets) <= 1e-12:
            continue
        lo, hi = int(np.argmin(targets)), int(np.argmax(targets))
        if all(abs(U[t][hi] - U[t][lo]) > 1e-12 for U in positions):
            first = t
            break
    if first is None:
        raise ValueError("No common informative orientation frame")
    lo, hi = int(np.argmin(q[first])), int(np.argmax(q[first]))
    records, details = [], []
    for method, U in zip(ev.METHODS, positions):
        sign = 1 if U[first][hi] > U[first][lo] else -1
        collected = {key: [] for key in ("tau_n2", "tau_n3", "rho_n2", "rho_n3", "raw_tau_n3", "raw_rho_n3")}
        for t, (targets, u) in enumerate(zip(q, U)):
            if len(u) < 2:
                continue
            tau = float(kendalltau(targets, u, variant="b").statistic)
            rho = float(spearmanr(targets, u).statistic)
            if not np.isfinite([tau, rho]).all():
                continue
            collected["tau_n2"].append(sign * tau)
            collected["rho_n2"].append(sign * rho)
            if len(u) >= 3:
                for key, value in (("tau_n3", sign * tau), ("rho_n3", sign * rho),
                                   ("raw_tau_n3", tau), ("raw_rho_n3", rho)):
                    collected[key].append(value)
            details.append(dict(method=method, frame=t, features=len(u), Kendall_tau_b=sign * tau,
                                Spearman_rho=sign * rho, raw_tau=tau, raw_rho=rho))
        records.append(dict(method=method, orientation_frame=first, orientation_sign=sign,
                            Kendall_tau_b=mean(collected["tau_n3"]), Spearman_rho=mean(collected["rho_n3"]),
                            frames_n3=len(collected["tau_n3"]), Kendall_tau_b_n2=mean(collected["tau_n2"]),
                            Spearman_rho_n2=mean(collected["rho_n2"]), frames_n2=len(collected["tau_n2"]),
                            raw_Kendall_tau_b=mean(collected["raw_tau_n3"]), raw_Spearman_rho=mean(collected["raw_rho_n3"])))
    return records, details


def motion_scores(extrema, tracks, positions, diagonal, metrics):
    truth, pair_windows, predictions = [], [], [[] for _ in ev.METHODS]
    extents = [max(float(max(x.max() for x in U) - min(x.min() for x in U)), 1e-9) for U in positions]
    def judge(change, epsilon):
        return -1 if change < -epsilon else 1 if change > epsilon else 0
    for t in range(len(tracks) - 2):
        current = {identity: i for i, identity in enumerate(tracks[t])}
        future = {identity: i for i, identity in enumerate(tracks[t + 2])}
        common = [identity for identity in tracks[t] if identity in future]
        from itertools import combinations
        for a, b in combinations(common, 2):
            ia, ib, ja, jb = current[a], current[b], future[a], future[b]
            change = np.linalg.norm(extrema[t + 2][ja] - extrema[t + 2][jb]) - np.linalg.norm(extrema[t][ia] - extrema[t][ib])
            truth.append(judge(change, .02 * diagonal))
            pair_windows.append(dict(frame=t, track_i=a, track_j=b, true_class=truth[-1]))
            for p, (U, extent) in enumerate(zip(positions, extents)):
                delta = abs(U[t + 2][ja] - U[t + 2][jb]) - abs(U[t][ia] - U[t][ib])
                predictions[p].append(judge(delta, .02 * extent))
    truth = np.asarray(truth)
    clear = truth != 0
    rows, events = [], []
    for method, predicted in zip(ev.METHODS, predictions):
        predicted = np.asarray(predicted)
        for scope, mask, labels in (("all_three_classes", np.ones(len(truth), bool), [-1, 0, 1]),
                                    ("clear_events", clear, [-1, 1])):
            y, pred = truth[mask], predicted[mask]
            eligible = len(np.unique(y)) >= 2
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                accuracy = float(metrics.accuracy_score(y, pred)) if len(y) else None
                ba = float(metrics.balanced_accuracy_score(y, pred)) if eligible else None
                f1 = float(metrics.f1_score(y, pred, labels=labels, average="macro", zero_division=0)) if eligible else None
            rows.append(dict(method=method, scope=scope, events=len(y),
                             approach=int(sum(y == -1)), unchanged=int(sum(y == 0)), separate=int(sum(y == 1)),
                             classes=len(np.unique(y)), accuracy=accuracy if eligible else None,
                             balanced_accuracy=ba, macro_F1=f1,
                             reversal=int(sum((y != 0) & (pred == -y))), miss=int(sum((y != 0) & (pred == 0)))))
        events.extend(dict(method=method, **window, predicted_class=int(value)) for window, value in zip(pair_windows, predicted))
    return rows, events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sklearn-path", type=Path)
    args = parser.parse_args()
    if args.sklearn_path:
        sys.path.insert(0, str(args.sklearn_path))
    from sklearn import metrics
    import sklearn
    output = ev.OUT / "reference_tasks"
    output.mkdir(parents=True, exist_ok=True)
    ev.write_json(output / "protocol.json", PROTOCOL)
    ranks, classes, validation = [], [], {}
    old = json.loads((ev.ROOT / "results/eval_projection.json").read_text())
    for name in ev.DATASETS:
        extrema, tracks, U = load_landmarks(name)
        axis = direction(extrema, tracks)
        q = [xy @ axis for xy in extrema]
        scores, frames = rank_scores(q, U)
        ranks.extend(dict(dataset=name, **score) for score in scores)
        ev.write_csv(output / f"{name}_rank_frames.csv", frames)
        ds = ev.rp.LOADERS[name]()
        retained = json.loads((ev.OUT / f"{name}.json").read_text())
        for key in ("fields", "coords"):
            assert ev.array_sha(ds["sc"][key]) == retained["input_sha256"][key]
        # Validate the reconstructed automatic reference direction.
        ref = ev.gm.auto_reference(ds["sc"], extrema, ds["lo"], ds["hi"])
        np.testing.assert_allclose(axis, ref["candidates"]["direction"]["a"], atol=1e-12)
        rows, events = motion_scores(extrema, tracks, U, float(np.linalg.norm(ds["hi"] - ds["lo"])), metrics)
        classes.extend(dict(dataset=name, **row) for row in rows)
        ev.write_csv(output / f"{name}_motion_events.csv", events)
        changes = {}
        for method, legacy in zip(ev.METHODS, ("TMTM", "ST-MTM", "A", "R 20%")):
            row = next(r for r in rows if r["method"] == method and r["scope"] == "clear_events")
            previous = next(r for r in old[name]["proxy"] if r["method"] == legacy and r["k"] == 2 and r["eps"] == .02)
            assert row["events"] == previous["clear"]
            old_errors = round(previous["error"] * previous["clear"]) if previous["clear"] else 0
            changes[method] = (row["reversal"] + row["miss"]) - old_errors
        validation[name] = dict(axis=axis.tolist(), input_hashes_match=True, clear_event_error_change_due_to_raster=changes)
        print(name, [(r["method"], round(r["Kendall_tau_b"], 4), round(r["Spearman_rho"], 4)) for r in scores], flush=True)
        print(" motion", [(r["method"], r["scope"], r["balanced_accuracy"], r["macro_F1"]) for r in rows], flush=True)
    ev.write_csv(output / "rank_summary.csv", ranks)
    ev.write_csv(output / "motion_summary.csv", classes)
    ev.write_json(output / "validation.json", validation)
    ev.write_json(output / "manifest.json", dict(protocol=PROTOCOL, sklearn_version=sklearn.__version__,
                   evaluator_sha256=ev.sha(__file__), parent_evaluator_sha256=ev.sha(ev.__file__),
                   input_landmark_sha256={name: ev.sha(ev.OUT / f"{name}_landmarks.npz") for name in ev.DATASETS},
                   output_sha256={p.name: ev.sha(p) for p in output.iterdir() if p.name != "manifest.json"}))


if __name__ == "__main__":
    main()
