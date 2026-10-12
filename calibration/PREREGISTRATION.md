# Pre-registration: is the FREYJA score reliable as a confidence?

Fixed on 2026-10-12, before any calibration score is computed. The only model
call so far is the step-3 smoke test (one FREYJA_BM query on two tables). The
FREYJA_BM lake has been profiled; no other lake has been downloaded or
profiled. After this file is committed, no analysis choice changes. Any
departure forced by a failure is logged in `WORKLOG.md` with its reason and
reported in the README; it never changes a choice below to improve a number.

## 0. Fixed context

- Model: `FREYJA/app/core/model/gradient_boosting_ne100_lr0.05_md3_ss0.8_msl10.pkl`, unmodified, never retrained or tuned.
- Code: FREYJA main @ 42b0532 (`app/core` untouched); our scripts live in `calibration/scripts/`.
- Software: Python 3.12.12, DuckDB 1.5.6, pandas 2.3.3, numpy 2.3.5, scikit-learn 1.6.1 (`requirements.txt`).
- Seed: 20261012 everywhere a seed is needed.

## 1. Benchmarks, lakes, order

| Benchmark (id) | lake folder profiled | profiler flags (FREYJA README) | k (README) | GT file |
|---|---|---|---|---|
| FREYJA_BM (`freyja_bm`) | mydisk zip `datalake/` | varchar_only=true | 10 | `freyja_ground_truth.csv` |
| SANTOS Small (`santos_small`) | Zenodo 7758091 `santos_benchmark/datalake/` | varchar_only=true | 10 | `santos_small_ground_truth.csv` |
| OmniMatch Culture Recreation (`om_cr`) | Zenodo 15705578 `datasets/culture_recreation/train_tables/` | varchar_only=**false** | 30 | `omnimatch_culture_recreation_ground_truth.csv` |
| OmniMatch City Government (`om_cg`) | Zenodo 15705578 `datasets/city_government/train_tables/` | varchar_only=**false** | 30 | `omnimatch_city_government_ground_truth.csv` |
| TUS Small (`tus_small`) | Zenodo 15499092 `tus.tar.gz` → `tus/datalake/` | varchar_only=true | 60 | `tus_small_ground_truth.csv` |
| TUS Big (`tus_big`) | Zenodo 15499092 `tusLarge.tar.gz` → `tusLarge/datalake/` | varchar_only=true | 60 | `tus_big_ground_truth_sample.csv` |

- max_workers = 8 (FREYJA default) for every lake. Profiling with `scripts/profile_lake.py`: FREYJA's worker, normalization (z-score, ddof=1, NaN→0), `round(6)` and preprocessing, with raw profile rows sorted by (dataset_name, attribute_name) before normalization.
- D3L: unavailable (no public copy; the user has none). Recorded, not evaluated.
- SANTOS Big: no labels. Downloaded and profiled only at the very end, if time allows, for the profiling-time chart; never evaluated.
- TUS (third-party copy): before scoring, check that every table and every column named in the FREYJA GT exists in the copy (file present; column in the CSV header; column profiled), and that TUS Small has all 100 queries. Provenance = Zenodo record 15499092 + md5 of the tarball. A missing name is counted and reported, never repaired.
- Order of work: FREYJA_BM, SANTOS Small, OmniMatch CR, OmniMatch CG, TUS Small, TUS Big (smallest lake first, TUS Big last), then SANTOS Big profiling. A lake whose profiling exceeds 90 minutes is stopped, noted, skipped. The full evaluation (§5–§7) is rerun on all benchmarks scored so far after each benchmark.

## 2. Ground truth, pairs, labels

