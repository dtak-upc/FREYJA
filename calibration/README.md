# Is the FREYJA score reliable as a confidence?

Branch `calibration` of FREYJA, folder `calibration/`. Work of 2026-10-12. The analysis plan was fixed in
`PREREGISTRATION.md` (commit `053d931`) before any calibration score was computed; every departure is
logged in `WORKLOG.md` and listed below. Numbers in this file are copied from `results/` (tables generated
by `scripts/report_tables.py` into `results/tables.md` and `results/b2_table.md`).

## Answers

Metric: expected calibration error (ECE, 10 equal-mass bins) with 95% cluster-bootstrap intervals (1000
resamples of query columns). PRIMARY = the top-k candidates FREYJA returns per query (k = 10, 10, 30, 30,
60, 60); it is the set a user acts on. In PRIMARY, 76–92% of candidates are true joins. Estimators: (a) the
raw score min-max scaled to [0, 1]; (b) isotonic regression of the label on the score; (c) a gradient-boosted
classifier on the 22 profile-difference features, isotonic-calibrated. Six benchmarks: FREYJA_BM (the
score model's training lake), SANTOS Small, OmniMatch CR and CG, TUS Small and Big.

**(a) Can the score be turned into a confidence within one lake? Yes.** As it is, the score is not a
probability: min-max scaled, it understates how often top-k candidates are true joins, with top-k ECE
0.45–0.68 on all six benchmarks (leave-one-out scaling; every lower bound ≥ 0.39). An isotonic map fitted by
5-fold cross-validation within the same lake brings top-k ECE to 0.034–0.101 (median 0.063), and the
calibrated 22-feature classifier to 0.011–0.038 (median 0.021). Post hoc (not pre-registered), a caution:
within the top-k, the score-based map is barely more informative than predicting the lake's positive rate.
Its Brier skill against that constant is 0.21, 0.39, −0.02, −0.01, 0.01 and 0.05 (FREYJA_BM, SANTOS Small,
OmniMatch CR, CG, TUS Small, TUS Big), whereas the feature classifier's is 0.26–0.93. On OmniMatch and TUS
Small the score does not separate true from false candidates inside its own top-k: the median score of a
false top-k candidate is higher than that of a true join. FREYJA_BM's within-lake numbers are optimistic: it
is the training lake, and mirror pairs (q1→q2, q2→q1) fall in different folds. On its rows not used to train
the model, within-lake ECE is 0.100 (b) and 0.043 (c).

**(b) Does the map transfer to a lake it was not fitted on? On average yes, but the evidence cannot speak
to independent deployments, and the average hides a failure.** Fitted on the pooled other five benchmarks,
the isotonic map gives top-k ECE 0.036–0.102 (median 0.092) on the held-out one. The within-lake references
are 0.034–0.101. The leave-one-out point lies inside the within-lake interval for SANTOS Small, OmniMatch CR
and CG, above it for FREYJA_BM (0.102 vs 0.034 [0.022, 0.068]) and TUS Small (0.094 vs [0.039, 0.093]), and
below it for TUS Big. Five of the six benchmarks are built by splitting a common origin, and in them
83–100% of labelled joins link same-origin tables. The pre-registered exclusion of shared-origin benchmarks
as both fitting and evaluation data leaves **no unseen benchmark**. Fitted only on the one non-shared-origin
lake (FREYJA_BM), the map gives 0.051–0.197 (median 0.155) on the other five. Split by origin (pre-registered
stratified reading), the transferred map is badly miscalibrated on top-k candidates from another origin:
ECE 0.842 on OmniMatch CR (187 such rows, 0% labelled joins), 0.842 on OmniMatch CG (144, 0%), 0.560 on TUS
Big (352, 22%), against 0.03–0.12 on same-origin candidates. Because those GTs label only same-origin pairs
as joins, this measures confidence on cross-source candidates that the benchmarks call non-joins. TUS
caveat: TUS Big's lake contains almost all of TUS Small's tables. Removing the sibling from the pool (post
hoc) moves (b) to 0.104 (TUS Small) and 0.051 (TUS Big).

**(c) Does a confidence fitted on the 22 features transfer better than one fitted on the score? Not on the
pre-registered metric, and it fails on the one benchmark of independent tables.** In leave-one-out, the
paired difference ECE(c) − ECE(b) on top-k is:
- below 0 for SANTOS Small (−0.051 [−0.104, −0.026]) and TUS Small (−0.029 [−0.071, −0.010]);
- indistinguishable from 0 for OmniMatch CR, OmniMatch CG and TUS Big;
- above 0 for FREYJA_BM (+0.323 [+0.208, +0.419]; held-out rows +0.237 [+0.111, +0.394]).

On FREYJA_BM, the feature model fitted on the other (shared-origin) benchmarks has ECE 0.425 against its
own within-lake 0.028. Medians over the six held-out benchmarks are 0.081 [range 0.019, 0.425] for (c) and
0.092 [0.036, 0.102] for (b). Post hoc, (c) is the more informative confidence where it transfers: Brier
skill 0.75, 0.46 and 0.43 on SANTOS Small, TUS Small and TUS Big, where (b) has 0.37, −0.07 and 0.10. But it
is far worse than a constant on FREYJA_BM (−4.6; held-out rows −1.3). FREYJA_BM is also the score model's
training lake, which favours (b) there. The one test of transfer to independent tables therefore goes
against the features, and no clean test exists in these benchmarks.

### Leave-one-out ECE [95% CI], PRIMARY (top-k), pool = all other benchmarks; within-lake reference last

| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |
|---|---|---|---|---|---|
| FREYJA_BM | 0.671 [0.577, 0.758] | 0.102 [0.080, 0.129] | 0.425 [0.322, 0.521] | 0.034 [0.022, 0.068] | 0.028 [0.009, 0.068] |
| FREYJA_BM (held-out rows) | 0.542 [0.439, 0.674] | 0.139 [0.094, 0.205] | 0.376 [0.262, 0.531] | 0.100 [0.056, 0.185] | 0.043 [0.016, 0.098] |
| SANTOS Small | 0.573 [0.498, 0.646] | 0.070 [0.062, 0.134] | 0.019 [0.017, 0.047] | 0.060 [0.040, 0.113] | 0.015 [0.005, 0.032] |
| OmniMatch CR | 0.680 [0.616, 0.742] | 0.100 [0.077, 0.156] | 0.111 [0.082, 0.173] | 0.096 [0.075, 0.147] | 0.031 [0.020, 0.059] |
| OmniMatch CG | 0.672 [0.618, 0.728] | 0.089 [0.059, 0.139] | 0.098 [0.077, 0.132] | 0.101 [0.058, 0.124] | 0.038 [0.022, 0.067] |
| TUS Small | 0.624 [0.592, 0.654] | 0.094 [0.080, 0.126] | 0.065 [0.042, 0.081] | 0.059 [0.039, 0.093] | 0.011 [0.009, 0.023] |
| TUS Big | 0.445 [0.397, 0.493] | 0.036 [0.032, 0.094] | 0.043 [0.034, 0.077] | 0.067 [0.045, 0.106] | 0.015 [0.010, 0.025] |

Everything else is in `results/tables.md`:
- SECONDARY (all candidates, 0.3–4.4% positives; leave-one-out and within-lake ECE of (b) and (c) are all
  ≤ 0.026, a number that says little at these positive rates);
- the `no_freyja_bm` and `no_shared_origin` pools;
- paired differences;
- all summaries in the four shared-origin variants;
- the stratified reading;
- per-benchmark descriptives.

Figures in `figures/`: one reliability diagram per held-out benchmark; leave-one-out ECE per benchmark with
the within-lake reference; profiling time against columns.

## What was done, in order

1. Cloned FREYJA (main @ `42b0532`) and freyja-readout (`72c911f`); branch `calibration`; Python 3.12.12
   environment pinned in `requirements.txt` (scikit-learn 1.6.1 = the version that pickled the model;
   pandas 2.3.3 because FREYJA's code predates pandas 3).
2. Downloaded FREYJA_BM and the "other assets" from mydisk. Smoke test: profiled two FREYJA_BM tables,
   computed the 22 features with FREYJA's code and scored one query.
3. Inventory of the seven benchmarks (`INVENTORY.md`), then stopped for the lake decision. Decisions: SANTOS
   Small, TUS Small and Big (third-party copy), OmniMatch CR and CG; D3L unavailable; SANTOS Big only for
   profiling time.
4. Wrote and committed `PREREGISTRATION.md` before any calibration score.
5. Downloaded the lakes (published md5 verified for all Zenodo files). Profiled every lake with FREYJA's
   profiler at one commit (`scripts/profile_lake.py`: FREYJA's worker, normalization and preprocessing; rows
   sorted before normalization). Order: FREYJA_BM, SANTOS Small, OmniMatch CR, OmniMatch CG, TUS Small, TUS
   Big. SANTOS Big was profiled last.
6. Compared profiles with the comparison targets. Checked the TUS copy against the FREYJA GT.
7. Scored every (query, candidate) pair of each benchmark (`scripts/score_benchmark.py`). Reran the full
   evaluation (`scripts/evaluate.py`: within-lake, all 30 ordered pairs, leave-one-out with three pools, both
   sets, three estimators, bootstrap) after each benchmark. Committed after each.
8. A fresh reviewer (subagent) audited the code against the pre-registration. Findings and rulings are in
   `WORKLOG.md`. The two important ones:
   - TUS Big's lake contains TUS Small's tables: flagged, plus a post-hoc rerun.
   - The export check was narrower than claimed: strengthened.
9. Post-hoc readings, labelled as such: TUS sibling removal (`scripts/posthoc_tus_sibling.py`), Brier skill
   against the base rate (`scripts/posthoc_brier_skill.py`), and the SANTOS precision diagnostic
   (`scripts/diag_santos_gap.py`).
10. Figures, tables, the verified export (`scripts/export.py`, see `DATA.md`), this README and
    `NUMBERS_FOR_B2.md`.

## Benchmarks, labels, sanity checks

| benchmark | tables | profiled columns | profiling (s) | queries | k | top-k rows | positive rate top-k | positive rate all | same-origin share of positives | GT pairs naming a missing column | P@k ours | P@k models.ipynb | P@k scores.txt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FREYJA_BM | 160 | 680 | 2.4 | 50 | 10 | 500 | 0.918 | 0.0435 | 0.000 | 0 of 1478 | 0.926 | 0.924 | 0.924 |
| SANTOS Small | 550 | 4301 | 9.7 | 50 | 10 | 500 | 0.868 | 0.0027 | 0.827 | 57 of 645 | 0.892 | 0.928 | 0.916 |
| OmniMatch CR | 480 | 1970 | 3.2 | 50 | 30 | 1500 | 0.771 | 0.0177 | 1.000 | 0 of 1742 | 0.748 | 0.609 | 0.547 |
| OmniMatch CG | 440 | 1938 | 3.5 | 50 | 30 | 1500 | 0.765 | 0.0165 | 1.000 | 0 of 1597 | 0.743 | 0.613 | 0.530 |
| TUS Small | 1526 | 12625 | 27.9 | 100 | 60 | 6000 | 0.891 | 0.0063 | 1.000 | 1665 of 9651 | 0.893 | 0.890 | 0.884 |
| TUS Big | 5045 | 49702 | 80.9 | 100 | 60 | 6000 | 0.896 | 0.0159 | 0.961 | 25064 of 103954 | 0.899 | 0.893 | 0.951 |
| SANTOS Big (profiling only) | 11086 | 81528 | 173.0 | – | – | – | – | – | – | – | – | – | – |

How the table was built:
- **Labels:** GT rows with duplicates and self-pairs removed. Dataset names are matched after removing
  `.csv`, because FREYJA main names datasets by file stem.
- **"GT pairs naming a missing column":** GT pairs that cannot be labelled because a named column is not in
  the lake. These are counted and never repaired.
  - SANTOS Small: 45 GT columns are not in their table's header, and 2 GT tables are not in the lake.
  - TUS: FREYJA's restructured GT pairs a column with a same-named column in projections that dropped it.
    In TUS Big, a further 282 columns are entirely empty, so FREYJA does not profile them.
- **Precision@k:** FREYJA's `evaluate_benchmark` convention, with the query column ranked with the others
  and self-pairs kept as hits.
- **Boundary ties:** score ties between ranks k and k+1, resolved by candidate name, occur in 13, 17, 27, 26,
  100 and 87 queries (`results/descriptives.csv`). TUS has many columns with identical profiles.

**Published precision** comes from two sources that disagree: `experiments/notebooks/models.ipynb` cell 56
(the shipped model) and other-assets `scores.txt`.
- **FREYJA_BM, TUS Small, TUS Big** reproduce within 0.01 of at least one source.
- **SANTOS Small** is 0.892 against 0.928 / 0.916. Our profiles equal freyja-readout's exactly (all 34
  metrics, all 4,301 columns), so the gap is not in the profiles.
  - Profiling the 50 query tables twice, as `santos_profiles.csv` does, raises our P@10 to 0.908. That is a
    diagnostic, not used anywhere.
  - The rest of the gap is unexplained.
- **OmniMatch** is 0.74–0.75 against 0.61 / 0.53–0.55: higher than published, unexplained. Our lake is
  `train_tables/`, the only tables the GT names. The published lake composition is not documented.

We tuned nothing to close these gaps.

**Profile comparisons** (`results/profile_comparison_*.csv`):
- **FREYJA_BM vs freyja-readout's `filtered_data.pkl`:** raw profiles are identical (max absolute difference
  0.0 on all 30 numeric features) on the 595 common columns.
  - The 14 missing columns are dates that DuckDB 1.5.6 types as DATE/TIMESTAMP, so `varchar_only` skips them.
  - Normalized values differ only because that file z-scores all features over its own 609 columns.
