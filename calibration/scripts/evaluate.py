"""Run every pre-registered design on all benchmarks scored so far
(PREREGISTRATION.md §4-§8).

Inputs: SCRATCH/<b>/pairs.csv.gz for each benchmark that has one.
Outputs: calibration/results/*.csv; SCRATCH/eval/{predictions/, replicates.csv.gz}.

Usage: python -I evaluate.py
"""
import itertools
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

import calib  # noqa: E402
from benchmarks import BENCHMARKS, CAL, ORDER, SCRATCH, pairs_path  # noqa: E402
from freyja_score import load_model  # noqa: E402

FEATS = list(load_model().feature_names_in_)
SETS = ["PRIMARY", "SECONDARY"]
EST = ["raw", "isotonic", "features"]
EVAL_DIR = SCRATCH / "eval"
RES = CAL / "results"


def load(b):
    d = pd.read_csv(pairs_path(b), float_precision="round_trip",
                    dtype={"query_ds": str, "query_attr": str, "cand_ds": str, "cand_attr": str},
                    keep_default_na=False)
    out = {}
    for s in SETS:
        m = (d["primary"] == 1).to_numpy() if s == "PRIMARY" else np.ones(len(d), bool)
        x = d.loc[m]
        out[s] = dict(
            qid=x["query_id"].to_numpy(), rank=x["rank"].to_numpy(),
            group=np.array([f"{b}|{q}" for q in x["query_id"].to_numpy()]),
            s=x["score"].to_numpy(float), y=x["label"].to_numpy(int), X=x[FEATS].to_numpy(float),
            same_origin=x["same_origin"].to_numpy(int),
            in_training=x["in_training"].to_numpy(int) if "in_training" in x else None,
        )
    return out


def concat(datas, s):
    keys = ["s", "y", "X", "group"]
    return {k: np.concatenate([d[s][k] for d in datas]) for k in keys}


class Fits:
    """Fitted estimators per (fitting benchmarks, set), cached within one run."""

    def __init__(self, data):
        self.data, self.cache = data, {}

    def get(self, fit_bs, s):
        key = (tuple(fit_bs), s)
        if key not in self.cache:
            t = time.time()
            f = concat([self.data[b] for b in fit_bs], s)
            self.cache[key] = (calib.RawMinMax().fit(f["s"]), calib.IsoScore().fit(f["s"], f["y"]),
                               calib.FeatureHGB().fit(f["X"], f["y"], f["group"]))
            print(f"    fitted {'+'.join(fit_bs)} {s} on {len(f['y'])} rows in {time.time() - t:.1f}s", flush=True)
        return self.cache[key]


def predict(models, e):
    raw, iso, feat = models
    return [raw.predict(e["s"]), iso.predict(e["s"]), feat.predict(e["X"])]


ROWS, REPS, PAIRED, STRAT_REPS = [], [], [], []


def record(design, fit_label, fit_bs, b, s, e, P, ests, fold=None, variant="all"):
    """Evaluate predictions P (list aligned with ests) on rows e; bootstrap; store."""
    if variant == "heldout_rows":
        m = e["in_training"] == 0
    else:
        m = np.ones(len(e["y"]), bool)
    y, qid = e["y"][m], e["qid"][m]
    Pm = [p[m] for p in P]
    rep = calib.bootstrap(Pm, y, qid)  # fresh default_rng(20261012) for this evaluated row set
    ids = []
    for j, est in enumerate(ests):
        row_id = len(ROWS)
        ids.append(row_id)
        lo, hi = calib.interval(rep["ece"][j]); blo, bhi = calib.interval(rep["brier"][j])
        ROWS.append(dict(row_id=row_id, design=design, fit=fit_label, fit_benchmarks="+".join(fit_bs),
                         eval=b, set=s, eval_rows=variant, estimator=est, n_rows=int(m.sum()),
                         n_queries=int(len(np.unique(qid))), n_pos=int(y.sum()), pos_rate=float(y.mean()),
                         ece=calib.ece(Pm[j], y), ece_lo=lo, ece_hi=hi,
                         brier=calib.brier(Pm[j], y), brier_lo=blo, brier_hi=bhi))
        REPS.append(pd.DataFrame({"row_id": row_id, "replicate": np.arange(calib.N_BOOT),
                                  "ece": rep["ece"][j], "brier": rep["brier"][j]}))
    if ests == EST:
        for a_, b_ in [("features", "isotonic"), ("isotonic", "raw")]:
            ja, jb = EST.index(a_), EST.index(b_)
            d = rep["ece"][ja] - rep["ece"][jb]
            PAIRED.append(dict(design=design, fit=fit_label, eval=b, set=s, eval_rows=variant,
                               contrast=f"ece_{a_}_minus_{b_}",
                               diff=ROWS[ids[ja]]["ece"] - ROWS[ids[jb]]["ece"],
                               lo=calib.interval(d)[0], hi=calib.interval(d)[1]))
    return ids


