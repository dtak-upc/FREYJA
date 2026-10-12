"""Export raw data per benchmark, after verification (protocol step 8).

Refuses to write anything unless all of the following hold:
 1. Pair files: rebuilding every pair file from the exported normalized
    profiles (typed JSON Lines), the GT file and the model's training pairs,
    with FREYJA's feature code and the model, reproduces every row and every
    column exactly (completeness, query ids, labels, ranks, PRIMARY flag,
    same-origin and in-training flags, 22 features, scores).
 2. Predictions: every prediction file covers exactly the rows of its set, in
    canonical order, with the same labels; within-lake folds partition the
    queries.
 3. Metrics: from the exported predictions, n_rows, n_queries, n_pos, pos_rate,
    ECE and Brier of every row of results/pairs.csv and results/stratified.csv
    are reproduced exactly; a row with rows but no ECE is a failure.
 4. Intervals: the percentiles of the exported replicates reproduce every
    interval exactly, and the replicates themselves are recomputed from the
    predictions, the query ids and the seed (all 1000 for PRIMARY rows, the
    first 100 for SECONDARY rows) and match exactly.
 5. Derived tables: paired_differences.csv, descriptives.csv and summary.csv
    are recomputed and match.
 6. The exported copies have the same sha256 as the files verified, and no
    source file changed during verification.

Output: SCRATCH/export/ (see calibration/DATA.md) + export/MANIFEST.csv (sha256).
Usage: python -I export.py
"""
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import calib  # noqa: E402
from benchmarks import BENCHMARKS, CAL, FREYJA, ORDER, SCRATCH, origin, pairs_path, profiles_dir  # noqa: E402
from freyja_score import features_for_query, load_model, score  # noqa: E402
from score_benchmark import load_gt, training_pairs  # noqa: E402

sys.path.insert(0, str(FREYJA))
from app.core.profiling.profiler import DataProfiler  # noqa: E402

EXPORT = SCRATCH / "export"
EVAL = SCRATCH / "eval"
LIST_COLS = ["freq_word_containment", "freq_word_soundex_containment"]
PROFILE_FILES = ["profiles_raw.csv", "profiles_normalized.csv", "profiles_normalized.pkl", "profiles_raw.pkl",
                 "profile_meta.json", "profile_errors.json", "profile_per_table.csv"]
FAIL = []


def fail(msg):
    FAIL.append(msg)
    print("FAIL:", msg, flush=True)


# ---------- typed JSON for profile values (Python types matter: 1 == 1.0 == True) ----------
def enc(v):
    if isinstance(v, (bool, np.bool_)):
        return {"bool": bool(v)}
    if isinstance(v, (int, np.integer)):
        return {"int": int(v)}
    if isinstance(v, (float, np.floating)):
        return {"float": repr(float(v))}
    if isinstance(v, dt.datetime):
        return {"datetime": v.isoformat()}
    if isinstance(v, dt.date):
        return {"date": v.isoformat()}
    if isinstance(v, str):
        return {"str": v}
    if v is None:
        return {"none": None}
    raise TypeError(f"unsupported profile value type {type(v)}")


def dec(d):
    (t, v), = d.items()
    return {"bool": lambda x: x, "int": int, "float": float, "datetime": dt.datetime.fromisoformat,
            "date": dt.date.fromisoformat, "str": str, "none": lambda x: None}[t](v)


def write_jsonl(norm, path):
    with open(path, "w") as f:
        for rec in norm.to_dict("records"):
            out = {k: ([enc(x) for x in v] if k in LIST_COLS else enc(v)) for k, v in rec.items()}
            f.write(json.dumps(out, ensure_ascii=False) + "\n")


def read_jsonl(path):
    recs = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            recs.append({k: ([dec(x) for x in v] if k in LIST_COLS else dec(v)) for k, v in r.items()})
    return pd.DataFrame(recs)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- 1. rebuild pair files ----------
