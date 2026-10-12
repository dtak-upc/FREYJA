# Numbers for the B2 section

The table is generated from `results/` by `scripts/report_tables.py` (`results/b2_table.md`).

**Columns:**
- ECE: expected calibration error, 10 equal-mass bins, [95% cluster-bootstrap interval over query columns].
- Top-k: the k candidates FREYJA returns per query (k = 10, 10, 30, 30, 60, 60).
- Estimators: (a) raw score min-max scaled; (b) isotonic map on the score; (c) calibrated classifier on the 22 profile-difference features.
- Within-lake: 5-fold cross-validation grouped by query column.
- Leave-one-out: fitted on the pooled other benchmarks.
- Profiling: wall time with FREYJA's profiler, 8 workers, Apple M3 Pro, one run.

**FREYJA_BM is the score model's training lake, never unseen.** Its "held-out rows" exclude the model's training pairs.

| benchmark | tables | columns | profiling (s) | positive rate in top-k | within-lake ECE (b) | within-lake ECE (c) | leave-one-out ECE (a) | leave-one-out ECE (b) | leave-one-out ECE (c) |
|---|---|---|---|---|---|---|---|---|---|
| FREYJA_BM | 160 | 680 | 2.4 | 0.918 | 0.034 [0.022, 0.068] | 0.028 [0.009, 0.068] | 0.671 [0.577, 0.758] | 0.102 [0.080, 0.129] | 0.425 [0.322, 0.521] |
| FREYJA_BM (held-out rows) | ″ | ″ | ″ | 0.778 | 0.100 [0.056, 0.185] | 0.043 [0.016, 0.098] | 0.542 [0.439, 0.674] | 0.139 [0.094, 0.205] | 0.376 [0.262, 0.531] |
| SANTOS Small | 550 | 4301 | 9.7 | 0.868 | 0.060 [0.040, 0.113] | 0.015 [0.005, 0.032] | 0.573 [0.498, 0.646] | 0.070 [0.062, 0.134] | 0.019 [0.017, 0.047] |
| OmniMatch CR | 480 | 1970 | 3.2 | 0.771 | 0.096 [0.075, 0.147] | 0.031 [0.020, 0.059] | 0.680 [0.616, 0.742] | 0.100 [0.077, 0.156] | 0.111 [0.082, 0.173] |
| OmniMatch CG | 440 | 1938 | 3.5 | 0.765 | 0.101 [0.058, 0.124] | 0.038 [0.022, 0.067] | 0.672 [0.618, 0.728] | 0.089 [0.059, 0.139] | 0.098 [0.077, 0.132] |
| TUS Small | 1526 | 12625 | 27.9 | 0.891 | 0.059 [0.039, 0.093] | 0.011 [0.009, 0.023] | 0.624 [0.592, 0.654] | 0.094 [0.080, 0.126] | 0.065 [0.042, 0.081] |
| TUS Big | 5045 | 49702 | 80.9 | 0.896 | 0.067 [0.045, 0.106] | 0.015 [0.010, 0.025] | 0.445 [0.397, 0.493] | 0.036 [0.032, 0.094] | 0.043 [0.034, 0.077] |
| SANTOS Big (profiling only, no labels) | 11086 | 81528 | 173.0 | – | – | – | – | – | – |

**Context for the sentences:**
- Five of the six labelled benchmarks are built by splitting a common origin: SANTOS Small, TUS Small and Big, OmniMatch CR and CG. In them, 83–100% of labelled joins are same-origin pairs. Excluding them as both fitting and evaluation data leaves no unseen benchmark.
- **Post hoc (not pre-registered):** within the top-k, the score-based confidence (b) is barely more informative than a constant at the positive rate. Its Brier skill is −0.07 to 0.37 in leave-one-out, and ≤ 0.05 within-lake on OmniMatch CR, CG, TUS Small and Big.
- **Stratified reading (pre-registered):** on top-k candidates from another origin, the transferred (b) has ECE 0.84 on OmniMatch CR and CG (0% labelled joins) and 0.56 on TUS Big (22%).