- **SANTOS Small vs `santos_profiles.csv`** (`dl__` rows): every metric is identical, raw and normalized, on
  all 4,301 columns.

**TUS copy check** (`results/tus_check.csv`):
- TUS Small: all 540 GT tables and all 100 queries are present and profiled.
- TUS Big: 2 of 3,264 GT tables are missing. All 100 queries are present and profiled.

## Shared-origin list (pre-registered) and reasons

| benchmark | shared origin? | reason |
|---|---|---|
| SANTOS Small | yes | real tables split into unionable pieces by the SANTOS authors (`X_0..X_9, X_a, X_b`); 82.7% of positives same-origin by the name rule |
| TUS Small | yes | synthesized from base tables by random projections and selections; GT from 5 base tables; 100% of positives same-origin |
| TUS Big | yes | same procedure; GT from 22 base tables; 96.1% same-origin. Its lake also contains 1,516 of TUS Small's 1,526 table file names (620 byte-identical) |
| OmniMatch CR, CG | yes | `train_tables` generated by OmniMatch's `training_generator.py` from 12 / 11 source tables by horizontal and vertical splits with injected typos; 100% same-origin |
| FREYJA_BM | no | 160 independently collected real tables; a few near-copies (`us_companies` / `us_companies_copy`). It is the score model's training lake: 1,010 of its 1,478 positives (68%) are training pairs |

