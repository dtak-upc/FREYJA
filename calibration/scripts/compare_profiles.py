"""Compare our profiles with the comparison targets (PREREGISTRATION.md §9).

freyja_bm:    freyja-readout data/filtered_data.pkl (re-saved without pandas-3
              types as SCRATCH/freyja_bm/filtered_data_plain.pkl)
santos_small: freyja-readout data/santos/santos_profiles.csv

Writes calibration/results/profile_comparison_<b>.csv (one row per feature).
Usage: python -I compare_profiles.py freyja_bm|santos_small
"""
import ast
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from benchmarks import CAL, FREYJA, SCRATCH, profiles_dir, strip_csv  # noqa: E402

sys.path.insert(0, str(FREYJA))
from app.core.profiling.metrics import MetricProperties  # noqa: E402
from app.core.profiling.profiler import DataProfiler  # noqa: E402

READOUT = Path("/Users/sergi.nadal/UPC/ERC/freyja-readout")
STR_COLS = ["dataset_name", "attribute_name", "first_word", "last_word",
            "freq_word_containment", "freq_word_soundex_containment"]


def maxdiff(a, b):
    d = np.abs(np.asarray(a, float) - np.asarray(b, float))
    return float(np.nanmax(d)) if len(d) else np.nan


def freyja_bm():
    ours_raw = pd.read_pickle(profiles_dir("freyja_bm") / "profiles_raw.pkl")
    ours_norm = pd.read_pickle(profiles_dir("freyja_bm") / "profiles_normalized.pkl")
    fd = pickle.load(open(SCRATCH / "freyja_bm/filtered_data_plain.pkl", "rb"))
    keys = [(strip_csv(d), a) for d, a in zip(fd["dataset_name"], fd["attribute_name"])]
    pos = {k: i for i, k in enumerate(zip(ours_raw.dataset_name, ours_raw.attribute_name))}
    common = [(i, pos[k]) for i, k in enumerate(keys) if k in pos]
    ti = np.array([c[0] for c in common]); oi = np.array([c[1] for c in common])
    out = []
    for j, f in enumerate(fd["feature_names"]):
        out.append(dict(benchmark="freyja_bm", target="filtered_data.pkl", feature=f,
                        common_columns=len(common), target_columns=len(keys), our_columns=len(ours_raw),
                        max_abs_diff_raw=maxdiff(fd["Phi_raw"][ti, j], ours_raw[f].to_numpy()[oi]),
                        max_abs_diff_normalized=maxdiff(fd["Phi_z"][ti, j], ours_norm[f].to_numpy()[oi]),
                        note="target normalized: z-score of all 30 features over its 609 columns; "
                             "ours: FREYJA normalization over our 680 columns"))
    return pd.DataFrame(out)


def read_santos_profiles():
    path = READOUT / "data/santos/santos_profiles.csv"
    s = pd.read_csv(path, dtype=str, keep_default_na=False)          # strings as written ("" kept)
    n = pd.read_csv(path, float_precision="round_trip", dtype={c: str for c in STR_COLS})
    for c in n.columns:
        if c not in STR_COLS:
            s[c] = n[c]
    pref = s.dataset_name.str.extract(r"^([a-z]+)__")[0]
    s = s[pref == "dl"].copy()                                       # drop the qy__ duplicates
    s["dataset_name"] = s.dataset_name.str.replace(r"^dl__", "", regex=True).map(strip_csv)
    return s.sort_values(["dataset_name", "attribute_name"], kind="stable").reset_index(drop=True)


def santos_small():
    ours_raw = pd.read_pickle(profiles_dir("santos_small") / "profiles_raw.pkl")
    ours_norm = pd.read_pickle(profiles_dir("santos_small") / "profiles_normalized.pkl")
    t_raw = read_santos_profiles()
    t_norm = DataProfiler.preprocess_profiles(DataProfiler.normalize_profiles(t_raw).round(6))
    pos = {k: i for i, k in enumerate(zip(ours_raw.dataset_name, ours_raw.attribute_name))}
    tk = list(zip(t_raw.dataset_name, t_raw.attribute_name))
    common = [(i, pos[k]) for i, k in enumerate(tk) if k in pos]
    ti = np.array([c[0] for c in common]); oi = np.array([c[1] for c in common])
    out = []
    for f, pattern in MetricProperties().distance_patterns.items():
        row = dict(benchmark="santos_small", target="santos_profiles.csv (dl__ rows)", feature=f,
                   common_columns=len(common), target_columns=len(t_raw), our_columns=len(ours_raw))
        if pattern == "substraction":
            row["max_abs_diff_raw"] = maxdiff(t_raw[f].to_numpy()[ti], ours_raw[f].to_numpy()[oi])
            row["max_abs_diff_normalized"] = maxdiff(t_norm[f].to_numpy()[ti], ours_norm[f].to_numpy()[oi])
            row["n_equal_normalized"] = int(np.sum(t_norm[f].to_numpy()[ti] == ours_norm[f].to_numpy()[oi]))
        elif pattern == "containment":
            eq = [a == b for a, b in zip(t_norm[f].to_numpy()[ti], ours_norm[f].to_numpy()[oi])]
            row["n_equal_normalized"] = int(sum(eq))
        else:
            eq = [a == b for a, b in zip(t_norm[f].to_numpy()[ti], ours_norm[f].to_numpy()[oi])]
            row["n_equal_normalized"] = int(sum(eq))
        out.append(row)
    return pd.DataFrame(out)


if __name__ == "__main__":
    b = sys.argv[1]
    df = freyja_bm() if b == "freyja_bm" else santos_small()
    df.to_csv(CAL / f"results/profile_comparison_{b}.csv", index=False)
    pd.set_option("display.width", 250)
    print(df.drop(columns=[c for c in ["note", "target"] if c in df]).to_string(index=False))