def save_predictions(design, fit_label, b, s, e, P, ests, fold=None):
    out = pd.DataFrame({"query_id": e["qid"], "rank": e["rank"], "label": e["y"]})
    for est, p in zip(ests, P):
        out[f"p_{est}"] = p
    if fold is not None:
        out["fold"] = fold
    name = f"{design}__{fit_label}__{b}__{s}.csv.gz"
    out.to_csv(EVAL_DIR / "predictions" / name, index=False,
               compression={"method": "gzip", "compresslevel": 6, "mtime": 0})


def evaluate_target(design, fit_label, fit_bs, b, s, e, P, ests, fold=None):
    save_predictions(design, fit_label, b, s, e, P, ests, fold)
    record(design, fit_label, fit_bs, b, s, e, P, ests, fold)
    if e["in_training"] is not None:
        record(design, fit_label, fit_bs, b, s, e, P, ests, fold, variant="heldout_rows")


def within_lake(data, b, s):
    e = data[b][s]
    n = len(e["y"])
    p_iso, p_feat, fold = np.empty(n), np.empty(n), np.empty(n, int)
    for f, (tr, te) in enumerate(GroupKFold(n_splits=5).split(e["X"], e["y"], e["qid"])):
        p_iso[te] = calib.IsoScore().fit(e["s"][tr], e["y"][tr]).predict(e["s"][te])
        p_feat[te] = calib.FeatureHGB().fit(e["X"][tr], e["y"][tr], e["group"][tr]).predict(e["X"][te])
        fold[te] = f
    evaluate_target("within_lake", "own_5fold", [b], b, s, e, [p_iso, p_feat], ["isotonic", "features"], fold)


def stratified(b, e, P):
    """LOO 'all' pool, PRIMARY: same-origin vs different-origin strata."""
    out = []
    variants = ["all"] + (["heldout_rows"] if e["in_training"] is not None else [])
    for variant in variants:
        base = np.ones(len(e["y"]), bool) if variant == "all" else e["in_training"] == 0
        for stratum, val in [("same_origin", 1), ("different_origin", 0)]:
            m = base & (e["same_origin"] == val)
            y, qid = e["y"][m], e["qid"][m]
            if m.sum() == 0:
                for est in EST:
                    out.append(dict(eval=b, eval_rows=variant, stratum=stratum, estimator=est, n_rows=0))
                continue
            rep = calib.bootstrap([p[m] for p in P], y, qid)
            for j, est in enumerate(EST):
                lo, hi = calib.interval(rep["ece"][j]); blo, bhi = calib.interval(rep["brier"][j])
                sid = len(STRAT_REPS)
                STRAT_REPS.append(pd.DataFrame({"strat_row_id": sid, "replicate": np.arange(calib.N_BOOT),
                                                "ece": rep["ece"][j], "brier": rep["brier"][j]}))
                out.append(dict(strat_row_id=sid, eval=b, eval_rows=variant, stratum=stratum, estimator=est, n_rows=int(m.sum()),
                                n_queries=int(len(np.unique(qid))), n_pos=int(y.sum()), pos_rate=float(y.mean()),
                                ece=calib.ece(P[j][m], y), ece_lo=lo, ece_hi=hi,
                                brier=calib.brier(P[j][m], y), brier_lo=blo, brier_hi=bhi))
    return out