The origin rule per benchmark is in `PREREGISTRATION.md` §6.

## Departures, failures, skips

- **D3L**: no public copy of the lake exists (only the crawler); not evaluated.
- **TUS**: the authors' Google Cloud bucket returns HTTP 403 ("billing account absent"). We used the
  third-party repackaging by Boutaleb et al. (Zenodo 15499092, md5 verified).
- **SANTOS Big**: profiled only, for the timing chart (no labels).
- **Step 6.1** (scoring from `santos_profiles.csv`) was dropped by decision; the file is a comparison target.
- **Rulings** (each in `WORKLOG.md` with its cost):
  - the scratch path was an unfilled placeholder;
  - scikit-learn and pandas versions pinned;
  - profile rows sorted before normalization;
  - features computed in memory;
  - GT names matched after removing `.csv`.
- **Review rulings:**
  - the TUS sibling overlap is flagged, with a post-hoc rerun that never enters summaries;
  - the export check was strengthened;
  - two tests were added;
  - boundary ties were moved into the descriptives.
- **Post-hoc readings** (labelled, never in summaries): TUS sibling removal, Brier skill against the base
  rate, and the SANTOS precision diagnostic.
- **macOS has no `timeout`:** the first batch of profiling commands failed. They were rerun without the
  90-minute guard. No lake came near it; the longest took 173 s.
