"""Tests for calib.py. Run: python -I -m pytest calibration/scripts/test_calib.py
(or python -I calibration/scripts/test_calib.py)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calib  # noqa: E402


def naive_ece(p, y, n_bins=10):
    """Textbook equal-mass ECE on rows in the given order (stable sort by p)."""
    order = np.argsort(p, kind="stable")
    tot = 0.0
    for b in np.array_split(order, n_bins):
        if len(b):
            tot += len(b) / len(p) * abs(y[b].mean() - p[b].mean())
    return tot


def naive_resample(p, y, qid, draws):
    """Expand a resample: canonical order, each row repeated by its query's count."""
    counts = np.bincount(draws, minlength=qid.max() + 1)
    w = counts[qid]
    return np.repeat(p, w), np.repeat(y, w)


def test_ece_matches_naive_unweighted():
    rng = np.random.default_rng(0)
    for n in [1, 5, 10, 11, 37, 1000]:
        p = rng.random(n).round(1)  # many ties
        y = (rng.random(n) < p).astype(float)
        assert abs(calib.ece(p, y) - naive_ece(p, y)) < 1e-12


def test_ece_weighted_matches_expanded_resample():
    rng = np.random.default_rng(1)
    for trial in range(200):
        nq = rng.integers(1, 15)
        sizes = rng.integers(1, 8, size=nq)
        qid = np.repeat(np.arange(nq), sizes)
        p = rng.random(len(qid)).round(rng.integers(0, 3))
        y = (rng.random(len(qid)) < 0.4).astype(float)
        draws = rng.integers(0, nq, size=nq)
        w = np.bincount(draws, minlength=nq)[qid]
        pe, ye = naive_resample(p, y, qid, draws)
        assert abs(calib.ece(p, y, w) - naive_ece(pe, ye)) < 1e-12


def test_brier():
    p = np.array([0.0, 0.5, 1.0]); y = np.array([0.0, 1.0, 1.0])
    assert abs(calib.brier(p, y) - 0.25 / 3) < 1e-15
    assert abs(calib.brier(p, y, np.array([2, 0, 1])) - 0.0) < 1e-15


def test_bootstrap_matches_naive_and_is_reproducible():
    rng = np.random.default_rng(2)
    nq = 12
    qid = np.repeat(np.arange(nq), rng.integers(1, 6, size=nq))
    y = (rng.random(len(qid)) < 0.3).astype(float)
    P = [rng.random(len(qid)), rng.random(len(qid)).round(1)]
    rep = calib.bootstrap(P, y, qid, n_boot=50, seed=20261012)
    rep2 = calib.bootstrap(P, y, qid, n_boot=50, seed=20261012)
    assert np.array_equal(rep["ece"], rep2["ece"]) and np.array_equal(rep["brier"], rep2["brier"])
    draws = np.random.default_rng(20261012).integers(0, nq, size=(50, nq))
    for r in range(50):
        for j, p in enumerate(P):
            pe, ye = naive_resample(p, y, qid, draws[r])
            assert abs(rep["ece"][j, r] - naive_ece(pe, ye)) < 1e-12
            assert abs(rep["brier"][j, r] - np.mean((pe - ye) ** 2)) < 1e-12


def test_bootstrap_with_gapped_query_ids():
    """Production passes query ids with gaps (held-out rows, strata): queries are
    numbered in sorted order of their ids before drawing."""
    rng = np.random.default_rng(4)
    ids = np.array([3, 7, 8, 20, 21, 40])
    qid = np.repeat(ids, rng.integers(1, 6, size=len(ids)))
    y = (rng.random(len(qid)) < 0.4).astype(float)
    p = rng.random(len(qid)).round(1)
    rep = calib.bootstrap([p], y, qid, n_boot=40, seed=20261012)
    dense = np.searchsorted(ids, qid)
    draws = np.random.default_rng(20261012).integers(0, len(ids), size=(40, len(ids)))
    for r in range(40):
        pe, ye = naive_resample(p, y, dense, draws[r])
        assert len(pe) == np.bincount(draws[r], minlength=len(ids))[dense].sum()
        assert abs(rep["ece"][0, r] - naive_ece(pe, ye)) < 1e-12
        assert abs(rep["brier"][0, r] - np.mean((pe - ye) ** 2)) < 1e-12


def test_bootstrap_subset_equals_full():
    rng = np.random.default_rng(5)
    qid = np.repeat(np.arange(9), 3)
    y = (rng.random(27) < 0.5).astype(float); p = rng.random(27)
    full = calib.bootstrap([p], y, qid, n_boot=30)
    sub = calib.bootstrap([p], y, qid, n_boot=30, which=[0, 7, 29])
    assert np.array_equal(full["ece"][0, [0, 7, 29]], sub["ece"][0, [0, 7, 29]])
    assert np.isnan(sub["ece"][0, 1])


def test_raw_estimator():
    est = calib.RawMinMax().fit(np.array([1.0, 3.0]))
    assert np.allclose(est.predict(np.array([0.0, 1.0, 2.0, 3.0, 4.0])), [0, 0, 0.5, 1, 1])
    assert np.allclose(calib.RawMinMax().fit(np.array([2.0, 2.0])).predict(np.array([5.0])), [0.5])


def test_feature_estimator_runs_and_is_deterministic():
    rng = np.random.default_rng(3)
    n = 600
    X = rng.normal(size=(n, 4)); y = (X[:, 0] + rng.normal(size=n) > 1).astype(int)
    groups = np.repeat(np.arange(60), 10)
    a = calib.FeatureHGB().fit(X, y, groups).predict(X)
    b = calib.FeatureHGB().fit(X, y, groups).predict(X)
    assert np.array_equal(a, b) and a.min() >= 0 and a.max() <= 1


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f(); print("ok", name)
