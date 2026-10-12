
### Leave-one-out ECE [95% CI], PRIMARY, pool `all`; within-lake reference last

| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |
|---|---|---|---|---|---|
| FREYJA_BM | 0.664 [0.568, 0.753] | 0.102 [0.081, 0.129] | 0.517 [0.428, 0.602] | 0.034 [0.022, 0.068] | 0.028 [0.009, 0.068] |
| FREYJA_BM (held-out rows) | 0.541 [0.435, 0.671] | 0.140 [0.095, 0.207] | 0.482 [0.366, 0.605] | 0.100 [0.056, 0.185] | 0.043 [0.016, 0.098] |
| SANTOS Small | 0.573 [0.498, 0.646] | 0.094 [0.074, 0.141] | 0.056 [0.031, 0.111] | 0.060 [0.040, 0.113] | 0.015 [0.005, 0.032] |
| OmniMatch CR | 0.680 [0.617, 0.743] | 0.101 [0.078, 0.157] | 0.123 [0.088, 0.162] | 0.096 [0.075, 0.147] | 0.031 [0.020, 0.059] |
| OmniMatch CG | 0.672 [0.619, 0.728] | 0.093 [0.062, 0.143] | 0.090 [0.073, 0.124] | 0.101 [0.058, 0.124] | 0.038 [0.022, 0.067] |
| TUS Small | 0.625 [0.592, 0.655] | 0.104 [0.085, 0.136] | 0.067 [0.055, 0.092] | 0.059 [0.039, 0.093] | 0.011 [0.009, 0.023] |

### Leave-one-out ECE [95% CI], SECONDARY, pool `all`; within-lake reference last

| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |
|---|---|---|---|---|---|
| FREYJA_BM | 0.113 [0.107, 0.118] | 0.023 [0.021, 0.025] | 0.023 [0.020, 0.026] | 0.003 [0.003, 0.007] | 0.002 [0.001, 0.007] |
| FREYJA_BM (held-out rows) | 0.100 [0.098, 0.104] | 0.007 [0.005, 0.010] | 0.008 [0.006, 0.011] | 0.009 [0.007, 0.011] | 0.005 [0.002, 0.009] |
| SANTOS Small | 0.126 [0.126, 0.126] | 0.001 [0.000, 0.003] | 0.024 [0.012, 0.035] | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| OmniMatch CR | 0.118 [0.116, 0.119] | 0.015 [0.003, 0.029] | 0.004 [0.002, 0.006] | 0.001 [0.000, 0.011] | 0.000 [0.000, 0.001] |
| OmniMatch CG | 0.117 [0.115, 0.118] | 0.013 [0.003, 0.023] | 0.012 [0.009, 0.015] | 0.001 [0.000, 0.008] | 0.000 [0.000, 0.001] |
| TUS Small | 0.123 [0.123, 0.123] | 0.003 [0.003, 0.003] | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.001] |

### Leave-one-out ECE, PRIMARY, other pools

| held-out benchmark | pool | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|
| FREYJA_BM | no_freyja_bm | 0.664 [0.568, 0.753] | 0.102 [0.081, 0.129] | 0.517 [0.428, 0.602] |
| FREYJA_BM (held-out rows) | no_freyja_bm | 0.541 [0.435, 0.671] | 0.140 [0.095, 0.207] | 0.482 [0.366, 0.605] |
| FREYJA_BM | no_shared_origin | n/a | n/a | n/a |
| FREYJA_BM (held-out rows) | no_shared_origin | n/a | n/a | n/a |
| SANTOS Small | no_freyja_bm | 0.556 [0.482, 0.632] | 0.113 [0.080, 0.174] | 0.055 [0.045, 0.082] |
| SANTOS Small | no_shared_origin | 0.573 [0.498, 0.646] | 0.051 [0.031, 0.115] | 0.092 [0.050, 0.165] |
| OmniMatch CR | no_freyja_bm | 0.673 [0.607, 0.737] | 0.100 [0.078, 0.155] | 0.092 [0.064, 0.124] |
| OmniMatch CR | no_shared_origin | 0.680 [0.617, 0.743] | 0.187 [0.146, 0.233] | 0.188 [0.141, 0.228] |
| OmniMatch CG | no_freyja_bm | 0.665 [0.611, 0.723] | 0.090 [0.059, 0.140] | 0.091 [0.065, 0.118] |
| OmniMatch CG | no_shared_origin | 0.672 [0.619, 0.728] | 0.197 [0.161, 0.242] | 0.215 [0.181, 0.264] |
| TUS Small | no_freyja_bm | 0.603 [0.569, 0.634] | 0.112 [0.091, 0.145] | 0.071 [0.060, 0.086] |
| TUS Small | no_shared_origin | 0.625 [0.592, 0.655] | 0.155 [0.129, 0.178] | 0.101 [0.076, 0.140] |

