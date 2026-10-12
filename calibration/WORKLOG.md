# Work log

Running record of decisions (`Ruling:`), failures and skips, in order. The
README will summarise it.

## Setup (2026-10-12)

- FREYJA main @ 42b0532260895c0ed712ecf7dfb3b07a5ce44d0e (2026-07-02 "Fixes"); branch `calibration` created from it.
- freyja-readout @ 72c911ff6e46ec6d146ac582e537fc2ff99bed61 (2026-05-05). Its vendored `freyja/app/` equals FREYJA main except `app/core/profiling/profiler.py`, which equals FREYJA commit **eae0ed8** (2025-12-30). Differences from main: main names datasets by file stem (no `.csv`), recurses into subfolders (`rglob`), also reads Parquet, and pickles the normalized profiles after `round(6)` (eae0ed8 pickled the unrounded ones).
- Machine: Apple M3 Pro, 11 cores, 19.3 GB RAM, macOS 26.5.2. Python 3.12.12 (uv venv outside the repos), DuckDB 1.5.6, pandas 2.3.3, scikit-learn 1.6.1, numpy 2.3.5. Full pins in `requirements.txt`.
- Model: `GradientBoostingRegressor(learning_rate=0.05, min_samples_leaf=10, random_state=211199, subsample=0.8)`, 100 trees, 22 features, pickled with scikit-learn 1.6.1.

## Rulings

- Ruling: scratch folder = `/Users/sergi.nadal/UPC/ERC/scratch` (outside both repos, 63 GB free) — the protocol's scratch path was the unfilled placeholder `<PATH>` — cost if wrong: move the folder.
- Ruling: scikit-learn pinned to 1.6.1, the version that pickled the model — avoids cross-version unpickling — cost if wrong: none known.
- Ruling: pandas pinned to 2.3.3, not 3.x — FREYJA's code predates pandas 3 (string dtype and copy-on-write changes) — cost if wrong: none for FREYJA code. freyja-readout's `filtered_data.pkl` needs pandas 3 to unpickle, so it was read once in a separate pandas-3 env and re-saved as plain Python/numpy (`scratch/freyja_bm/filtered_data_plain.pkl`).
- Ruling: `scripts/profile_lake.py` reproduces `DataProfiler.generate_profiles_for_datalake` with FREYJA's own worker, normalization, `round(6)` and preprocessing, plus one change: raw profiles are sorted by (dataset_name, attribute_name) before normalization — thread completion order otherwise changes the last bits of the z-score means — cost if wrong: none for FREYJA semantics.
- Ruling: features are computed in memory with FREYJA's `_compute_distances_vectorized`, not written to and re-read from CSV as FREYJA's API does — avoids float re-parsing — cost if wrong: last-bit feature differences against FREYJA's API path.
- Ruling: ground-truth dataset names map to profile names by stripping a trailing `.csv` — FREYJA main's profiler names datasets by file stem, the GTs use file names — cost if wrong: none (FREYJA_BM: 0 GT names unmatched after the mapping).

## Failures and skips

- TUS: the authors' Google Cloud links (`storage.googleapis.com/table-union-benchmark/...`) return HTTP 403 ("billing account ... absent"). Only third-party copies were found (Zenodo 15499092 / 15224451, Boutaleb et al.; Zenodo 15350355, a modified "Novel Table Search" TUS with 33/100 TUS Small queries).
- D3L: no public copy of the lake found.
- Wayback Machine check for the TUS files: HTTP 429 (rate-limited), not retried.

## User decisions after the step-4 stop (2026-10-12)

- Lakes approved: SANTOS Small, TUS Small, TUS Big (Boutaleb copy, Zenodo 15499092), OmniMatch CR and CG. D3L skipped (unavailable). SANTOS Big: profiling-time only, at the end, if time allows.
- Analysis uses our own profiles for every lake, SANTOS Small included; santos_profiles.csv and filtered_data.pkl are comparison targets only. Step 6.1 dropped as a separate analysis.
- GT: duplicates and self-pairs removed for labels; TUS Big same-table pairs kept; name mismatches counted, not repaired.
- precision@k: FREYJA code convention only, both published sources reported.
- Added: stratified same/different-origin reading; FREYJA_BM "held-out rows" variant; leave-one-out pool without FREYJA_BM.

## Progress

