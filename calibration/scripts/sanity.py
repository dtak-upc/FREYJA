"""Sanity checks, report only (PREREGISTRATION.md §9): precision@k next to the
two published sources, GT name checks, profiling record.

Usage: python -I sanity.py
"""
import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from benchmarks import BENCHMARKS, CAL, FREYJA, ORDER, SCRATCH, profiles_dir  # noqa: E402

NB_NAMES = {"santos_small": "santos_small", "tus_small": "tus_small", "tus_big": "tus_big", "freyja_bm": "freyja",
            "om_cg": "omnimatch_city_government", "om_cr": "omnimatch_culture_recreation", "d3l": "d3l"}
SC_NAMES = {"santos_small": "santos_small", "tus_small": "tus_small", "tus_big": "tus_big", "freyja_bm": "freyja",
            "om_cg": "om_cg", "om_cr": "om_cr", "d3l": "d3l"}


def notebook_precision():
    nb = json.load(open(FREYJA / "experiments/notebooks/models.ipynb"))
    out, bench = {}, None
    for o in nb["cells"][56].get("outputs", []):
        for line in "".join(o.get("text", [])).splitlines():
            m = re.search(r"benchmark (\S+)$", line)
            if m:
                bench = m.group(1)
            if line.startswith("Precision scores:"):
                out[bench] = ast.literal_eval(line.split(":", 1)[1].strip())
    return out


def scores_txt_precision():
    txt = (SCRATCH / "other_assets/extract/data/scores.txt").read_text()
    out = {}
    for block in re.split(r"\n(?=[a-zA-Z0-9_]+ = )", txt):
        name, val = block.split(" = ", 1)
        if name.endswith("_freyja_scores") and not name.endswith("_no_k_freyja_scores"):
            d = ast.literal_eval(val.strip())
            P = pd.DataFrame([v["precision"] for v in d.values()])
            out[name[: -len("_freyja_scores")]] = P.mean().tolist()
    return out


def main():
    nb, sc = notebook_precision(), scores_txt_precision()
    pk, names, prof = [], [], []
    for b in ORDER + ["santos_big"]:
        pm = profiles_dir(b) / "profile_meta.json"
        if pm.exists():
            m = json.loads(pm.read_text())
            lake = Path(m["lake_dir"])
            size = sum(f.stat().st_size for f in lake.rglob("*") if f.is_file()) if lake.exists() else None
            prof.append(dict(benchmark=b, varchar_only=m["varchar_only"], max_workers=m["max_workers"],
                             files_found=m["files_found"], tables_profiled=m["tables_profiled"],
                             tables_failed=m["tables_failed"],
                             tables_with_zero_profiled_columns=m["tables_with_zero_profiled_columns"],
                             columns=m["columns"], duplicate_keys=m["duplicate_dataset_attribute_pairs"],
                             lake_bytes=size, wall_time_s=m["wall_time_s"], duckdb=m["duckdb"]))
        sm = SCRATCH / b / "score_meta.json"
        if b not in BENCHMARKS or not sm.exists():
            continue
        m = json.loads(sm.read_text())
        for j, ours in zip(m["precision_steps"], m["precision_mean"]):
            i = m["precision_steps"].index(j)
            pk.append(dict(benchmark=b, k=j, ours=ours,
                           published_models_ipynb=nb.get(NB_NAMES[b], [None] * 99)[i],
                           published_scores_txt=sc.get(SC_NAMES[b], [None] * 99)[i]))
        ranks = [r for r in m["query_rank_of_self"].values()]
        names.append(dict(benchmark=b, gt_rows=m["gt_rows"], gt_rows_after_dedup=m["gt_rows_dedup"],
                          gt_self_pairs=m["gt_self_pairs"], gt_pairs=m["gt_pairs"], queries=m["queries"],
                          queries_missing_from_lake=len(m["queries_missing_from_lake"]),
                          gt_pairs_naming_a_column_not_in_lake=m["gt_pairs_any_name_missing"],
                          of_which_query_missing=m["gt_pairs_query_missing"],
                          of_which_candidate_missing=m["gt_pairs_candidate_missing"],
                          distinct_gt_columns_not_in_lake=len(m["gt_columns_missing"]),
                          positives_in_lake=m["pairs_positives"], candidate_rows=m["pairs_rows"],
                          profiled_columns=m["profiled_columns"], duplicate_profile_keys=m["duplicate_profile_keys"],
                          nonfinite_feature_pairs=m["nonfinite_feature_pairs"],
                          primary_boundary_ties=m["primary_boundary_ties"],
                          queries_whose_own_column_is_not_rank_1=sum(1 for r in ranks if r != 1)))
    pd.DataFrame(pk).to_csv(CAL / "results/precision_at_k.csv", index=False)
    pd.DataFrame(names).to_csv(CAL / "results/gt_name_check.csv", index=False)
    pd.DataFrame(prof).to_csv(CAL / "results/profiling.csv", index=False)
    pkd = pd.DataFrame(pk)
    if len(pkd):
        last = pkd.groupby("benchmark").tail(1)
        print(last.to_string(index=False))
    print(pd.DataFrame(names).T.to_string())


if __name__ == "__main__":
    main()