### Paired difference ECE(c) − ECE(b), leave-one-out pool `all` [95% CI]

| held-out benchmark | PRIMARY | SECONDARY |
|---|---|---|
| FREYJA_BM | +0.415 [+0.314, +0.505] | +0.000 [-0.003, +0.003] |
| FREYJA_BM (held-out rows) | +0.342 [+0.198, +0.464] | +0.001 [-0.001, +0.004] |
| SANTOS Small | -0.037 [-0.081, +0.018] | +0.022 [+0.011, +0.033] |
| OmniMatch CR | +0.022 [-0.048, +0.060] | -0.011 [-0.024, -0.001] |
| OmniMatch CG | -0.003 [-0.040, +0.031] | -0.001 [-0.010, +0.007] |
| TUS Small | -0.037 [-0.068, -0.008] | -0.003 [-0.003, -0.002] |

Reading (c) of PREREGISTRATION.md §8 — benchmarks (FREYJA_BM on all rows) whose 95% interval of ECE(c) − ECE(b), leave-one-out pool `all`, lies below 0 / contains 0 / lies above 0:

- PRIMARY: below 0 ((c) better): 1 (TUS Small); contains 0: 3 (SANTOS Small, OmniMatch CR, OmniMatch CG); above 0 ((b) better): 1 (FREYJA_BM)
- SECONDARY: below 0 ((c) better): 2 (OmniMatch CR, TUS Small); contains 0: 2 (FREYJA_BM, OmniMatch CG); above 0 ((b) better): 1 (SANTOS Small)

### Summaries (median [min, max] of ECE)

