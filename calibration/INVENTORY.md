# Inventory (step 4), 2026-10-12

No calibration score has been computed. The only model call so far is the
step-3 smoke test (one query, two FREYJA_BM tables).

Profiling rate measured on FREYJA_BM with FREYJA's profiler (main @ 42b0532,
DuckDB 1.5.6, 8 workers, Apple M3 Pro, 11 cores): 160 tables, 680 text
columns, 133 MB on disk (138.6 MB uncompressed per the zip), **2.39 s wall**.
That is 285 columns/s or 58 MB/s.

## Ground truths (FREYJA/ground_truths)

All files have columns `target_ds, target_attr, candidate_ds, candidate_attr`
(SANTOS Big: `target_ds, target_attr` only). "Pairs" = distinct rows after
dropping exact duplicates and self-pairs (query = candidate).

| Benchmark | k / step | queries | GT rows | dup rows | self-pairs | pairs | positives per query (min/median/max) | sample or restructured |
|---|---|---|---|---|---|---|---|---|
| FREYJA_BM | 10 / 1 | 50 | 1,646 | 118 | 50 | 1,478 | 26 / 29 / 31 | built by the FREYJA team; training lake |
| SANTOS Small | 10 / 1 | 50 | 695 | 0 | 50 | 645 | 10 / 12 / 30 | headers unified |
| SANTOS Big | none | 80 | 80 | – | – | 0 (no candidates) | – | queries only; README: ~15 queries fail |
| TUS Small | 60 / 10 | 100 | 9,811 | 60 | 100 | 9,651 | 64 / 99 / 129 | headers unified |
| TUS Big | 60 / 10 | 100 | 104,054 | 0 | 100 | 103,954 | 29 / 319 / 4,173 | **sample** of 100 queries; columns removed |
| D3L | 100 / 10 | 100 | 14,352 | 0 | 0 | 14,352 | 109 / 149 / 149 | **sample** of 100 queries; columns removed |
| OmniMatch CG | 30 / 5 | 50 | 1,597 | 0 | 0 | 1,597 | 30 / 32 / 34 | **restructured**, subset of 50 queries |
| OmniMatch CR | 30 / 5 | 50 | 1,742 | 0 | 0 | 1,742 | 30 / 35 / 39 | **restructured**, subset of 50 queries |

## Sources, sizes, estimated profiling time

Time estimates scale the FREYJA_BM rate. "By columns" only where the column
count is known; "by bytes" otherwise. Both are rough (per-table overhead and
table length matter); even at 5x, every lake is far below the 90-minute cap.

| Benchmark | source found | download | lake to profile | tables | text columns | est. profiling |
|---|---|---|---|---|---|---|
| FREYJA_BM | mydisk QHJbKcyeacxq35f (zip; sha256 475a05f3…) | 33.7 MB (done) | `datalake/` | 160 | 680 (measured) | 2.4 s (measured) |
| SANTOS Small | Zenodo 7758091 `santos_benchmark.zip`, md5 2be11121… (authors) | 90.5 MB | `santos_benchmark/datalake/` (441 MB) | 550 (incl. the 50 query tables, same sizes as in `query/`) | 4,301 in santos_profiles.csv | 15 s by columns, 8 s by bytes |
| SANTOS Big | Zenodo 7758091 `real_data_lake_benchmark.zip`, md5 1c3c041d… (authors) | 1.82 GB (11.6 GB unzipped) | `real_data_lake_benchmark/datalake/` (11.5 GB) | 11,086 (+80 query, 76 also in datalake) | unknown | ~3.5 min by bytes |
| TUS Small | authors' Google Cloud bucket **dead** (HTTP 403, billing disabled). Third-party repackaging: Zenodo 15499092 (= 15224451) `tus.tar.gz`, md5 122bd8be…, Boutaleb et al. ("Something's Fishy…", fishy-tus). File names match the FREYJA GT naming. | 441 MB (unzipped size unknown, est. 1.3–1.7 GB) | `tus/datalake/` | ~1,300 (TUS README) | unknown | ~25–30 s by bytes |
| TUS Big | same bucket dead. Zenodo 15499092 `tusLarge.tar.gz`, md5 74853546… (same third party); naming matches the GT (hashed and descriptive names) | 511 MB (est. 1.5–2 GB) | `tusLarge/datalake/` | ~5,000 (TUS README) | unknown | ~30–35 s by bytes |
| D3L | **not found.** The FREYJA README and page link only the crawler (alex-bogatu/DataSpiders) and the d3l code repo. The GT is D3L's "Smaller Real" repository (data.gov.uk / NHS tables, manual GT, renamed to random IDs such as `nA8aluO.csv`). No public copy found (GitHub, Zenodo, web search). | – | – | ~1,000 (D3L paper) | – | – |
| OmniMatch CG | Zenodo 15705578 `data-products-matching.zip`, md5 daca6f90… (authors; one zip for both) | 98 MB for both | `datasets/city_government/train_tables/` (30.5 MB). The GT uses only train tables (382 of 440 present; 0 test tables) | 440 | unknown (`varchar_only=false` per README) | <1 s by bytes, ~7 s by table count |
| OmniMatch CR | same zip | (incl.) | `datasets/culture_recreation/train_tables/` (4.6 MB); GT uses 428 of 480 train tables | 480 | unknown (`varchar_only=false`) | <1 s by bytes, ~7 s by table count |