- **Zenodo throttles** single connections to ~150 KB/s, so downloads used parallel byte ranges. Every file's
  published md5 matched.

## Caveats a reviewer will raise

- **Labels are what the GTs say.** In the shared-origin benchmarks, positives are essentially "same origin";
  a semantically joinable pair from another source is labelled 0. Some GT pairs name columns that do not
  exist (counted above).
- **Selection:** PRIMARY is selected by the score, so its calibration is conditional on FREYJA's ranking.
  That is the intended use, not an unbiased sample of pairs.
- **Interval coverage:**
  - Bootstrap clusters are query columns. Mirror pairs make clusters dependent, especially in FREYJA_BM
    (1,236 of 1,478 positives have a positive mirror), so intervals may be too narrow.
  - ECE is biased upward under resampling. In 3 of 352 rows the point estimate lies below its percentile
    interval (all SECONDARY).
- **Fold reproducibility:** fold assignment uses scikit-learn 1.6.1 `GroupKFold`, whose order for
  equal-sized groups depends on numpy's non-stable argsort. Outer folds are saved; inner folds are not.
- **Profiler and version effects:** one machine and one DuckDB version. DuckDB's type detection changes
  which columns are profiled (FREYJA_BM date columns).

## Reproduce

From the FREYJA repository root, on branch `calibration`, with the environment of `requirements.txt`. Lakes
live under `/Users/sergi.nadal/UPC/ERC/scratch/<benchmark>/`; the path is fixed in `scripts/benchmarks.py`.