- GT rows: exact duplicate rows removed. Dataset names map to profile names by removing a trailing `.csv` (FREYJA main names datasets by file stem). Attribute names are compared exactly.
- Queries: the distinct (target_ds, target_attr) of the GT. A query absent from the lake profiles cannot be scored: counted and reported per benchmark.
- Candidates: for each query, every other profiled column of the same lake. The query column itself is dropped. Same-table columns are candidates (TUS Big's 322 same-table GT pairs stay labelled).
- Label: 1 if (query, candidate) is a GT row after removing duplicates and self-pairs, else 0.
- GT pairs that name a column (query or candidate) not in the lake profiles: counted and reported per benchmark, never repaired. They contribute no row.
- If a (dataset, attribute) key occurs more than once in a lake's profiles, every copy is a candidate and carries the label; a duplicated query key uses its first copy in sorted order as the query. Counts are reported.

## 3. Score, rank, evaluation sets

- Features: the 22 features `model.feature_names_in_`, computed with FREYJA's `ComputeDistances._compute_distances_vectorized` on the lake's preprocessed normalized profiles, in memory.
- Score: `model.predict` on those features (raw regression output, not divided by 0.5). A pair with a non-finite feature is counted, reported and has no score.
- Rank within query: score descending; ties broken by candidate (dataset_name, attribute_name) ascending. Rank 1 = best candidate.
- **PRIMARY** set: per query, the candidates with rank ≤ k (k from the table above). **SECONDARY** set: all candidates. Ties at the k boundary are broken by the rule above; the number of queries with a tie between ranks k and k+1 is reported.
- FREYJA_BM has two evaluation variants wherever FREYJA_BM is the evaluated benchmark: **all** and **held-out rows**. Held-out rows = the evaluation rows minus every pair present in other-assets `models/ground_truth_models.csv` (the model's training pairs), matched as an unordered pair of (dataset, attribute) after removing `.csv`. Rows are removed after the PRIMARY selection; nothing is re-ranked. When FREYJA_BM is fitting data, all its rows are used.

## 4. Estimators (same rows for all three)

Fitting rows = rows of the fitting benchmark(s) in the same set (PRIMARY or SECONDARY) as the evaluation.

- **(a) raw**: p = clip((s − min_fit) / (max_fit − min_fit), 0, 1), min and max of the score over the fitting rows (p = 0.5 everywhere if max_fit = min_fit).
- **(b) isotonic**: `IsotonicRegression(out_of_bounds="clip")` (increasing=True, defaults otherwise) of label on score, fitted on the fitting rows.
- **(c) features**: `HistGradientBoostingClassifier(random_state=20261012)`, all other parameters default (scikit-learn 1.6.1: early_stopping="auto", max_iter=100, …), on the 22 features (model order), label = in GT, fitted on all fitting rows. Then `IsotonicRegression(out_of_bounds="clip")` of label on the classifier's 5-fold out-of-fold `predict_proba[:,1]` over the same fitting rows, folds = `GroupKFold(n_splits=5)` (no shuffle) grouped by query column (group = benchmark + query). Prediction on evaluation rows = isotonic(classifier fitted on all fitting rows). No class weighting, no tuning.

## 5. Designs (all reported)

- **Within-lake reference**: per benchmark and set, `GroupKFold(n_splits=5)` over query columns (query ids numbered in sorted (dataset, attribute) order); for each fold, fit (b) and (c) on the other four folds (for (c) the inner 5-fold calibration runs inside those four folds), predict the held-out fold; out-of-fold predictions pooled. FREYJA_BM: evaluated on all and on held-out rows.
- **Pairwise transfer**: every ordered pair (A, B), A ≠ B: fit on A, evaluate on B, (a), (b), (c), both sets.
- **Leave-one-out**: for each benchmark B, fit on the pooled rows of the other benchmarks, evaluate on B, (a), (b), (c), both sets. Three fitting pools, all reported:
  1. `all`: every other benchmark (main pool);
  2. `no_freyja_bm`: every other benchmark except FREYJA_BM (identical to `all` when B = FREYJA_BM);
  3. `no_shared_origin`: every other benchmark not in the shared-origin list (§6). An empty pool is reported as "no fitting data".
- **Stratified reading** (PRIMARY only, leave-one-out with the `all` pool): each candidate is flagged same-origin or different-origin by the rule in §6. Per benchmark, stratum and estimator: rows, queries, positive rate, ECE and Brier with the bootstrap of §7. Also per benchmark: share of positives that are same-origin, in SECONDARY (all labelled positives present in the lake) and in PRIMARY.

## 6. Shared origin

Shared-origin benchmarks (several tables derived from one origin by splitting or sampling):

- **SANTOS Small**: real tables split into unionable pieces by the SANTOS authors.
- **TUS Small**, **TUS Big**: synthesized from base tables by random projections and selections (TUS Small GT: 5 base tables; TUS Big GT: 22).
- **OmniMatch CR**, **OmniMatch CG**: `train_tables` generated by OmniMatch's `training_generator.py`, horizontal and vertical splits of 12 / 11 source tables with injected typos.

Not shared-origin: **FREYJA_BM** (independent real tables; it is the training lake, a separate caveat).

Every summary is reported four ways: all; shared-origin benchmarks excluded as fitting data; excluded as evaluation data; excluded as both. With these lakes, "excluded as both" leaves no fitting data for the only remaining benchmark; it is reported as **"no unseen benchmark remains"**.

Origin rule, applied to the table name with `.csv` (same-origin = origin(query table) == origin(candidate table); a name the rule does not match is its own origin):

| Benchmark | origin(table) |
|---|---|
| FREYJA_BM | the table name itself (identity) |
| SANTOS Small | name with the regex `_[0-9a-z]\.csv$` removed |
| TUS Small, TUS Big | name with `____c\d+_\d+____\d+\.csv$` removed |
| OmniMatch CR, CG | name with `_\d+_noisy_\d+\.csv$` removed |

## 7. Metrics and intervals

- **ECE**: 10 equal-mass bins. Rows are put in canonical order (query id, rank), sorted stably by predicted probability, and split with `numpy.array_split` into 10 consecutive bins. ECE = Σ_b (n_b / N) · |mean(y_b) − mean(p_b)|; empty bins are skipped.
- **Brier**: mean((p − y)²).
- **95% intervals**: 1000 bootstrap resamples of query columns with replacement (as many draws as the evaluated rows have queries), each query contributing all its evaluation rows; ECE (bins recomputed on the resample) and Brier are recomputed with predictions fixed (no refitting); 2.5th and 97.5th percentiles (`numpy.percentile`, default method). `numpy.random.default_rng(20261012)` is created afresh before each table row. Rows evaluated on the same benchmark and set therefore share their resamples. A resample row repeated w times counts w times in the bins.
- **Derived (paired)**: for leave-one-out and pairwise rows, ECE(c) − ECE(b) and ECE(b) − ECE(a), with the percentile interval of the replicate differences (paired because they share resamples).
- **Descriptives** per benchmark and set: queries, rows, positives, positive rate, median score of a true join, median score of a false candidate, number of boundary ties (PRIMARY).

## 8. Summaries

Median, minimum and maximum over held-out benchmarks (leave-one-out) and over ordered pairs (pairwise), per set and estimator, PRIMARY first; each in the four shared-origin variants of §6, with the `no_freyja_bm` pool as an extra row, and with FREYJA_BM evaluated on all rows and on held-out rows.

How the questions will be read (fixed now): (a) within-lake ECE of (b) and (c) with intervals; (b) leave-one-out ECE of (b) next to its within-lake reference, per benchmark; (c) the paired difference ECE(c) − ECE(b) in leave-one-out, per benchmark, counting benchmarks whose interval lies below 0, above 0, or contains 0. No threshold on ECE is used to call anything "calibrated"; numbers are reported as they are.

## 9. Sanity checks (report only, never tuned against)

- precision@k per benchmark with FREYJA's `evaluate_benchmark` convention: all lake columns including the query column ranked by score (ties as in §3); a hit is a ranked column listed for that query in the GT (duplicates removed, **self-pairs kept**); P@j averaged over queries for j = step, 2·step, …, k. Reported next to both published sources: `experiments/notebooks/models.ipynb` (cell 56, the shipped model) and other-assets `scores.txt` (`<benchmark>_freyja_scores`, mean over queries).
- Counts per benchmark: GT pairs naming a column not in the lake; queries not in the lake.
- Profile comparisons (comparison targets only, never used in the analysis): FREYJA_BM vs freyja-readout `data/filtered_data.pkl` (609 columns); SANTOS Small vs freyja-readout `data/santos/santos_profiles.csv` (prefixes `dl__` / `qy__` removed, `qy__` duplicates dropped; read with `float_precision="round_trip"` and empty `first_word` read as ""). On columns common by (dataset, attribute): max absolute difference per normalized feature (and per raw feature), plus counts of equal `first_word`, `last_word` and top-value lists.

## 10. Outputs

`results/pairs.csv` (one row per design × fitting data × evaluated benchmark × set × estimator, incl. FREYJA_BM variant), `results/leave_one_out.csv`, `results/within_lake.csv`, `results/descriptives.csv`, `results/summary.csv`, `results/stratified.csv`, `results/precision_at_k.csv`, `results/gt_name_check.csv`, `results/profile_comparison.csv`, `results/profiling.csv`. Figures as in the protocol (§7 of the brief), main pool `all`, FREYJA_BM on all rows. Per-benchmark exports (profiles, pair files, every prediction row, all bootstrap replicates) are written to the scratch folder by a verifying export script and described in `DATA.md`.
