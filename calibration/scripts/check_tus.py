"""Pre-scoring check of the third-party TUS copy (PREREGISTRATION.md §1).

For every table and column named in the FREYJA GT: file present in the lake
folder; column in the header as DuckDB reads it with the profiler's options;
column profiled. Also: queries present and profiled. Report only.

Usage: python -I check_tus.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb  # noqa: E402
import pandas as pd  # noqa: E402

from benchmarks import BENCHMARKS, CAL, GT_DIR, profiles_dir, strip_csv  # noqa: E402


def header(path):
    con = duckdb.connect()
    try:
        rows = con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{path.as_posix()}', header = TRUE, "
                           "ignore_errors = TRUE, sample_size = 100, strict_mode = false)").fetchall()
        return {r[0].replace("﻿", "").replace('"', "").replace("\n", "").replace("\r", "").strip(): r[1]
                for r in rows}
    finally:
        con.close()


def main():
    out = []
    for b in ["tus_small", "tus_big"]:
        cfg = BENCHMARKS[b]
        lake = cfg["lake"]
        g = pd.read_csv(GT_DIR / cfg["gt"], dtype=str, keep_default_na=False).drop_duplicates()
        prof = pd.read_pickle(profiles_dir(b) / "profiles_normalized.pkl")
        profiled = set(zip(prof.dataset_name, prof.attribute_name))
        cols = set(zip(g.target_ds, g.target_attr)) | set(zip(g.candidate_ds, g.candidate_attr))
        tables = sorted({t for t, _ in cols})
        present = {t: (lake / t).exists() for t in tables}
        headers = {t: header(lake / t) for t in tables if present[t]}
        in_header = {c: present[c[0]] and c[1] in headers[c[0]] for c in cols}
        queries = set(zip(g.target_ds, g.target_attr))
        types = pd.Series([headers[t][a] for t, a in cols if in_header[(t, a)]]).value_counts().to_dict()
        not_profiled = [c for c in cols if in_header[c] and (strip_csv(c[0]), c[1]) not in profiled]
        out.append(dict(benchmark=b, gt_tables=len(tables), gt_tables_missing=sum(not v for v in present.values()),
                        gt_columns=len(cols), gt_columns_not_in_header=sum(not v for v in in_header.values()),
                        gt_columns_in_header_not_profiled=len(not_profiled),
                        not_profiled_types=str(pd.Series([headers[t][a] for t, a in not_profiled]).value_counts().to_dict()),
                        queries=len(queries), queries_table_present=sum(present[t] for t, _ in queries),
                        queries_in_header=sum(in_header[q] for q in queries),
                        queries_profiled=sum((strip_csv(t), a) in profiled for t, a in queries),
                        gt_column_types=str(types)))
    df = pd.DataFrame(out)
    df.to_csv(CAL / "results/tus_check.csv", index=False)
    print(df.T.to_string())


if __name__ == "__main__":
    main()