| design | shared-origin variant | FREYJA_BM rows | set | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|---|---|
| leave_one_out | all | all | PRIMARY | 0.664 [0.573, 0.680] (n=5) | 0.101 [0.093, 0.104] (n=5) | 0.090 [0.056, 0.517] (n=5) |
| leave_one_out | excluded_as_fitting | all | PRIMARY | 0.649 [0.573, 0.680] (n=4) | 0.171 [0.051, 0.197] (n=4) | 0.144 [0.092, 0.215] (n=4) |
| leave_one_out | excluded_as_evaluation | all | PRIMARY | 0.664 [0.664, 0.664] (n=1) | 0.102 [0.102, 0.102] (n=1) | 0.517 [0.517, 0.517] (n=1) |
| leave_one_out | excluded_as_both | all | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | all | PRIMARY | 0.664 [0.556, 0.673] (n=5) | 0.102 [0.090, 0.113] (n=5) | 0.091 [0.055, 0.517] (n=5) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | all | PRIMARY | 0.664 [0.664, 0.664] (n=1) | 0.102 [0.102, 0.102] (n=1) | 0.517 [0.517, 0.517] (n=1) |
| pairwise | all | all | PRIMARY | 0.666 [0.554, 0.680] (n=20) | 0.124 [0.051, 0.197] (n=20) | 0.128 [0.026, 0.448] (n=20) |
| pairwise | excluded_as_fitting | all | PRIMARY | 0.649 [0.573, 0.680] (n=4) | 0.171 [0.051, 0.197] (n=4) | 0.144 [0.092, 0.215] (n=4) |
| pairwise | excluded_as_evaluation | all | PRIMARY | 0.669 [0.663, 0.671] (n=4) | 0.116 [0.085, 0.160] (n=4) | 0.414 [0.357, 0.448] (n=4) |
| pairwise | excluded_as_both | all | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | all | PRIMARY | – | 0.060 [0.034, 0.101] (n=5) | 0.028 [0.011, 0.038] (n=5) |
| within_lake | excluded_as_evaluation | all | PRIMARY | – | 0.034 [0.034, 0.034] (n=1) | 0.028 [0.028, 0.028] (n=1) |
| leave_one_out | all | all | SECONDARY | 0.118 [0.113, 0.126] (n=5) | 0.013 [0.001, 0.023] (n=5) | 0.012 [0.000, 0.024] (n=5) |
| leave_one_out | excluded_as_fitting | all | SECONDARY | 0.120 [0.117, 0.126] (n=4) | 0.025 [0.010, 0.040] (n=4) | 0.006 [0.001, 0.008] (n=4) |
| leave_one_out | excluded_as_evaluation | all | SECONDARY | 0.113 [0.113, 0.113] (n=1) | 0.023 [0.023, 0.023] (n=1) | 0.023 [0.023, 0.023] (n=1) |
| leave_one_out | excluded_as_both | all | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | all | SECONDARY | 0.106 [0.098, 0.113] (n=5) | 0.011 [0.001, 0.023] (n=5) | 0.007 [0.000, 0.023] (n=5) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | all | SECONDARY | 0.113 [0.113, 0.113] (n=1) | 0.023 [0.023, 0.023] (n=1) | 0.023 [0.023, 0.023] (n=1) |
| pairwise | all | all | SECONDARY | 0.097 [0.002, 0.126] (n=20) | 0.006 [0.000, 0.040] (n=20) | 0.004 [0.000, 0.031] (n=20) |
| pairwise | excluded_as_fitting | all | SECONDARY | 0.120 [0.117, 0.126] (n=4) | 0.025 [0.010, 0.040] (n=4) | 0.006 [0.001, 0.008] (n=4) |
| pairwise | excluded_as_evaluation | all | SECONDARY | 0.093 [0.038, 0.113] (n=4) | 0.029 [0.011, 0.029] (n=4) | 0.029 [0.018, 0.031] (n=4) |
| pairwise | excluded_as_both | all | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | all | SECONDARY | – | 0.001 [0.000, 0.003] (n=5) | 0.000 [0.000, 0.002] (n=5) |
| within_lake | excluded_as_evaluation | all | SECONDARY | – | 0.003 [0.003, 0.003] (n=1) | 0.002 [0.002, 0.002] (n=1) |
| leave_one_out | all | heldout_rows | PRIMARY | 0.625 [0.541, 0.680] (n=5) | 0.101 [0.093, 0.140] (n=5) | 0.090 [0.056, 0.482] (n=5) |
| leave_one_out | excluded_as_fitting | heldout_rows | PRIMARY | 0.649 [0.573, 0.680] (n=4) | 0.171 [0.051, 0.197] (n=4) | 0.144 [0.092, 0.215] (n=4) |
| leave_one_out | excluded_as_evaluation | heldout_rows | PRIMARY | 0.541 [0.541, 0.541] (n=1) | 0.140 [0.140, 0.140] (n=1) | 0.482 [0.482, 0.482] (n=1) |
| leave_one_out | excluded_as_both | heldout_rows | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | heldout_rows | PRIMARY | 0.603 [0.541, 0.673] (n=5) | 0.112 [0.090, 0.140] (n=5) | 0.091 [0.055, 0.482] (n=5) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | heldout_rows | PRIMARY | 0.541 [0.541, 0.541] (n=1) | 0.140 [0.140, 0.140] (n=1) | 0.482 [0.482, 0.482] (n=1) |
| pairwise | all | heldout_rows | PRIMARY | 0.608 [0.541, 0.680] (n=20) | 0.137 [0.051, 0.197] (n=20) | 0.128 [0.026, 0.428] (n=20) |
| pairwise | excluded_as_fitting | heldout_rows | PRIMARY | 0.649 [0.573, 0.680] (n=4) | 0.171 [0.051, 0.197] (n=4) | 0.144 [0.092, 0.215] (n=4) |
| pairwise | excluded_as_evaluation | heldout_rows | PRIMARY | 0.546 [0.541, 0.547] (n=4) | 0.151 [0.109, 0.171] (n=4) | 0.416 [0.352, 0.428] (n=4) |
| pairwise | excluded_as_both | heldout_rows | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | heldout_rows | PRIMARY | – | 0.096 [0.059, 0.101] (n=5) | 0.031 [0.011, 0.043] (n=5) |
| within_lake | excluded_as_evaluation | heldout_rows | PRIMARY | – | 0.100 [0.100, 0.100] (n=1) | 0.043 [0.043, 0.043] (n=1) |
| leave_one_out | all | heldout_rows | SECONDARY | 0.118 [0.100, 0.126] (n=5) | 0.007 [0.001, 0.015] (n=5) | 0.008 [0.000, 0.024] (n=5) |
| leave_one_out | excluded_as_fitting | heldout_rows | SECONDARY | 0.120 [0.117, 0.126] (n=4) | 0.025 [0.010, 0.040] (n=4) | 0.006 [0.001, 0.008] (n=4) |
| leave_one_out | excluded_as_evaluation | heldout_rows | SECONDARY | 0.100 [0.100, 0.100] (n=1) | 0.007 [0.007, 0.007] (n=1) | 0.008 [0.008, 0.008] (n=1) |
| leave_one_out | excluded_as_both | heldout_rows | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | heldout_rows | SECONDARY | 0.105 [0.098, 0.109] (n=5) | 0.007 [0.001, 0.013] (n=5) | 0.007 [0.000, 0.008] (n=5) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | heldout_rows | SECONDARY | 0.100 [0.100, 0.100] (n=1) | 0.007 [0.007, 0.007] (n=1) | 0.008 [0.008, 0.008] (n=1) |
| pairwise | all | heldout_rows | SECONDARY | 0.095 [0.002, 0.126] (n=20) | 0.005 [0.000, 0.040] (n=20) | 0.004 [0.000, 0.011] (n=20) |
| pairwise | excluded_as_fitting | heldout_rows | SECONDARY | 0.120 [0.117, 0.126] (n=4) | 0.025 [0.010, 0.040] (n=4) | 0.006 [0.001, 0.008] (n=4) |
| pairwise | excluded_as_evaluation | heldout_rows | SECONDARY | 0.079 [0.013, 0.101] (n=4) | 0.010 [0.007, 0.010] (n=4) | 0.010 [0.009, 0.011] (n=4) |
| pairwise | excluded_as_both | heldout_rows | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | heldout_rows | SECONDARY | – | 0.001 [0.000, 0.009] (n=5) | 0.000 [0.000, 0.005] (n=5) |
| within_lake | excluded_as_evaluation | heldout_rows | SECONDARY | – | 0.009 [0.009, 0.009] (n=1) | 0.005 [0.005, 0.005] (n=1) |

