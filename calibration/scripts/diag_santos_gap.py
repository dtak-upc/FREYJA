"""Diagnostic, report only (not part of the pre-registered analysis): does the
SANTOS Small precision@10 gap (ours 0.892, published 0.928) come from the
published run profiling the 50 query tables twice (datalake/ and query/), as
freyja-readout's santos_profiles.csv does?

Profile set = santos_profiles.csv with BOTH dl__ and qy__ rows, prefixes
removed (so each query table appears twice under the same name), FREYJA
normalization over all 4,747 rows; precision@k with FREYJA's convention.
Usage: python -I diag_santos_gap.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from benchmarks import CAL, FREYJA, GT_DIR, strip_csv  # noqa: E402
from compare_profiles import READOUT, STR_COLS  # noqa: E402
from freyja_score import features_for_query, load_model, score  # noqa: E402

sys.path.insert(0, str(FREYJA))
from app.core.profiling.profiler import DataProfiler  # noqa: E402


def main():
    path = READOUT / "data/santos/santos_profiles.csv"
    s = pd.read_csv(path, dtype=str, keep_default_na=False)
    n = pd.read_csv(path, float_precision="round_trip", dtype={c: str for c in STR_COLS})
    for c in n.columns:
        if c not in STR_COLS:
            s[c] = n[c]
    s["dataset_name"] = s.dataset_name.str.replace(r"^(dl|qy)__", "", regex=True).map(strip_csv)
    s = s.sort_values(["dataset_name", "attribute_name"], kind="stable").reset_index(drop=True)
    prof = DataProfiler.preprocess_profiles(DataProfiler.normalize_profiles(s).round(6))
    model = load_model()
    g = pd.read_csv(GT_DIR / "santos_small_ground_truth.csv", dtype=str, keep_default_na=False).drop_duplicates()
    for c in ("target_ds", "candidate_ds"):
        g[c] = g[c].map(strip_csv)
    gt = {}
    for a, b, c, d in zip(g.target_ds, g.target_attr, g.candidate_ds, g.candidate_attr):
        gt.setdefault((a, b), set()).add((c, d))
    ds, at = prof.dataset_name.to_numpy(), prof.attribute_name.to_numpy()
    first = {}
    for i, k in enumerate(zip(ds, at)):
        first.setdefault(k, i)
    P = []
    for q in sorted(gt):
        f = features_for_query(prof, first[q], list(model.feature_names_in_))
        sc = score(model, f)
        order = np.lexsort((np.arange(len(sc)), -sc))
        hits = np.array([(ds[i], at[i]) in gt[q] for i in order[:10]])
        P.append([hits[:j].sum() / j for j in range(1, 11)])
    out = {"profile_rows": len(prof), "precision_mean": np.mean(P, axis=0).round(4).tolist()}
    (CAL / "results/diag_santos_gap.json").write_text(json.dumps(out, indent=1))
    print(out)


if __name__ == "__main__":
    main()