```
python -I calibration/scripts/test_calib.py
python -I calibration/scripts/profile_lake.py <lake dir> <scratch>/<b>/profiles --varchar-only true|false
python -I calibration/scripts/score_benchmark.py <b>
python -I calibration/scripts/check_tus.py
python -I calibration/scripts/compare_profiles.py freyja_bm|santos_small
python -I calibration/scripts/sanity.py
python -I calibration/scripts/evaluate.py            # ~34 min with all six benchmarks
python -I calibration/scripts/posthoc_tus_sibling.py # post hoc
python -I calibration/scripts/posthoc_brier_skill.py # post hoc
python -I calibration/scripts/figures.py
python -I calibration/scripts/report_tables.py
python -I calibration/scripts/export.py              # refuses to write unless every check passes
python -I calibration/scripts/diag_santos_gap.py     # diagnostic
```

Lake folders and profiler flags (`varchar_only` per the FREYJA README; 8 workers):

| benchmark | lake folder | varchar_only |
|---|---|---|
| FREYJA_BM | `datalake/` | true |
| SANTOS Small | `santos_benchmark/datalake/` | true |
| OmniMatch CR | `datasets/culture_recreation/train_tables/` | **false** |
| OmniMatch CG | `datasets/city_government/train_tables/` | **false** |
| TUS Small | `tus/datalake/` | true |
| TUS Big | `tusLarge/datalake/` | true |
| SANTOS Big | `real_data_lake_benchmark/datalake/` | true |

### Versions, commits, machine