Total download if every found lake is approved: 90 MB + 1.82 GB + 441 MB +
511 MB + 98 MB ≈ **2.96 GB** (≈ 1.14 GB without SANTOS Big). Disk free: 63 GB.
Total estimated profiling: **≈ 5 minutes** with SANTOS Big, **≈ 1.5 minutes**
without (estimates, see above).

## Existing profiles or predictions (comparison targets only)

No per-pair FREYJA score or prediction exists for any benchmark. Only
per-query precision (and recall) do.

| Benchmark | file | what it is |
|---|---|---|
| FREYJA_BM | freyja-readout `data/filtered_data.pkl` | 609 columns, 30 raw numeric profile features + z-scores over those 609 (pickled with pandas 3). No `first_word` / top-value lists, so the 22 features cannot be recomputed from it. Step 6.2 comparison target. |
| FREYJA_BM | other assets `ground_truths/distances.csv` (706 MB) | 853k pair distances from an older profiler (47 columns, `pct_*` features etc.). Not the current feature set. |
| FREYJA_BM | other assets `models/ground_truth_models.csv` | the model's **training pairs**: 22,610 rows (1,701 semantic, 2,703 syntactic, 18,206 unrelated) with continuous quality. Of our 33,950 FREYJA_BM evaluation pairs, 3,780 (11%) are training pairs (either direction); **1,010 of the 1,478 positives (68%) are training pairs.** |
| SANTOS Small | freyja-readout `data/santos/santos_profiles.csv` | raw profiles, vendored profiler = FREYJA commit eae0ed8 (2025-12-30), 4,747 rows. Dataset names are prefixed `dl__` (4,301 rows, 546 datalake tables) and `qy__` (446 rows, the 50 query tables profiled a second time; **446/446 identical to their `dl__` copies**). 4 datalake tables have no profile (French `analytics-*` files). 36 empty-string `first_word`. **57 of 645 GT pairs name a column absent from these profiles** (e.g. `biodiversity_0.csv / Common Name`). Used in step 6.1. |
| SANTOS Small | freyja-readout `results/santos_quicktest/` | profiles of a sample only. |
| all 7 | other assets `scores.txt` | per-query precision and recall per k for FREYJA (and the other systems) on every benchmark. |
| d3l, santos_small, tus_small | other assets `k_justification/*.csv` | syntactic/semantic join pairs with containment etc. Not profiles. |
| all | FREYJA `experiments/notebooks/models.ipynb`, cell 56 | precision@k of the shipped model per benchmark (the label printed in that cell names another model, but `model_path` is the shipped one). |

Published precision at the largest k, two sources that disagree:

| Benchmark | models.ipynb cell 56 | scores.txt (mean over queries) |
|---|---|---|
| FREYJA_BM | 0.924 | 0.924 |
| SANTOS Small | 0.928 | 0.916 |
| TUS Small | 0.890 | 0.885 |
| TUS Big | 0.894 | 0.950 |
| D3L | 0.751 | 0.746 |
| OmniMatch CG | 0.613 | 0.530 |
| OmniMatch CR | 0.609 | 0.547 |

## How each benchmark was built; shared origin

| Benchmark | how built (one line) | several tables from one origin? |
|---|---|---|
| FREYJA_BM | 160 independent real tables (Kaggle/OpenML-style), joins labelled semantic/syntactic by the FREYJA team | Not by construction. A few near-copies exist (`us_companies` / `us_companies_copy`, `NetflixShows` / `Netflix_Shows`, several `books*`). **Training lake.** |
| SANTOS Small | real open-data tables split by the SANTOS authors into unionable pieces (`X_0..X_9`, `X_a`, `X_b`) | **Yes.** ≥ 82% of GT positives share the query's origin by the name rule `_[0-9a-z].csv` (rule misses 75 GT names). |
| SANTOS Big | 11k real open-data tables | not evaluated (no labels) |
| TUS Small | synthesized from a few Canadian open-data base tables by random projections and selections | **Yes.** The GT's 540 tables come from **5** base tables; 97.4% of positives share the query's base table. |
| TUS Big | same procedure, more base tables | **Yes.** GT tables from **22** base tables; 96.3% of positives share the query's base table. |
| D3L | "Smaller Real": ~1,000 real data.gov.uk / NHS tables, manual relatedness GT | Not by construction (but periodic releases of the same publication). Lake not available. |
| OmniMatch CG / CR | `train_tables` generated by OmniMatch's `training_generator.py`: horizontal and vertical splits of 11 / 12 source tables with injected typos (`*_k_noisy_n.csv`) | **Yes.** 100% of GT positives share the query's source table. |

Consequence for step 5: TUS Small, TUS Big, SANTOS Small and both OmniMatch
lakes are shared-origin. Without them, only FREYJA_BM (the training lake) and
D3L (unavailable) remain. So every "without shared-origin" summary has at most
one benchmark, and it is the training lake.