def descriptives(data, b):
    out = []
    for s in SETS:
        e = data[b][s]
        variants = [("all", np.ones(len(e["y"]), bool))]
        if e["in_training"] is not None:
            variants.append(("heldout_rows", e["in_training"] == 0))
        for v, m in variants:
            y, sc = e["y"][m], e["s"][m]
            out.append(dict(benchmark=b, set=s, eval_rows=v, queries=int(len(np.unique(e["qid"][m]))),
                            rows=int(m.sum()), positives=int(y.sum()), pos_rate=float(y.mean()),
                            median_score_true=float(np.median(sc[y == 1])) if y.sum() else np.nan,
                            median_score_false=float(np.median(sc[y == 0])) if (y == 0).sum() else np.nan,
                            same_origin_share_of_positives=float(e["same_origin"][m][y == 1].mean()) if y.sum() else np.nan))
    return out


def summarize(pairs):
    shared = {b for b in BENCHMARKS if BENCHMARKS[b]["shared_origin"]}
    out = []

    def add(design, variant, fbm_rows, sub, s, est, unit):
        r = sub[(sub["set"] == s) & (sub["estimator"] == est)]
        base = dict(design=design, shared_origin_variant=variant, fbm_rows=fbm_rows, set=s, estimator=est, unit=unit)
        if len(r) == 0 or r["ece"].isna().all():
            out.append({**base, "n": 0, "note": "no unseen benchmark remains"})
        else:
            r = r.dropna(subset=["ece"])
            out.append({**base, "n": len(r), "ece_median": r.ece.median(), "ece_min": r.ece.min(),
                        "ece_max": r.ece.max(), "brier_median": r.brier.median(), "brier_min": r.brier.min(),
                        "brier_max": r.brier.max(), "note": ""})

    for fbm_rows in ["all", "heldout_rows"]:
        p = pairs[(pairs["eval"] != "freyja_bm") | (pairs["eval_rows"] == fbm_rows)]
        for s in SETS:
            for est in EST:
                loo = p[p.design == "leave_one_out"]
                for variant, pool, cond in [
                    ("all", "all", lambda r: r),
                    ("excluded_as_fitting", "no_shared_origin", lambda r: r),
                    ("excluded_as_evaluation", "all", lambda r: r[~r["eval"].isin(shared)]),
                    ("excluded_as_both", "no_shared_origin", lambda r: r[~r["eval"].isin(shared)]),
                    ("all [pool without FREYJA_BM]", "no_freyja_bm", lambda r: r),
                    ("excluded_as_evaluation [pool without FREYJA_BM]", "no_freyja_bm", lambda r: r[~r["eval"].isin(shared)]),
                ]:
                    add("leave_one_out", variant, fbm_rows, cond(loo[loo.fit == pool]), s, est, "held-out benchmark")
                pw = p[p.design == "pairwise"]
                fit_b = pw.fit_benchmarks
                for variant, sub in [("all", pw), ("excluded_as_fitting", pw[~fit_b.isin(shared)]),
                                     ("excluded_as_evaluation", pw[~pw["eval"].isin(shared)]),
                                     ("excluded_as_both", pw[~fit_b.isin(shared) & ~pw["eval"].isin(shared)])]:
                    add("pairwise", variant, fbm_rows, sub, s, est, "ordered pair")
                wl = p[p.design == "within_lake"]
                if est != "raw":
                    for variant, sub in [("all", wl), ("excluded_as_evaluation", wl[~wl["eval"].isin(shared)])]:
                        add("within_lake", variant, fbm_rows, sub, s, est, "benchmark")
    return pd.DataFrame(out)


def fmt(r):
    return f"{r.ece:.3f} [{r.ece_lo:.3f}, {r.ece_hi:.3f}]"


