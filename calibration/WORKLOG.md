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