def rebuild_pairs(b, prof, model):
    """Second implementation of PREREGISTRATION.md §2-§3 from exported profiles."""
    cfg = BENCHMARKS[b]
    feats = list(model.feature_names_in_)
    g, _ = load_gt(cfg)
    queries = sorted(set(zip(g.target_ds, g.target_attr)))
    nonself = g[(g.target_ds != g.candidate_ds) | (g.target_attr != g.candidate_attr)]
    pos = set(zip(nonself.target_ds, nonself.target_attr, nonself.candidate_ds, nonself.candidate_attr))
    train = training_pairs() if b == "freyja_bm" else None
    ds, at = prof.dataset_name.to_numpy(), prof.attribute_name.to_numpy()
    first = {}
    for i, k in enumerate(zip(ds, at)):
        first.setdefault(k, i)
    frames = []
    for qid, q in enumerate(queries):
        if q not in first:
            continue
        qi = first[q]
        f = features_for_query(prof, qi, feats)
        s = score(model, f)
        idx = np.arange(len(prof))
        cand = idx[idx != qi]
        cand = cand[np.lexsort((cand, -s[cand]))]
        out = pd.DataFrame({"query_id": qid, "query_ds": q[0], "query_attr": q[1], "cand_ds": ds[cand],
                            "cand_attr": at[cand]})
        for c in feats:
            out[c] = f[c].to_numpy()[cand]
        out["score"] = s[cand]
        out["label"] = [int((q[0], q[1], ds[i], at[i]) in pos) for i in cand]
        out["rank"] = np.arange(1, len(cand) + 1)
        out["primary"] = (out["rank"] <= cfg["k"]).astype(int)
        qo = origin(b, q[0])
        out["same_origin"] = [int(origin(b, ds[i]) == qo) for i in cand]
        if train is not None:
            out["in_training"] = [int(frozenset([q, (ds[i], at[i])]) in train) for i in cand]
        frames.append(out)
    return pd.concat(frames, ignore_index=True)


def read_pairs(b):
    return pd.read_csv(pairs_path(b), float_precision="round_trip", keep_default_na=False,
                       dtype={"query_ds": str, "query_attr": str, "cand_ds": str, "cand_attr": str})


def check_pairs(b, rebuilt, stored):
    if list(rebuilt.columns) != list(stored.columns):
        fail(f"{b}: pair file columns differ: {list(stored.columns)} vs {list(rebuilt.columns)}")
        return
    if len(rebuilt) != len(stored):
        fail(f"{b}: pair file has {len(stored)} rows, rebuild has {len(rebuilt)}")
        return
    for c in stored.columns:
        a, r = stored[c].to_numpy(), rebuilt[c].to_numpy()
        eq = (a == r) if a.dtype.kind in "fiub" and r.dtype.kind in "fiub" else (a.astype(str) == r.astype(str))
        if not eq.all():
            fail(f"{b}: column {c}: {int((~eq).sum())} mismatching rows")


# ---------- 2-5. predictions and metrics ----------
_PRED = {}


def read_pred(name):
    if name not in _PRED:
        _PRED.clear()
        _PRED[name] = pd.read_csv(EVAL / "predictions" / name, float_precision="round_trip")
    return _PRED[name]


def check_metrics(res, reps, strat, sreps, pairs_of):
    checked_files = set()
    rep_g, srep_g = reps.groupby("row_id"), sreps.groupby("strat_row_id")

    def verify(tag, d, m, est, r, rr, prim):
        p, y, q = d[f"p_{est}"].to_numpy()[m], d["label"].to_numpy()[m], d["query_id"].to_numpy()[m]
        got = dict(n_rows=int(m.sum()), n_queries=int(len(np.unique(q))), n_pos=int(y.sum()),
                   pos_rate=float(y.mean()), ece=calib.ece(p, y), brier=calib.brier(p, y))
        for k, v in got.items():
            if v != getattr(r, k):
                fail(f"{tag}: {k} {getattr(r, k)} != recomputed {v}")
        if calib.interval(rr.ece.to_numpy()) != (r.ece_lo, r.ece_hi) or \
                calib.interval(rr.brier.to_numpy()) != (r.brier_lo, r.brier_hi):
            fail(f"{tag}: interval not reproduced by stored replicates")
        which = list(range(calib.N_BOOT)) if prim else list(range(100))
        rec = calib.bootstrap([p], y, q, which=which)
        stored_e = rr.sort_values("replicate").ece.to_numpy()[which]
        stored_b = rr.sort_values("replicate").brier.to_numpy()[which]
        if not (np.array_equal(rec["ece"][0, which], stored_e) and np.array_equal(rec["brier"][0, which], stored_b)):
            fail(f"{tag}: stored replicates differ from recomputed replicates")

    for r in res.itertuples():
        if r.n_rows == 0:
            if pd.isna(getattr(r, "note", np.nan)):
                fail(f"row {r.row_id}: zero rows without a note")
            continue
        if pd.isna(r.ece):
            fail(f"row {r.row_id}: has rows but no ECE")
            continue
        name = f"{r.design}__{r.fit}__{r.eval}__{r.set}.csv.gz"
        d = read_pred(name)
        pr = pairs_of(r.eval)
        sel = pr[pr.primary == 1] if r.set == "PRIMARY" else pr
        if name not in checked_files:
            checked_files.add(name)
            if not (len(d) == len(sel) and np.array_equal(d.query_id.to_numpy(), sel.query_id.to_numpy())
                    and np.array_equal(d["rank"].to_numpy(), sel["rank"].to_numpy())
                    and np.array_equal(d.label.to_numpy(), sel.label.to_numpy())):
                fail(f"{name}: rows differ from the pair file's {r.set} rows")
            if "fold" in d and d.groupby("query_id").fold.nunique().max() != 1:
                fail(f"{name}: a query spans several folds")
        m = np.ones(len(d), bool) if r.eval_rows == "all" else sel.in_training.to_numpy() == 0
        verify(f"row {r.row_id} ({name}, {r.eval_rows}, {r.estimator})", d, m, r.estimator, r,
               rep_g.get_group(r.row_id), r.set == "PRIMARY")
    for r in strat.itertuples():
        if r.n_rows == 0:
            continue
        if pd.isna(r.ece):
            fail(f"stratified row {r.strat_row_id}: has rows but no ECE")
            continue
        d = read_pred(f"leave_one_out__all__{r.eval}__PRIMARY.csv.gz")
        sel = pairs_of(r.eval)
        sel = sel[sel.primary == 1]
        m = sel.same_origin.to_numpy() == (1 if r.stratum == "same_origin" else 0)
        if r.eval_rows == "heldout_rows":
            m &= sel.in_training.to_numpy() == 0
        verify(f"stratified row {r.strat_row_id}", d, m, r.estimator, r, srep_g.get_group(r.strat_row_id), True)


