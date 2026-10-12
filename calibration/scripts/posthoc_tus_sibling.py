"""POST-HOC, not pre-registered. Added after the code review found that TUS Big's
lake contains almost all of TUS Small's tables (same file names, same bytes).
The pre-registered leave-one-out pools `all` and `no_freyja_bm` for TUS Small
therefore contain TUS Big (and vice versa), so those rows are close to
within-lake. This script (1) measures the overlap and (2) reruns leave-one-out
for TUS Small and TUS Big with the sibling TUS lake also removed from the pool
(pool = all other benchmarks except the sibling). Same estimators, metrics,
bootstrap and seed as the pre-registered analysis. Never used in summaries.

Writes calibration/results/posthoc_tus_overlap.json and posthoc_tus_sibling.csv.
Usage: python -I posthoc_tus_sibling.py
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import calib  # noqa: E402
import evaluate as ev  # noqa: E402
from benchmarks import BENCHMARKS, CAL, GT_DIR, ORDER, pairs_path, strip_csv  # noqa: E402


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def overlap():
    small, big = BENCHMARKS["tus_small"]["lake"], BENCHMARKS["tus_big"]["lake"]
    s_files = {p.name for p in small.glob("*.csv")}
    b_files = {p.name for p in big.glob("*.csv")}
    common = sorted(s_files & b_files)
    identical = sum(md5(small / f) == md5(big / f) for f in common)
    gs = pd.read_csv(GT_DIR / BENCHMARKS["tus_small"]["gt"], dtype=str, keep_default_na=False)
    gb = pd.read_csv(GT_DIR / BENCHMARKS["tus_big"]["gt"], dtype=str, keep_default_na=False)
    ts = set(gs.target_ds) | set(gs.candidate_ds)
    tb = set(gb.target_ds) | set(gb.candidate_ds)
    ps = pd.read_csv(pairs_path("tus_small"), usecols=["query_ds", "query_attr", "cand_ds", "cand_attr", "label"],
                     dtype=str, keep_default_na=False)
    pb_cols = pd.read_pickle(ev.SCRATCH / "tus_big/profiles/profiles_normalized.pkl")[["dataset_name", "attribute_name"]]
    big_cols = set(zip(pb_cols.dataset_name, pb_cols.attribute_name))
    small_cols = {(strip_csv(a), b) for a, b in zip(ps.cand_ds, ps.cand_attr)} | \
                 {(strip_csv(a), b) for a, b in zip(ps.query_ds, ps.query_attr)}
    out = {"tus_small_lake_files": len(s_files), "tus_big_lake_files": len(b_files),
           "same_file_name": len(common), "same_name_and_identical_bytes": identical,
           "tus_small_profiled_columns_also_in_tus_big_profiles": len(small_cols & big_cols),
           "tus_small_profiled_columns": len(small_cols),
           "gt_tables_tus_small": len(ts), "gt_tables_tus_small_also_in_tus_big_gt": len(ts & tb),
           "gt_queries_common": len(set(zip(gs.target_ds, gs.target_attr)) & set(zip(gb.target_ds, gb.target_attr)))}
    (CAL / "results/posthoc_tus_overlap.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def rerun():
    present = [b for b in ORDER if pairs_path(b).exists()]
    data = {b: ev.load(b) for b in present}
    fits = ev.Fits(data)
    rows = []
    for b, sib in [("tus_small", "tus_big"), ("tus_big", "tus_small")]:
        pool = [x for x in present if x not in (b, sib)]
        for s in ev.SETS:
            e = data[b][s]
            P = ev.predict(fits.get(pool, s), e)
            rep = calib.bootstrap(P, e["y"], e["qid"])
            for j, est in enumerate(ev.EST):
                lo, hi = calib.interval(rep["ece"][j]); blo, bhi = calib.interval(rep["brier"][j])
                rows.append(dict(analysis="POST-HOC leave-one-out, pool = all other benchmarks minus the sibling TUS lake",
                                 eval=b, set=s, fit_benchmarks="+".join(pool), estimator=est,
                                 n_rows=len(e["y"]), n_queries=len(np.unique(e["qid"])), pos_rate=float(e["y"].mean()),
                                 ece=calib.ece(P[j], e["y"]), ece_lo=lo, ece_hi=hi,
                                 brier=calib.brier(P[j], e["y"]), brier_lo=blo, brier_hi=bhi))
    df = pd.DataFrame(rows)
    df.to_csv(CAL / "results/posthoc_tus_sibling.csv", index=False)
    print(df[["eval", "set", "estimator", "ece", "ece_lo", "ece_hi"]].to_string(index=False))


if __name__ == "__main__":
    overlap()
    rerun()
