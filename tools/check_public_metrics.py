"""Independent checks for the public-metric evaluation, not layout tests.

Optional --sklearn-path points to an isolated installation of scikit-learn.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.spatial.distance import pdist, squareform

import evaluate_public_metrics as ev


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sklearn-path", type=Path)
    parser.add_argument("--output", type=Path, default=ev.OUT / "metric_checks.json")
    args = parser.parse_args()
    rng = np.random.default_rng(42)
    max_tw_error = max_sns_error = 0.0
    checks = 0
    if args.sklearn_path:
        sys.path.insert(0, str(args.sklearn_path))
        from sklearn.manifold import trustworthiness
        import sklearn
        for n in (3, 4, 7, 11, 20):
            for k in range(1, (n - 1) // 2 + 1):
                for _ in range(15):
                    points = rng.normal(size=(n, 2))
                    u = rng.normal(size=n)
                    expected = trustworthiness(points, u[:, None], n_neighbors=k)
                    actual = ev.b2.trustworthiness(points, u, k)
                    max_tw_error = max(max_tw_error, abs(actual - expected))
                    np.testing.assert_allclose(actual, expected, atol=1e-12)
                    checks += 1
        sklearn_version = sklearn.__version__
    else:
        sklearn_version = None
    for n in (3, 7, 11):
        for _ in range(30):
            points = rng.normal(size=(n, 2))
            u = rng.normal(size=n)
            d = squareform(pdist(points))
            # Numerically minimize the paper's original objective rather than
            # reuse the implemented closed-form scale coefficient.
            a = abs(u[:, None] - u[None, :])
            opt = minimize_scalar(lambda alpha: float(np.sum((d - alpha * a) ** 2) / np.sum(d * d)),
                                  bounds=(0, 100), method="bounded", options={"xatol": 1e-12})
            score = ev.b2.scale_normalized_stress(d, u)
            max_sns_error = max(max_sns_error, abs(score - opt.fun))
            np.testing.assert_allclose(score, opt.fun, atol=1e-10)
            np.testing.assert_allclose(score, ev.b2.scale_normalized_stress(d, -8 * u + 17), atol=1e-12)
    line = np.array([0., 1., 3., 7., 12.])
    points = np.c_[line, np.zeros(5)]
    np.testing.assert_allclose(ev.b2.scale_normalized_stress(squareform(pdist(points)), 3 * line + 20), 0, atol=1e-12)
    np.testing.assert_allclose(ev.b2.scale_normalized_stress(squareform(pdist(points)), np.zeros(5)), 1, atol=1e-12)
    assert ev.b2.trustworthiness(points, line, 1) == 1
    try:
        ev.b2.trustworthiness(points[:2], line[:2], 1)
    except ValueError:
        pass
    else:
        raise AssertionError("TW must reject k >= n/2")
    # One continuing identity (2) moves by .25; 1 disappears and 3 appears.
    centroids = [np.array([[0., 0.], [1., 0.]]), np.array([[1., 0.], [2., 0.]])]
    positions = [np.array([0., .25]), np.array([.50, 1.])]
    score, _ = ev.standard_metrics(centroids, positions, [[1, 2], [2, 3]])
    assert score["matched_steps"] == 1 and score["TD"] == .25
    assert score["TW1"] is None and score["SNS_frames"] == 2
    # A constant static layout is stable irrespective of its geometric quality.
    score, _ = ev.standard_metrics([points, points], [line, line], [list(range(5)), list(range(5))])
    assert score["TD"] == 0
    report = dict(passed=True, sklearn_version=sklearn_version, sklearn_tw_comparisons=checks,
                  max_tw_absolute_error=max_tw_error, numerical_sns_comparisons=90,
                  max_sns_absolute_error=max_sns_error,
                  checks=["SNS scale/reflection/translation invariance", "SNS collinear perfect embedding and collapsed embedding",
                          "TW public-library equivalence and invalid small-n rejection", "TD identity matching with birth/death",
                          "TD static-layout zero", "Two-feature SNS retained but TW undefined"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ev.write_json(args.output, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