def check_derived(res, reps, pairs_of, present):
    import evaluate  # summary and descriptives logic, applied to the exported tables
    paired = pd.read_csv(CAL / "results/paired_differences.csv", float_precision="round_trip")
    rep_g = reps.groupby("row_id")
    for r in paired.itertuples():
        a_, b_ = r.contrast[len("ece_"):].split("_minus_")
        sub = res[(res.design == r.design) & (res.fit == r.fit) & (res["eval"] == r.eval) & (res.set == r.set)
                  & (res.eval_rows == r.eval_rows)]
        ra, rb = sub[sub.estimator == a_].iloc[0], sub[sub.estimator == b_].iloc[0]
        diff = rep_g.get_group(ra.row_id).sort_values("replicate").ece.to_numpy() - \
            rep_g.get_group(rb.row_id).sort_values("replicate").ece.to_numpy()
        if ra.ece - rb.ece != r.diff or calib.interval(diff) != (r.lo, r.hi):
            fail(f"paired difference {r.Index} not reproduced")
    desc = pd.read_csv(CAL / "results/descriptives.csv", float_precision="round_trip")
    for b in present:
        pr = pairs_of(b)
        for s in ["PRIMARY", "SECONDARY"]:
            sel = pr[pr.primary == 1] if s == "PRIMARY" else pr
            variants = [("all", np.ones(len(sel), bool))]
            if "in_training" in sel:
                variants.append(("heldout_rows", sel.in_training.to_numpy() == 0))
            for v, m in variants:
                row = desc[(desc.benchmark == b) & (desc.set == s) & (desc.eval_rows == v)].iloc[0]
                y, sc = sel.label.to_numpy()[m], sel.score.to_numpy()[m]
                got = dict(rows=int(m.sum()), positives=int(y.sum()), pos_rate=float(y.mean()),
                           queries=int(sel.query_id[m].nunique()),
                           median_score_true=float(np.median(sc[y == 1])),
                           median_score_false=float(np.median(sc[y == 0])),
                           same_origin_share_of_positives=float(sel.same_origin.to_numpy()[m][y == 1].mean()))
                for k, val in got.items():
                    if val != row[k]:
                        fail(f"descriptives {b} {s} {v}: {k} {row[k]} != {val}")
    summ = pd.read_csv(CAL / "results/summary.csv", float_precision="round_trip")
    again = evaluate.summarize(res)
    num = [c for c in summ.columns if summ[c].dtype.kind == "f"]
    if len(summ) != len(again) or not all(
            np.array_equal(summ[c].to_numpy(), again[c].to_numpy(), equal_nan=True) for c in num):
        fail("summary.csv not reproduced from pairs.csv")