### Stratified reading: leave-one-out pool `all`, PRIMARY

| held-out benchmark | stratum | rows | positive rate | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|---|---|
| FREYJA_BM | same_origin | 9 | 0.000 | 0.619 [0.323, 0.838] | 0.905 [0.848, 0.944] | 0.000 [0.000, 0.000] |
| FREYJA_BM | different_origin | 491 | 0.935 | 0.688 [0.600, 0.767] | 0.112 [0.090, 0.135] | 0.524 [0.436, 0.618] |
| FREYJA_BM (held-out rows) | same_origin | 9 | 0.000 | 0.619 [0.323, 0.838] | 0.905 [0.848, 0.944] | 0.000 [0.000, 0.000] |
| FREYJA_BM (held-out rows) | different_origin | 171 | 0.819 | 0.591 [0.469, 0.702] | 0.110 [0.084, 0.178] | 0.487 [0.384, 0.638] |
| SANTOS Small | same_origin | 393 | 0.939 | 0.610 [0.528, 0.690] | 0.117 [0.097, 0.171] | 0.039 [0.032, 0.080] |
| SANTOS Small | different_origin | 107 | 0.607 | 0.438 [0.319, 0.575] | 0.110 [0.092, 0.218] | 0.242 [0.112, 0.375] |
| OmniMatch CR | same_origin | 1313 | 0.881 | 0.791 [0.753, 0.827] | 0.043 [0.031, 0.067] | 0.093 [0.064, 0.122] |
| OmniMatch CR | different_origin | 187 | 0.000 | 0.099 [0.049, 0.152] | 0.847 [0.847, 0.848] | 0.406 [0.214, 0.615] |
| OmniMatch CG | same_origin | 1356 | 0.846 | 0.750 [0.713, 0.783] | 0.031 [0.023, 0.050] | 0.077 [0.061, 0.098] |
| OmniMatch CG | different_origin | 144 | 0.000 | 0.060 [0.032, 0.102] | 0.848 [0.848, 0.848] | 0.421 [0.227, 0.609] |
| TUS Small | same_origin | 6000 | 0.891 | 0.625 [0.592, 0.655] | 0.104 [0.085, 0.136] | 0.067 [0.055, 0.092] |
| TUS Small | different_origin | 0 | – | no rows | no rows | no rows |

### Benchmarks

| benchmark | tables | profiled columns | profiling (s) | queries | k | top-k rows | positive rate top-k | positive rate all | same-origin share of positives | GT pairs naming a missing column | P@k ours | P@k models.ipynb | P@k scores.txt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FREYJA_BM | 160 | 680 | 2.4 | 50 | 10 | 500 | 0.918 | 0.0435 | 0.000 | 0 of 1478 | 0.926 | 0.924 | 0.924 |
| SANTOS Small | 550 | 4301 | 9.7 | 50 | 10 | 500 | 0.868 | 0.0027 | 0.827 | 57 of 645 | 0.892 | 0.928 | 0.916 |
| OmniMatch CR | 480 | 1970 | 3.2 | 50 | 30 | 1500 | 0.771 | 0.0177 | 1.000 | 0 of 1742 | 0.748 | 0.609 | 0.547 |
| OmniMatch CG | 440 | 1938 | 3.5 | 50 | 30 | 1500 | 0.765 | 0.0165 | 1.000 | 0 of 1597 | 0.743 | 0.613 | 0.530 |
| TUS Small | 1526 | 12625 | 27.9 | 100 | 60 | 6000 | 0.891 | 0.0063 | 1.000 | 1665 of 9651 | 0.893 | 0.890 | 0.884 |
