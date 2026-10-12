# Data files

Two places hold data:

- `calibration/results/` (in the repo): every table reported.
- `export/` in the scratch folder (`/Users/sergi.nadal/UPC/ERC/scratch/export/`, not in git because of its size): raw data per benchmark, written only after the checks in `scripts/export.py` passed (see `export/verification.json`). `export/MANIFEST.csv` (copied to `results/export_manifest.csv`) lists every exported file with its size and sha256.

Benchmark ids: `freyja_bm`, `santos_small`, `om_cr` (OmniMatch Culture Recreation), `om_cg` (OmniMatch City Government), `tus_small`, `tus_big`.
Sets: `PRIMARY` = top-k candidates per query (k = 10, 10, 30, 30, 60, 60); `SECONDARY` = all candidates.
Estimators: `raw` (a), `isotonic` (b), `features` (c). See `PREREGISTRATION.md`.

All CSVs are comma-separated with a header. Floats are written with Python's shortest round-trip representation; read them with `pandas.read_csv(..., float_precision="round_trip")` for exact values. Read string columns with `keep_default_na=False` (column names such as `NA` or empty `first_word` values must stay strings).

## calibration/results/

| file | one row per | columns |
|---|---|---|
| `pairs.csv` | design × fitting data × evaluated benchmark × set × FREYJA_BM row variant × estimator | `row_id` (key into the replicate files); `design` (`within_lake`, `pairwise`, `leave_one_out`); `fit` (fitting label: `own_5fold` for within-lake, the fitting benchmark for pairwise, the pool `all` / `no_freyja_bm` / `no_shared_origin` for leave-one-out); `fit_benchmarks` (`+`-joined ids); `eval`; `set`; `eval_rows` (`all`, or `heldout_rows` = FREYJA_BM rows not in the model's training pairs); `estimator`; `n_rows`, `n_queries`, `n_pos`, `pos_rate` of the evaluated rows; `ece`, `ece_lo`, `ece_hi` (point and 95% bootstrap interval); `brier`, `brier_lo`, `brier_hi`; `note` (`no fitting data` when the pool is empty) |
| `leave_one_out.csv`, `within_lake.csv` | the same rows as `pairs.csv`, filtered by design | as `pairs.csv` |
| `leave_one_out_primary_table.txt` | – | the printed PRIMARY leave-one-out table (pool `all`), within-lake references last |
| `paired_differences.csv` | leave-one-out or pairwise evaluation × contrast | `contrast` (`ece_features_minus_isotonic`, `ece_isotonic_minus_raw`), `diff` (point), `lo`, `hi` (percentiles of the paired replicate differences) |
| `descriptives.csv` | benchmark × set × row variant | queries, rows, positives, positive rate, median score of true joins and of false candidates (raw model output), share of positives that are same-origin, PRIMARY boundary ties (queries with a score tie between ranks k and k+1) |
| `summary.csv` | design × shared-origin variant × FREYJA_BM row variant × set × estimator | `n` (benchmarks or ordered pairs summarized), median / min / max of ECE and Brier; `note` = `no unseen benchmark remains` when nothing is left |
| `stratified.csv` | held-out benchmark × row variant × stratum × estimator (leave-one-out, pool `all`, PRIMARY) | `strat_row_id` (key into `replicates_stratified.csv.gz`), `stratum` (`same_origin` / `different_origin`), counts, ECE and Brier with intervals |
| `precision_at_k.csv` | benchmark × k | `ours` (FREYJA's `evaluate_benchmark` convention), `published_models_ipynb` (notebook cell 56), `published_scores_txt` (mean over queries of other-assets `scores.txt`) |
| `gt_name_check.csv` | benchmark | GT rows, duplicates, self-pairs, pairs, queries, GT pairs naming a column not in the lake (split by query / candidate), positives present, candidate rows, duplicate profile keys, non-finite feature pairs, PRIMARY boundary ties, queries whose own column is not ranked first |
| `tus_check.csv` | TUS benchmark | pre-scoring check of the third-party TUS copy against the FREYJA GT |
| `profiling.csv` | lake | profiler flags, files, tables profiled / failed / with no profiled column, columns, lake bytes, wall time (s), DuckDB version |
| `profile_comparison_freyja_bm.csv`, `profile_comparison_santos_small.csv` | profile feature | common columns, max absolute difference raw and normalized against the comparison target, count of equal values |
| `diag_santos_gap.json` | – | diagnostic only: SANTOS Small precision@k when the query tables are profiled twice (as in santos_profiles.csv) |
| `posthoc_tus_overlap.json` | – | POST-HOC: overlap between the TUS Small and TUS Big lakes (file names, identical bytes, profiled column keys, GT tables, queries) |
| `posthoc_tus_sibling.csv` | held-out TUS benchmark × set × estimator | POST-HOC: leave-one-out with the sibling TUS lake also removed from the pool; same columns as `pairs.csv` plus `analysis` |
| `posthoc_brier_skill.csv` | design × benchmark × row variant × estimator (PRIMARY) | POST-HOC: `brier_constant` = r(1−r) for the evaluated positive rate r, `skill` = 1 − brier / brier_constant, `skill_lo`, `skill_hi` (same bootstrap draws) |
| `tables.md` | – | all report tables, generated from the files above by `scripts/report_tables.py` |
| `b2_table.md` | benchmark | the NUMBERS_FOR_B2 table, generated |
| `export_manifest.csv` | exported file | `path`, `bytes`, `sha256` |

## export/<benchmark>/

| file | content |
|---|---|
| `profiles_raw.csv`, `profiles_raw.pkl` | raw FREYJA profiles, one row per profiled column, sorted by (`dataset_name`, `attribute_name`); `dataset_name` is the file stem. Columns: the 34 active FREYJA metrics (`app/core/profiling/metrics.py`). The `.pkl` is the exact in-memory frame; in the `.csv`, list columns are Python list reprs |
| `profiles_normalized.csv`, `profiles_normalized.pkl` | after FREYJA's normalization (z-score of 14 metrics, NaN→0) and `round(6)`; the `.pkl` is additionally preprocessed exactly as FREYJA's pickle (sets, strings) and is what the scores were computed from |
| `profiles_normalized.jsonl` | the normalized profiles (before preprocessing) as typed JSON Lines, one object per column; every value is `{"<type>": value}` with type `str`, `int`, `float` (repr string), `bool`, `date`, `datetime` or `none`, so Python types survive (they matter: `1 == 1.0 == True` in set containment). The export check recomputes every feature and score from this file |
| `profile_meta.json`, `profile_errors.json`, `profile_per_table.csv` | profiling run record: flags, counts, wall time, versions; errors; columns profiled per file |
| `pairs.csv.gz` | one row per (query, candidate): `query_id` (index of the query in the sorted distinct GT queries), `query_ds`, `query_attr`, `cand_ds`, `cand_attr`, the 22 model features in model order, `score` (model output), `label` (1 = in GT), `rank` (1 = best; score descending, ties by candidate name), `primary` (rank ≤ k), `same_origin` (name rule of PREREGISTRATION.md §6), and for FREYJA_BM `in_training` (pair present in the model's training pairs, either direction) |
| `score_meta.json` | scoring record: GT counts, missing names (`gt_columns_missing`), precision@k per query, rank of each query's own column, boundary ties |
| `predictions/<design>__<fit>__<eval>__<set>.csv.gz` | every prediction row: `query_id`, `rank` (join key to `pairs.csv.gz`), `label`, `p_raw`, `p_isotonic`, `p_features` (within-lake files have no `p_raw`), `fold` (within-lake only, 0-4). Rows are in canonical order (query_id, rank), the order used for ECE bins |
| `replicates.csv.gz` | every bootstrap replicate of the rows of `results/pairs.csv` evaluated on this benchmark: `row_id`, `replicate` (0-999), `ece`, `brier` |
| `replicates_stratified.csv.gz` | the same for `results/stratified.csv`: `strat_row_id`, `replicate`, `ece`, `brier` |

## Bootstrap definition (exact)

For each evaluated row set, `rng = numpy.random.default_rng(20261012)`; `draws = rng.integers(0, n_queries, size=(1000, n_queries))`, queries numbered in sorted order of `query_id` among the evaluated rows. In replicate r, a query drawn c times contributes all its rows c times. ECE bins: the rows in canonical order (query_id, rank), each repeated c times with copies adjacent, stably sorted by predicted probability and cut like `numpy.array_split(·, 10)`. Interval = `numpy.percentile(replicates, [2.5, 97.5])` (linear interpolation). `scripts/calib.py` implements this without materializing the repeated rows; `scripts/test_calib.py` checks it against the explicit construction.
