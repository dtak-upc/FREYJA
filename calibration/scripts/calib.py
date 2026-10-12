"""Calibration metrics, bootstrap and the three pre-registered estimators.

Conventions (PREREGISTRATION.md §4, §7):
- Rows are passed in canonical order (query id, rank).
- ECE: 10 equal-mass bins. Rows (each repeated w times, copies adjacent) are
  sorted stably by p and the expanded sequence is cut like numpy.array_split
  into 10 consecutive bins; ECE = sum_b n_b/N |mean(y_b) - mean(p_b)|.
- Bootstrap: one numpy.random.default_rng(seed) per call; draws =
  rng.integers(0, n_queries, size=(n_boot, n_queries)); a query drawn c times
  contributes all its rows with weight c.
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import GroupKFold

SEED = 20261012
N_BINS = 10
N_BOOT = 1000


def _bin_edges(total, n_bins=N_BINS):
    """Start/end positions of numpy.array_split(range(total), n_bins)."""
    q, r = divmod(total, n_bins)
    sizes = np.array([q + 1] * r + [q] * (n_bins - r), dtype=np.int64)
    ends = np.cumsum(sizes)
    return ends - sizes, ends


def _ece_sorted(p_s, y_s, w_s, n_bins=N_BINS):
    """ECE on rows already sorted by p, with integer weights w_s."""
    c = np.cumsum(w_s)                      # end position of each row
    total = int(c[-1]) if len(c) else 0
    if total == 0:
        return np.nan
    cy = np.cumsum(w_s * y_s)
    cp = np.cumsum(w_s * p_s)

    def cum_at(pos):
        # weighted sums of y and p over expanded positions [0, pos)
        pos = np.asarray(pos)
        r = np.searchsorted(c, pos, side="right")  # row containing position pos
        r_c = np.minimum(r, len(c) - 1)
        start = c[r_c] - w_s[r_c]
        prev_y = np.where(r > 0, cy[np.maximum(r - 1, 0)], 0.0)
        prev_p = np.where(r > 0, cp[np.maximum(r - 1, 0)], 0.0)
        inside = np.where(r < len(c), pos - start, 0)
        return prev_y + inside * y_s[r_c], prev_p + inside * p_s[r_c]

    lo, hi = _bin_edges(total, n_bins)
    ylo, plo = cum_at(lo)
    yhi, phi = cum_at(hi)
    n = (hi - lo).astype(float)
    keep = n > 0
    return float(np.sum(np.abs((yhi - ylo)[keep] - (phi - plo)[keep])) / total)


def ece(p, y, w=None, n_bins=N_BINS):
    p = np.asarray(p, dtype=float); y = np.asarray(y, dtype=float)
    w = np.ones(len(p), dtype=np.int64) if w is None else np.asarray(w, dtype=np.int64)
    order = np.argsort(p, kind="stable")
    return _ece_sorted(p[order], y[order], w[order], n_bins)


def brier(p, y, w=None):
    p = np.asarray(p, dtype=float); y = np.asarray(y, dtype=float)
    if w is None:
        return float(np.mean((p - y) ** 2))
    w = np.asarray(w, dtype=float)
    return float(np.sum(w * (p - y) ** 2) / np.sum(w))


def query_index(qid):
    """Map arbitrary query labels to 0..n_q-1 in order of first appearance sorted."""
    uniq, inv = np.unique(qid, return_inverse=True)
    return inv, len(uniq)


def bootstrap(P, y, qid, n_boot=N_BOOT, seed=SEED, which=None):
    """Replicates of ECE and Brier for each prediction vector in P (same resamples).

    Returns dict with arrays ece[j, r], brier[j, r] and the draws used. `which`
    (optional) lists the replicate indices to compute; the others are NaN. The
    draws are always generated in full, so replicate r is the same either way.
    """
    y = np.asarray(y, dtype=float)
    qi, nq = query_index(qid)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, nq, size=(n_boot, nq))
    E = np.empty((len(P), n_boot)); B = np.empty((len(P), n_boot))
    nrows_q = np.bincount(qi, minlength=nq).astype(float)
    for j, p in enumerate(P):
        p = np.asarray(p, dtype=float)
        order = np.argsort(p, kind="stable")
        p_s, y_s, q_s = p[order], y[order], qi[order]
        sq_q = np.bincount(qi, weights=(p - y) ** 2, minlength=nq)
        E[j, :] = np.nan; B[j, :] = np.nan
        for r in (range(n_boot) if which is None else which):
            cnt = np.bincount(draws[r], minlength=nq)
            E[j, r] = _ece_sorted(p_s, y_s, cnt[q_s])
            B[j, r] = np.dot(cnt, sq_q) / np.dot(cnt, nrows_q)
    return {"ece": E, "brier": B, "draws": draws}


def interval(rep):
    return float(np.percentile(rep, 2.5)), float(np.percentile(rep, 97.5))


class RawMinMax:
    """(a) raw: score min-max scaled on the fitting rows, clipped to [0, 1]."""

    def fit(self, s):
        self.lo, self.hi = float(np.min(s)), float(np.max(s))
        return self

    def predict(self, s):
        s = np.asarray(s, dtype=float)
        if self.hi == self.lo:
            return np.full(len(s), 0.5)
        return np.clip((s - self.lo) / (self.hi - self.lo), 0.0, 1.0)


class IsoScore:
    """(b) isotonic regression of label on score."""

    def fit(self, s, y):
        self.iso = IsotonicRegression(out_of_bounds="clip").fit(np.asarray(s, float), np.asarray(y, float))
        return self

    def predict(self, s):
        return self.iso.predict(np.asarray(s, float))


class FeatureHGB:
    """(c) HistGradientBoostingClassifier on the 22 features, isotonic-calibrated
    on its 5-fold out-of-fold predictions (folds grouped by query column)."""

    def fit(self, X, y, groups):
        X = np.asarray(X, float); y = np.asarray(y, int)
        self.clf = HistGradientBoostingClassifier(random_state=SEED).fit(X, y)
        oof = np.empty(len(y))
        for tr, te in GroupKFold(n_splits=5).split(X, y, groups):
            m = HistGradientBoostingClassifier(random_state=SEED).fit(X[tr], y[tr])
            oof[te] = m.predict_proba(X[te])[:, 1]
        self.iso = IsotonicRegression(out_of_bounds="clip").fit(oof, y)
        return self

    def predict(self, X):
        return self.iso.predict(self.clf.predict_proba(np.asarray(X, float))[:, 1])
