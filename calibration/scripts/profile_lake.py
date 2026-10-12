"""Profile one data lake with FREYJA's profiler (app/core/profiling) and write
raw and normalized profiles.

Same steps as DataProfiler.generate_profiles_for_datalake at the recorded
commit (same file list, same worker, same thread pool, same normalization,
same round(6), same preprocessing), with one change: the concatenated raw
profiles are sorted by (dataset_name, attribute_name) before normalization,
so the z-scores do not depend on the order in which threads finish.

Usage:
  python -I profile_lake.py LAKE_DIR OUT_DIR --varchar-only true|false
"""
import argparse
import json
import platform
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

FREYJA = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FREYJA))

import duckdb  # noqa: E402
import pandas as pd  # noqa: E402
from app.core.profiling.profiler import ProfilerConfig, DataProfiler, DataProfilerWorker  # noqa: E402

MAX_WORKERS = 8  # FREYJA's default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lake_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--varchar-only", required=True, choices=["true", "false"])
    a = ap.parse_args()
    lake, out = Path(a.lake_dir), Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    varchar_only = a.varchar_only == "true"

    config = ProfilerConfig(datalake_path=lake, output_profiles_path=out / "unused.csv",
                            max_workers=MAX_WORKERS, varchar_only=varchar_only)
    worker = DataProfilerWorker(config)
    # Same file list as DataProfiler.generate_profiles_for_datalake
    files = (list(lake.rglob("*.csv")) + list(lake.rglob("*.parquet")) + list(lake.rglob("*.pq")))

    results, errors, per_table = [], [], []
    start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(worker.process_file, f): f for f in files}
        for fut in as_completed(futures):
            f = futures[fut]
            table_name, profile_df, error = fut.result()
            if error is not None:
                errors.append({"file": str(f.relative_to(lake)), "error": error})
            else:
                results.append(profile_df)
                per_table.append({"file": str(f.relative_to(lake)), "columns": len(profile_df)})
    wall = time.time() - start

    raw = pd.concat(results, ignore_index=True)
    raw = raw.sort_values(["dataset_name", "attribute_name"], kind="stable").reset_index(drop=True)
    dup = raw.duplicated(["dataset_name", "attribute_name"]).sum()
    raw.to_pickle(out / "profiles_raw.pkl")
    raw.to_csv(out / "profiles_raw.csv", index=False)

    norm = DataProfiler.normalize_profiles(raw).round(6)
    norm.to_csv(out / "profiles_normalized.csv", index=False)
    pre = DataProfiler.preprocess_profiles(norm)
    pre.to_pickle(out / "profiles_normalized.pkl")

    freyja_commit = subprocess.run(["git", "-C", str(FREYJA), "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()
    meta = {
        "lake_dir": str(lake), "varchar_only": varchar_only, "max_workers": MAX_WORKERS,
        "files_found": len(files), "tables_profiled": len(results),
        "tables_with_zero_profiled_columns": sum(1 for t in per_table if t["columns"] == 0),
        "tables_failed": len(errors), "columns": len(raw),
        "duplicate_dataset_attribute_pairs": int(dup),
        "wall_time_s": wall, "duckdb": duckdb.__version__, "pandas": pd.__version__,
        "python": platform.python_version(), "machine": platform.platform(),
        "freyja_branch_head": freyja_commit,
    }
    (out / "profile_meta.json").write_text(json.dumps(meta, indent=1))
    (out / "profile_errors.json").write_text(json.dumps(errors, indent=1))
    pd.DataFrame(per_table).sort_values("file").to_csv(out / "profile_per_table.csv", index=False)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