- FREYJA_BM scored (33,950 candidate rows, 1,478 positives, 0 GT names missing, 13 PRIMARY boundary ties, 9 queries whose own column is not rank 1 because identical columns tie with it). precision@10 = 0.926 (published 0.924 in both sources).
- FREYJA_BM vs filtered_data.pkl: raw profiles identical (max abs diff 0.0 on all 30 numeric features) on 595 common columns. 14 of its 609 columns are absent from ours: all date-like columns (`ModifiedDate`, `date`, `birthdate`, ...) that DuckDB 1.5.6 types as DATE/TIMESTAMP, so `varchar_only=true` skips them; the older profiling run read them as VARCHAR. Normalized values differ only because the two files normalize differently (filtered_data z-scores all 30 features over its 609 columns).
- Downloads from Zenodo run at ~150-170 KB/s per connection; the four lakes were downloaded in parallel with resume.

## Final review (fresh reviewer subagent, run while TUS Small was being evaluated) and rulings

- Final: Ruling: TUS Big's lake contains 1,516 of TUS Small's 1,526 table file names (620 of them byte-identical; 12,605 of TUS Small's 12,625 profiled (table, column) keys also exist in TUS Big; 478 of the 540 TUS Small GT tables appear in the TUS Big GT; no common query). The pre-registered leave-one-out pools `all` / `no_freyja_bm` and the pairwise TUS Small <-> TUS Big rows therefore fit on the sibling lake and are close to within-lake for these two benchmarks. The pre-registered rows stay as they are; they are flagged in the README, and a clearly labelled POST-HOC rerun (`scripts/posthoc_tus_sibling.py`, pool = all others minus the sibling TUS lake) is reported next to them and never used in summaries — cost if wrong: none for the pre-registered numbers; the post-hoc row is extra information.
- Final: fixed export verification being narrower than claimed — `export.py` now rebuilds every pair file from the exported typed profiles + GT + training pairs and compares every column (negative control: one flipped label is detected), checks prediction files sit on the right rows and folds partition queries, recomputes n/queries/positives/ECE/Brier, recomputes bootstrap replicates (all 1000 PRIMARY, 0-99 SECONDARY), checks paired differences, descriptives and summary, fails on NaN ECE, and checks that the exported copies hash identically to the verified files.
- Final: added `test_bootstrap_with_gapped_query_ids` and `test_bootstrap_subset_equals_full` (gapped query ids were untested; production code already handled them, so the first test passed on its first run: it adds coverage, it did not expose a bug). `calib.bootstrap` gained an optional `which` (subset of replicate indices) for the export check; default behaviour unchanged.
- Final: descriptives now carry `primary_boundary_ties` (pre-registered §7; previously only in gt_name_check.csv).
- Final: minor (deferred): mirror rows (q1->q2 and q2->q1 when both columns are queries) fall in different within-lake folds and bootstrap clusters; FREYJA_BM SECONDARY: 1,236 of 1,478 positives have a positive mirror, 1,022 in another fold. The FREYJA_BM within-lake reference is optimistic and intervals may be narrow. Pre-registered grouping kept; caveat in README.
- Final: minor (deferred): sklearn 1.6.1 GroupKFold orders equal-size groups with a non-stable argsort; fold assignment could differ on another numpy build. Outer folds are saved in the prediction files; inner folds of (c) are not.
- Final: minor (deferred): latent edge cases not triggered by the data (duplicate profile keys: 0 in every lake; single-class fitting rows: never; non-finite features: 0).
- Final: minor (deferred): the §8 count of benchmarks whose ECE(c)−ECE(b) interval lies below/above/contains 0 is computed in report_tables.py, not evaluate.py.

- SANTOS Big profiled at the end for the timing chart only: 11,086 tables, 81,528 columns, 173.0 s, 0 errors, 245 tables without a text column (md5 1c3c041de79479bb5176729df3c55d35 OK).
- Post-hoc TUS sibling rerun: removing the sibling TUS lake from the leave-one-out pool changes PRIMARY ECE of (b) from 0.094 to 0.104 (TUS Small) and from 0.036 to 0.051 (TUS Big); (c) from 0.065 to 0.067 and from 0.043 to 0.048.
- TUS Big: the 282 GT columns present in the header but not profiled are all-null columns (FREYJA's profiler skips columns without a non-null value).
- SANTOS Small: of the 57 GT pairs naming a missing column, the missing columns are absent from their table's header (45 columns) or their table is absent from the lake (2 tables: minister_meetings_7, stockport_contracts_4).
- Post-hoc Brier skill reading added after seeing that, within the top-k, the median score of false candidates exceeds that of true joins on OmniMatch and TUS Small: ECE rewards a constant at the base rate, so `scripts/posthoc_brier_skill.py` reports 1 − Brier / (r(1 − r)) with the same bootstrap. Labelled post hoc; never used in summaries.
- Export (verified) run once on the final evaluation (all checks passed, 258 files), then rerun after the post-hoc and table files were added to results/.
