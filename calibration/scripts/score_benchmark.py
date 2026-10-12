"""Score every (query, candidate) pair of one benchmark (PREREGISTRATION.md §2-§3, §9).

Writes SCRATCH/<b>/pairs.csv.gz (one row per candidate, query column dropped)
and SCRATCH/<b>/score_meta.json (name checks, precision@k per query, counts).

Usage: python -I score_benchmark.py <benchmark id>
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from benchmarks import BENCHMARKS, GT_DIR, SCRATCH, TRAINING_PAIRS, origin, pairs_path, profiles_dir, strip_csv  # noqa: E402
from freyja_score import features_for_query, load_model, score  # noqa: E402


def load_gt(cfg):
    g = pd.read_csv(GT_DIR / cfg["gt"], dtype=str, keep_default_na=False)
    n_rows = len(g)
    g = g.drop_duplicates()
    for c in ("target_ds", "candidate_ds"):
        g[c] = g[c].map(strip_csv)
    return g, n_rows


def training_pairs():
    t = pd.read_csv(TRAINING_PAIRS, dtype=str, keep_default_na=False)
    return {frozenset([(strip_csv(a), b), (strip_csv(c), d)])
            for a, b, c, d in zip(t.ds_name, t.att_name, t.ds_name_2, t.att_name_2)}


def main(b):
    cfg = BENCHMARKS[b]
    t0 = time.time()
    model = load_model()
    feats = list(model.feature_names_in_)
    prof = pd.read_pickle(profiles_dir(b) / "profiles_normalized.pkl")
    assert isinstance(prof.index, pd.RangeIndex) and prof.index.start == 0
    ds = prof["dataset_name"].to_numpy(); at = prof["attribute_name"].to_numpy()
    keys = {}
    for i, k in enumerate(zip(ds, at)):
        keys.setdefault(k, []).append(i)
    dup_keys = sum(1 for v in keys.values() if len(v) > 1)

    g, n_gt_rows = load_gt(cfg)
    queries = sorted(set(zip(g.target_ds, g.target_attr)))
    qid_of = {q: i for i, q in enumerate(queries)}
    self_mask = (g.target_ds == g.candidate_ds) & (g.target_attr == g.candidate_attr)
    gt_with_self = {}
    for a, bb, c, d in zip(g.target_ds, g.target_attr, g.candidate_ds, g.candidate_attr):
        gt_with_self.setdefault((a, bb), set()).add((c, d))
    pos = g[~self_mask]
    positives = {}
    for a, bb, c, d in zip(pos.target_ds, pos.target_attr, pos.candidate_ds, pos.candidate_attr):
        positives.setdefault((a, bb), set()).add((c, d))

    # GT name check (pairs without self-pairs)
    q_in = np.array([(a, bb) in keys for a, bb in zip(pos.target_ds, pos.target_attr)])
    c_in = np.array([(c, d) in keys for c, d in zip(pos.candidate_ds, pos.candidate_attr)])
    missing_cols = sorted({(a, bb) for a, bb in zip(pos.target_ds, pos.target_attr) if (a, bb) not in keys}
                          | {(c, d) for c, d in zip(pos.candidate_ds, pos.candidate_attr) if (c, d) not in keys})
    queries_missing = [q for q in queries if q not in keys]

    train = training_pairs() if b == "freyja_bm" else None
    k, step = cfg["k"], cfg["step"]
    steps = list(range(step, k + 1, step))
    rows, p_at_k, nonfinite, boundary_ties = [], {}, 0, 0
    query_rank_of_self = {}
    for q in queries:
        if q not in keys:
            continue
        qrow = keys[q][0]
        f = features_for_query(prof, qrow, feats)
        fin = np.isfinite(f.to_numpy(dtype=float)).all(axis=1)
        nonfinite += int((~fin).sum())
        s = np.full(len(f), np.nan)
        s[fin] = score(model, f[fin])
        # FREYJA evaluate_benchmark convention: all columns incl. the query, ties by name order
        valid = np.flatnonzero(fin)
        order_all = valid[np.lexsort((valid, -s[valid]))]
        gtq = gt_with_self.get(q, set())
        hits = np.array([(ds[i], at[i]) in gtq for i in order_all[:k]])
        p_at_k["|".join(q)] = [float(hits[:j].sum() / j) for j in steps]
        query_rank_of_self["|".join(q)] = int(np.flatnonzero(order_all == qrow)[0] + 1) if fin[qrow] else None
        # candidates: query row dropped
        cand = order_all[order_all != qrow]
        if len(cand) > k and s[cand[k - 1]] == s[cand[k]]:
            boundary_ties += 1
        posq = positives.get(q, set())
        qo = origin(b, q[0])
        df = f.iloc[cand].reset_index(drop=True)
        df.insert(0, "cand_attr", at[cand]); df.insert(0, "cand_ds", ds[cand])
        df.insert(0, "query_attr", q[1]); df.insert(0, "query_ds", q[0]); df.insert(0, "query_id", qid_of[q])
        df["score"] = s[cand]
        df["label"] = np.array([(ds[i], at[i]) in posq for i in cand], dtype=np.int8)
        df["rank"] = np.arange(1, len(cand) + 1)
        df["primary"] = (df["rank"] <= k).astype(np.int8)
        df["same_origin"] = np.array([origin(b, ds[i]) == qo for i in cand], dtype=np.int8)
        if train is not None:
            df["in_training"] = np.array([frozenset([q, (ds[i], at[i])]) in train for i in cand], dtype=np.int8)
        rows.append(df)
    pairs = pd.concat(rows, ignore_index=True)
    pairs.to_csv(pairs_path(b), index=False, compression={"method": "gzip", "compresslevel": 6, "mtime": 0})

    pk = np.array(list(p_at_k.values()))
    meta = {
        "benchmark": b, "k": k, "step": step, "profiled_columns": len(prof), "tables": int(prof.dataset_name.nunique()),
        "duplicate_profile_keys": dup_keys, "gt_rows": n_gt_rows, "gt_rows_dedup": len(g),
        "gt_self_pairs": int(self_mask.sum()), "gt_pairs": len(pos), "queries": len(queries),
        "queries_missing_from_lake": ["|".join(q) for q in queries_missing],
        "gt_pairs_query_missing": int((~q_in).sum()), "gt_pairs_candidate_missing": int((~c_in).sum()),
        "gt_pairs_any_name_missing": int((~(q_in & c_in)).sum()),
        "gt_columns_missing": ["|".join(x) for x in missing_cols],
        "pairs_rows": len(pairs), "pairs_positives": int(pairs.label.sum()),
        "nonfinite_feature_pairs": nonfinite, "primary_boundary_ties": boundary_ties,
        "precision_steps": steps, "precision_mean": pk.mean(axis=0).tolist(),
        "precision_per_query": p_at_k, "query_rank_of_self": query_rank_of_self,
        "seconds": time.time() - t0,
    }
    (SCRATCH / b / "score_meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k_: v for k_, v in meta.items() if k_ not in
                      ("precision_per_query", "query_rank_of_self", "gt_columns_missing")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