## Candidate sentences

1. *"Out of the box, FREYJA's score ranks well but is not a probability. Scaled to [0, 1], it understates how often top-ranked candidates are true joins: calibration error 0.45–0.68 on six benchmarks."* (32 words)
   - Rests on: leave-one-out (a), top-k, all six benchmarks, including FREYJA_BM (the training lake) and the five shared-origin ones. Every lower bound is ≥ 0.39. It depends on min-max scaling (any monotone map can do better; that is sentence 2). "Ranks well" = our precision@k 0.74–0.93, which reproduces the published values within 0.01 on three benchmarks.
   - Fragility: low.
   - **Label: safe.**
2. *"Fitted on labelled pairs from the same lake, a simple monotone map turns the score into a calibrated confidence. Calibration error on the top-ranked candidates drops to 0.03–0.10 on six benchmarks."* (31 words)
   - Rests on: within-lake 5-fold cross-validation, (b), six benchmarks. FREYJA_BM's 0.034 is optimistic: it is the training lake and mirror pairs cross folds (0.100 on its held-out rows).
   - Fragility: calibrated is not the same as informative. Post hoc, on four of six benchmarks this confidence barely beats predicting the lake's positive rate (Brier skill −0.02 to 0.05). Do not write "useful" or "discriminative".
   - **Label: needs the caveat.**
3. *"Fitted on five benchmarks and applied to a sixth, the same map keeps top-k calibration error between 0.04 and 0.10. But five of these six benchmarks split tables from a common source. So this does not yet show transfer to independent deployments."* (42 words)
   - Rests on: leave-one-out (b), pool = the other five, six held-out benchmarks.
   - Fragility:
     - The only non-shared-origin held-out lake is FREYJA_BM, the training lake.
     - The TUS pools contain the sibling TUS lake. Removing it (post hoc) gives 0.104 and 0.051, at the edge of the range.
     - Fitted only on FREYJA_BM, the range widens to 0.05–0.20.
     - On candidates from another origin, the transferred map fails (ECE 0.56–0.84).
   - **Label: needs the caveat** (the caveat is in the sentence; do not quote the first sentence alone).
4. *"Public join benchmarks cannot yet test reliability across independent sources. In five of the six we used, 83–100% of labelled joins link pieces cut from the same source table."* (29 words)
   - Rests on: the pre-registered origin name rules applied to the labelled positives present in each lake: SANTOS Small 82.7%, TUS Big 96.1%, TUS Small and both OmniMatch lakes 100%, FREYJA_BM 0%.
   - Fragility: "public join benchmarks" means the six we used. D3L was unavailable and SANTOS Big has no labels. The name rules may miss some same-origin tables, so the shares are lower bounds.
   - **Label: safe.**
5. *"A confidence learned from 22 profile features is better calibrated within a lake (error 0.01–0.04). It does not transfer better than one learned from the score. On the one benchmark of independent tables, it is worse: 0.43 against 0.10."* (39 words)
   - Rests on:
     - within-lake (c): 0.011–0.038 on six;
     - leave-one-out paired difference (c) − (b): better on 2, indistinguishable on 3, worse on FREYJA_BM (+0.32 [+0.21, +0.42]; held-out rows +0.24 [+0.11, +0.39]).
   - Fragility:
     - The "independent" benchmark is a single lake, and it is the score model's training lake, which favours (b).
     - Post hoc, where (c) does transfer it is the more informative confidence (Brier skill 0.43–0.75 on SANTOS Small and both TUS lakes).
   - **Label: needs the caveat.**

**Do not use:** the hypothesis as phrased, *"confidences learned from lightweight evidence (profiles) are reliable on deployments the model never saw"*. In these data:
- no unseen independent benchmark remains after the pre-registered exclusion;
- the only independent lake is the training lake;
- on that lake, the profile-feature confidence is the one that fails.

The ranking claim, "the ranking carries over", remains supported. Our precision@k matches the published values within 0.01 on FREYJA_BM and both TUS lakes. It is lower on SANTOS Small and higher on OmniMatch; see the README.