| item | value |
|---|---|
| FREYJA | main @ `42b0532260895c0ed712ecf7dfb3b07a5ce44d0e` (2026-07-02); `app/core` unmodified |
| freyja-readout | `72c911ff6e46ec6d146ac582e537fc2ff99bed61` (2026-05-05); its vendored `freyja/app/` = FREYJA main except `app/core/profiling/profiler.py`, which = FREYJA commit `eae0ed8` (2025-12-30) |
| model | `app/core/model/gradient_boosting_ne100_lr0.05_md3_ss0.8_msl10.pkl`: `GradientBoostingRegressor(learning_rate=0.05, min_samples_leaf=10, subsample=0.8, random_state=211199)`, 100 trees, 22 features, pickled with scikit-learn 1.6.1 |
| profiler | FREYJA main `app/core/profiling` via `scripts/profile_lake.py`, DuckDB 1.5.6, 8 workers |
| Python stack | Python 3.12.12, pandas 2.3.3, numpy 2.3.5, scikit-learn 1.6.1, scipy 1.18.1, jellyfish 1.2.1, Levenshtein 0.27.5, matplotlib 3.11.2 |
| machine | Apple M3 Pro (11 cores), 19.3 GB RAM, macOS 26.5.2 |
| seed | 20261012 |

### Sources, sizes, checksums

| lake | source | file | bytes | md5 (published = ours) | sha256 |
|---|---|---|---|---|---|
| FREYJA_BM | mydisk share `QHJbKcyeacxq35f` (WebDAV) | zip | 33,667,406 | 0699688d20e3f0d4a30b7c352243186a (not published) | 475a05f3adbd0393ceda6573055857c2363e64cc8dd25f80f23a45c38f22edd8 |
| other assets | mydisk share `5n8jRDm4neF5HfR` | zip | 230,625,460 | 206c654f311c563eea6e4bd26972f977 (not published) | 36665f03efd06a3dd55c716dd182a86ab60b7dd20deb7f34e50c5a7f3c430729 |
| SANTOS Small | Zenodo 7758091 (SANTOS authors) | `santos_benchmark.zip` | 90,478,237 | 2be111215b569bd2d64515fa5deed490 | 2c82e55cc8d3dd0dd65722d80e22fca91cdee158863e08d85043d35c6c5d00d4 |
| SANTOS Big | Zenodo 7758091 (SANTOS authors) | `real_data_lake_benchmark.zip` | 1,822,726,531 | 1c3c041de79479bb5176729df3c55d35 | 99f68f22689c360e60d1b5dbdbe09ae15cbc6733197dae7aa3a9c20b6270b1ee |
| OmniMatch CR, CG | Zenodo 15705578 (OmniMatch authors) | `data-products-matching.zip` | 98,076,892 | daca6f90a26c346d945f4bdede97bfb2 | bdec08de48452acfea6ad8ea1e620fafe533471e08f856bad8ff89dfda5ab509 |
| TUS Small | Zenodo 15499092 (Boutaleb et al., third party) | `tus.tar.gz` | 441,479,359 | 122bd8be0d7d41488ccfcd48f75486d2 | 92b83630eff9ee0069e331d086268e985bffacd8249208d42cb2cd04b1a526ab |
| TUS Big | Zenodo 15499092 (same) | `tusLarge.tar.gz` | 511,134,024 | 74853546b2c95869c77e084049d0f442 | f8dde2e518559dac963ec1025b4ac0411078b083de37dca9346dbbbe2a889682 |

Profiling wall times (8 workers, one run each) are in `results/profiling.csv` and `figures/profiling_time.*`:

| lake | time |
|---|---|
| FREYJA_BM | 2.4 s |
| OmniMatch CR | 3.2 s |
| OmniMatch CG | 3.5 s |
| SANTOS Small | 9.7 s |
| TUS Small | 27.9 s |
| TUS Big | 80.9 s |
| SANTOS Big | 173.0 s |

## Files

`PREREGISTRATION.md` (the fixed plan), `INVENTORY.md` (step 4), `WORKLOG.md` (decisions, failures, review),
`DATA.md` (every file and column), `NUMBERS_FOR_B2.md`, `scripts/`, `results/`, `figures/`.
