"""Export raw data per benchmark, after verification (protocol step 8).

Refuses to write anything unless
 1. recomputing the 22 features from the exported normalized profiles
    (typed JSON Lines) with FREYJA's code and running the model reproduces
    every feature and every score of the pair file exactly;
 2. recomputing ECE and Brier from the exported predictions reproduces every
    value in results/pairs.csv and results/stratified.csv exactly;
 3. the 2.5/97.5 percentiles of the exported bootstrap replicates reproduce
    every interval exactly.

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
from benchmarks import BENCHMARKS, CAL, FREYJA, ORDER, SCRATCH, pairs_path, profiles_dir  # noqa: E402
from freyja_score import features_for_query, load_model, score  # noqa: E402

sys.path.insert(0, str(FREYJA))
from app.core.profiling.profiler import DataProfiler  # noqa: E402

EXPORT = SCRATCH / "export"
EVAL = SCRATCH / "eval"
LIST_COLS = ["freq_word_containment", "freq_word_soundex_containment"]
OBJ_COLS = ["dataset_name", "attribute_name", "first_word", "last_word"]


# ---------- typed JSON for profile values (Python types matter: 1 == 1.0 == True) ----------
def enc(v):
    if isinstance(v, bool):
        return {"bool": v}
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
            out = {}
            for k, v in rec.items():
                if k in LIST_COLS:
                    out[k] = [enc(x) for x in v]
                else:
                    out[k] = enc(v.item() if isinstance(v, np.generic) else v)
            f.write(json.dumps(out, ensure_ascii=False) + "\n")


def read_jsonl(path):
    recs = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            recs.append({k: ([dec(x) for x in v] if k in LIST_COLS else dec(v)) for k, v in r.items()})
    return pd.DataFrame(recs)


# ---------- checks ----------
def check_scores(b, jsonl_path, model):
    prof = DataProfiler.preprocess_profiles(read_jsonl(jsonl_path))
    pairs = pd.read_csv(pairs_path(b), float_precision="round_trip", keep_default_na=False,
                        dtype={"query_ds": str, "query_attr": str, "cand_ds": str, "cand_attr": str})
    feats = list(model.feature_names_in_)
    row_of = {}
    for i, k in enumerate(zip(prof.dataset_name, prof.attribute_name)):
        row_of.setdefault(k, i)
    n_bad_f = n_bad_s = 0
    for (qd, qa), g in pairs.groupby(["query_ds", "query_attr"], sort=False):
        f = features_for_query(prof, row_of[(qd, qa)], feats)
        idx = [row_of[k] for k in zip(g.cand_ds, g.cand_attr)]
        fr = f.iloc[idx]
        n_bad_f += int((fr.to_numpy(float) != g[feats].to_numpy(float)).sum())
        n_bad_s += int((score(model, fr) != g["score"].to_numpy(float)).sum())
    return dict(rows=len(pairs), feature_mismatches=n_bad_f, score_mismatches=n_bad_s)


_PRED = {}


def read_pred(name):
    """Prediction file, keeping only the most recently used one in memory."""
    if name not in _PRED:
        _PRED.clear()
        _PRED[name] = pd.read_csv(EVAL / "predictions" / name, float_precision="round_trip")
    return _PRED[name]


def check_metrics(res, reps, strat, strat_reps, pairs_cache):
    bad = []
    rep_g = reps.groupby("row_id")
    for r in res.itertuples():
        if r.n_rows == 0 or pd.isna(getattr(r, "ece", np.nan)):
            continue
        d = read_pred(f"{r.design}__{r.fit}__{r.eval}__{r.set}.csv.gz")
        if r.eval_rows == "heldout_rows":
            tr = pairs_cache(r.eval).set_index(["query_id", "rank"])["in_training"]
            d = d[tr.loc[list(zip(d.query_id, d["rank"]))].to_numpy() == 0]
        p, y = d[f"p_{r.estimator}"].to_numpy(), d["label"].to_numpy()
        rr = rep_g.get_group(r.row_id)
        checks = [calib.ece(p, y) == r.ece, calib.brier(p, y) == r.brier,
                  calib.interval(rr.ece.to_numpy()) == (r.ece_lo, r.ece_hi),
                  calib.interval(rr.brier.to_numpy()) == (r.brier_lo, r.brier_hi), len(d) == r.n_rows]
        if not all(checks):
            bad.append((r.row_id, checks))
    srep_g = strat_reps.groupby("strat_row_id")
    for r in strat.itertuples():
        if r.n_rows == 0:
            continue
        d = read_pred(f"leave_one_out__all__{r.eval}__PRIMARY.csv.gz")
        pr = pairs_cache(r.eval).set_index(["query_id", "rank"])
        key = list(zip(d.query_id, d["rank"]))
        m = pr["same_origin"].loc[key].to_numpy() == (1 if r.stratum == "same_origin" else 0)
        if r.eval_rows == "heldout_rows":
            m &= pr["in_training"].loc[key].to_numpy() == 0
        p, y = d[f"p_{r.estimator}"].to_numpy()[m], d["label"].to_numpy()[m]
        rr = srep_g.get_group(r.strat_row_id)
        checks = [calib.ece(p, y) == r.ece, calib.brier(p, y) == r.brier,
                  calib.interval(rr.ece.to_numpy()) == (r.ece_lo, r.ece_hi),
                  calib.interval(rr.brier.to_numpy()) == (r.brier_lo, r.brier_hi)]
        if not all(checks):
            bad.append(("strat", r.strat_row_id, checks))
    return bad


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    model = load_model()
    present = [b for b in ORDER if pairs_path(b).exists()]
    staging = SCRATCH / "export_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    report = {}
    for b in present:
        (staging / b).mkdir()
        norm = pd.read_csv(profiles_dir(b) / "profiles_normalized.csv")  # only to get column order
        pkl = pd.read_pickle(profiles_dir(b) / "profiles_raw.pkl")
        exact_norm = DataProfiler.normalize_profiles(pkl).round(6)       # same call as profile_lake.py
        assert list(exact_norm.columns) == list(norm.columns)
        write_jsonl(exact_norm, staging / b / "profiles_normalized.jsonl")
        report[b] = check_scores(b, staging / b / "profiles_normalized.jsonl", model)
        print(b, report[b], flush=True)
    res = pd.read_csv(CAL / "results/pairs.csv", float_precision="round_trip")
    strat = pd.read_csv(CAL / "results/stratified.csv", float_precision="round_trip")
    reps = pd.read_csv(EVAL / "replicates.csv.gz", float_precision="round_trip")
    sreps = pd.read_csv(EVAL / "replicates_stratified.csv.gz", float_precision="round_trip")
    cache = {}

    def pairs_cache(b):
        if b not in cache:
            cache[b] = pd.read_csv(pairs_path(b), usecols=lambda c: c in
                                   ("query_id", "rank", "in_training", "same_origin"))
        return cache[b]

    bad = check_metrics(res, reps, strat, sreps, pairs_cache)
    fails = {b: r for b, r in report.items() if r["feature_mismatches"] or r["score_mismatches"]}
    if fails or bad:
        print("REFUSING TO EXPORT. score failures:", fails, "metric failures:", bad[:20], f"({len(bad)} total)")
        sys.exit(1)
    print("all checks passed; writing export", flush=True)

    if EXPORT.exists():
        shutil.rmtree(EXPORT)
    staging.rename(EXPORT)
    for b in present:
        o = EXPORT / b
        for name in ["profiles_raw.csv", "profiles_normalized.csv", "profiles_normalized.pkl", "profiles_raw.pkl",
                     "profile_meta.json", "profile_errors.json", "profile_per_table.csv"]:
            shutil.copy2(profiles_dir(b) / name, o / name)
        shutil.copy2(pairs_path(b), o / "pairs.csv.gz")
        shutil.copy2(SCRATCH / b / "score_meta.json", o / "score_meta.json")
        (o / "predictions").mkdir()
        for f in (EVAL / "predictions").glob(f"*__{b}__*.csv.gz"):
            shutil.copy2(f, o / "predictions" / f.name)
        ids = set(res.loc[res["eval"] == b, "row_id"])
        reps[reps.row_id.isin(ids)].to_csv(o / "replicates.csv.gz", index=False,
                                           compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
        sids = set(strat.loc[strat["eval"] == b, "strat_row_id"].dropna().astype(int))
        sreps[sreps.strat_row_id.isin(sids)].to_csv(o / "replicates_stratified.csv.gz", index=False,
                                                    compression={"method": "gzip", "compresslevel": 6, "mtime": 0})
    (EXPORT / "results").mkdir()
    for f in (CAL / "results").glob("*"):
        shutil.copy2(f, EXPORT / "results" / f.name)
    (EXPORT / "verification.json").write_text(json.dumps({"scores": report, "metric_rows_checked": len(res),
                                                          "stratified_rows_checked": len(strat),
                                                          "metric_failures": 0}, indent=1))
    rows = [dict(path=str(p.relative_to(EXPORT)), bytes=p.stat().st_size, sha256=sha256(p))
            for p in sorted(EXPORT.rglob("*")) if p.is_file()]
    pd.DataFrame(rows).to_csv(EXPORT / "MANIFEST.csv", index=False)
    pd.DataFrame(rows).to_csv(CAL / "results/export_manifest.csv", index=False)
    print(f"exported {len(rows)} files, {sum(r['bytes'] for r in rows) / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