def print_loo_table(pairs):
    p = pairs[(pairs.set == "PRIMARY")]
    lines = ["Leave-one-out, PRIMARY, pool 'all': ECE [95% CI]; within-lake reference last",
             f"{'held-out':28s} {'(a) raw':24s} {'(b) isotonic':24s} {'(c) features':24s} {'within (b)':24s} {'within (c)':24s}"]
    for b in ORDER:
        for v in ["all", "heldout_rows"]:
            r = p[(p["eval"] == b) & (p.eval_rows == v)]
            if len(r) == 0:
                continue
            cells = []
            for design, fit, est in [("leave_one_out", "all", "raw"), ("leave_one_out", "all", "isotonic"),
                                     ("leave_one_out", "all", "features"), ("within_lake", "own_5fold", "isotonic"),
                                     ("within_lake", "own_5fold", "features")]:
                x = r[(r.design == design) & (r.fit == fit) & (r.estimator == est)]
                cells.append(fmt(x.iloc[0]) if len(x) and pd.notna(x.iloc[0].ece) else "n/a")
            label = BENCHMARKS[b]["name"] + (" (held-out rows)" if v == "heldout_rows" else "")
            lines.append(f"{label:28s} " + " ".join(f"{c:24s}" for c in cells))
    txt = "\n".join(lines)
    print(txt)
    (RES / "leave_one_out_primary_table.txt").write_text(txt + "\n")


def main():
    t0 = time.time()
    present = [b for b in ORDER if pairs_path(b).exists()]
    print("benchmarks:", present, flush=True)
    if (EVAL_DIR / "predictions").exists():
        shutil.rmtree(EVAL_DIR / "predictions")
    (EVAL_DIR / "predictions").mkdir(parents=True)
    RES.mkdir(exist_ok=True)
    data = {b: load(b) for b in present}
    fits = Fits(data)
    shared = {b for b in present if BENCHMARKS[b]["shared_origin"]}
    strat = []
    for s in SETS:
        print(f"== {s}", flush=True)
        for b in present:
            print(f"  within-lake {b}", flush=True)
            within_lake(data, b, s)
        for a, b in itertools.permutations(present, 2):
            evaluate_target("pairwise", a, [a], b, s, data[b][s], predict(fits.get([a], s), data[b][s]), EST)
        for b in present:
            others = [x for x in present if x != b]
            pools = {"all": others, "no_freyja_bm": [x for x in others if x != "freyja_bm"],
                     "no_shared_origin": [x for x in others if x not in shared]}
            for pool, fit_bs in pools.items():
                e = data[b][s]
                if not fit_bs:
                    for v in ["all"] + (["heldout_rows"] if e["in_training"] is not None else []):
                        for est in EST:
                            ROWS.append(dict(row_id=len(ROWS), design="leave_one_out", fit=pool, fit_benchmarks="",
                                             eval=b, set=s, eval_rows=v, estimator=est, n_rows=0,
                                             note="no fitting data"))
                    continue
                P = predict(fits.get(fit_bs, s), e)
                evaluate_target("leave_one_out", pool, fit_bs, b, s, e, P, EST)
                if pool == "all" and s == "PRIMARY":
                    strat += stratified(b, e, P)
    pairs = pd.DataFrame(ROWS)
    pairs.to_csv(RES / "pairs.csv", index=False)
    pairs[pairs.design == "leave_one_out"].to_csv(RES / "leave_one_out.csv", index=False)
    pairs[pairs.design == "within_lake"].to_csv(RES / "within_lake.csv", index=False)
    pd.DataFrame(PAIRED).to_csv(RES / "paired_differences.csv", index=False)
    pd.DataFrame(strat).to_csv(RES / "stratified.csv", index=False)
    pd.DataFrame([r for b in present for r in descriptives(data, b)]).to_csv(RES / "descriptives.csv", index=False)
    summarize(pairs).to_csv(RES / "summary.csv", index=False)
    pd.concat(REPS, ignore_index=True).to_csv(EVAL_DIR / "replicates.csv.gz", index=False,
                                              compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    if STRAT_REPS:
        pd.concat(STRAT_REPS, ignore_index=True).to_csv(EVAL_DIR / "replicates_stratified.csv.gz", index=False,
                                                        compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    (EVAL_DIR / "run_meta.json").write_text(json.dumps({"benchmarks": present, "seconds": time.time() - t0}))
    print_loo_table(pairs)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