def main():
    model = load_model()
    present = [b for b in ORDER if pairs_path(b).exists()]
    sources = [CAL / "results" / f.name for f in sorted((CAL / "results").glob("*")) if f.name != "export_manifest.csv"]
    sources += [EVAL / "replicates.csv.gz", EVAL / "replicates_stratified.csv.gz"]
    sources += sorted((EVAL / "predictions").glob("*.csv.gz"))
    for b in present:
        sources += [profiles_dir(b) / n for n in PROFILE_FILES] + [pairs_path(b), SCRATCH / b / "score_meta.json"]
    before = {p: sha256(p) for p in sources}
    staging = SCRATCH / "export_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    pairs_cache = {}
    for b in present:
        (staging / b).mkdir()
        raw = pd.read_pickle(profiles_dir(b) / "profiles_raw.pkl")
        norm = DataProfiler.normalize_profiles(raw).round(6)   # the call made by profile_lake.py
        if list(norm.columns) != list(pd.read_csv(profiles_dir(b) / "profiles_normalized.csv", nrows=1).columns):
            fail(f"{b}: normalized columns differ from profiles_normalized.csv")
        write_jsonl(norm, staging / b / "profiles_normalized.jsonl")
        prof = DataProfiler.preprocess_profiles(read_jsonl(staging / b / "profiles_normalized.jsonl"))
        stored = read_pairs(b)
        check_pairs(b, rebuild_pairs(b, prof, model), stored)
        pairs_cache[b] = stored
        print(f"{b}: pair file checked ({len(stored)} rows)", flush=True)
    res = pd.read_csv(CAL / "results/pairs.csv", float_precision="round_trip")
    strat = pd.read_csv(CAL / "results/stratified.csv", float_precision="round_trip")
    reps = pd.read_csv(EVAL / "replicates.csv.gz", float_precision="round_trip")
    sreps = pd.read_csv(EVAL / "replicates_stratified.csv.gz", float_precision="round_trip")
    check_metrics(res, reps, strat, sreps, pairs_cache.__getitem__)
    print("metrics checked", flush=True)
    check_derived(res, reps, pairs_cache.__getitem__, present)
    print("derived tables checked", flush=True)
    changed = [str(p) for p in sources if sha256(p) != before[p]]
    if changed:
        fail(f"source files changed during verification: {changed[:5]}")
    if FAIL:
        print(f"REFUSING TO EXPORT: {len(FAIL)} failures")
        sys.exit(1)
    print("all checks passed; writing export", flush=True)

    if EXPORT.exists():
        shutil.rmtree(EXPORT)
    staging.rename(EXPORT)
    copied = {}
    for b in present:
        o = EXPORT / b
        for name in PROFILE_FILES:
            copied[o / name] = profiles_dir(b) / name
        copied[o / "pairs.csv.gz"] = pairs_path(b)
        copied[o / "score_meta.json"] = SCRATCH / b / "score_meta.json"
        (o / "predictions").mkdir()
        for f in (EVAL / "predictions").glob(f"*__{b}__*.csv.gz"):
            copied[o / "predictions" / f.name] = f
        for dst, src in list(copied.items()):
            if dst.parent in (o, o / "predictions") and not dst.exists():
                shutil.copy2(src, dst)
        ids = set(res.loc[res["eval"] == b, "row_id"])
        reps[reps.row_id.isin(ids)].to_csv(o / "replicates.csv.gz", index=False,
                                           compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
        sids = set(strat.loc[strat["eval"] == b, "strat_row_id"].dropna().astype(int))
        sreps[sreps.strat_row_id.isin(sids)].to_csv(o / "replicates_stratified.csv.gz", index=False,
                                                    compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    (EXPORT / "results").mkdir()
    for f in sources:
        if f.parent == CAL / "results":
            shutil.copy2(f, EXPORT / "results" / f.name)
            copied[EXPORT / "results" / f.name] = f
    bad = [str(d) for d, s in copied.items() if sha256(d) != before[s]]
    if bad:
        print("EXPORTED COPIES DIFFER FROM VERIFIED FILES:", bad[:5])
        shutil.rmtree(EXPORT)
        sys.exit(1)
    (EXPORT / "verification.json").write_text(json.dumps({
        "benchmarks": present, "pair_rows_checked": {b: len(v) for b, v in pairs_cache.items()},
        "metric_rows_checked": int((res.n_rows > 0).sum()), "stratified_rows_checked": int((strat.n_rows > 0).sum()),
        "replicates_recomputed": "all 1000 for PRIMARY rows, replicates 0-99 for SECONDARY rows",
        "failures": 0}, indent=1))
    rows = [dict(path=str(p.relative_to(EXPORT)), bytes=p.stat().st_size, sha256=sha256(p))
            for p in sorted(EXPORT.rglob("*")) if p.is_file()]
    pd.DataFrame(rows).to_csv(EXPORT / "MANIFEST.csv", index=False)
    pd.DataFrame(rows).to_csv(CAL / "results/export_manifest.csv", index=False)
    print(f"exported {len(rows)} files, {sum(r['bytes'] for r in rows) / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
