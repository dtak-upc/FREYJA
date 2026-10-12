
### Leave-one-out ECE [95% CI], PRIMARY, pool `all`; within-lake reference last

| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |
|---|---|---|---|---|---|
| FREYJA_BM | 0.671 [0.577, 0.758] | 0.102 [0.080, 0.129] | 0.425 [0.322, 0.521] | 0.034 [0.022, 0.068] | 0.028 [0.009, 0.068] |
| FREYJA_BM (held-out rows) | 0.542 [0.439, 0.674] | 0.139 [0.094, 0.205] | 0.376 [0.262, 0.531] | 0.100 [0.056, 0.185] | 0.043 [0.016, 0.098] |
| SANTOS Small | 0.573 [0.498, 0.646] | 0.070 [0.062, 0.134] | 0.019 [0.017, 0.047] | 0.060 [0.040, 0.113] | 0.015 [0.005, 0.032] |
| OmniMatch CR | 0.680 [0.616, 0.742] | 0.100 [0.077, 0.156] | 0.111 [0.082, 0.173] | 0.096 [0.075, 0.147] | 0.031 [0.020, 0.059] |
| OmniMatch CG | 0.672 [0.618, 0.728] | 0.089 [0.059, 0.139] | 0.098 [0.077, 0.132] | 0.101 [0.058, 0.124] | 0.038 [0.022, 0.067] |
| TUS Small | 0.624 [0.592, 0.654] | 0.094 [0.080, 0.126] | 0.065 [0.042, 0.081] | 0.059 [0.039, 0.093] | 0.011 [0.009, 0.023] |
| TUS Big | 0.445 [0.397, 0.493] | 0.036 [0.032, 0.094] | 0.043 [0.034, 0.077] | 0.067 [0.045, 0.106] | 0.015 [0.010, 0.025] |

### Leave-one-out ECE [95% CI], SECONDARY, pool `all`; within-lake reference last

| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |
|---|---|---|---|---|---|
| FREYJA_BM | 0.142 [0.135, 0.147] | 0.020 [0.019, 0.023] | 0.026 [0.024, 0.028] | 0.003 [0.003, 0.007] | 0.002 [0.001, 0.007] |
| FREYJA_BM (held-out rows) | 0.136 [0.132, 0.139] | 0.007 [0.004, 0.010] | 0.004 [0.003, 0.007] | 0.009 [0.007, 0.011] | 0.005 [0.002, 0.009] |
| SANTOS Small | 0.141 [0.141, 0.142] | 0.006 [0.005, 0.007] | 0.008 [0.007, 0.010] | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| OmniMatch CR | 0.130 [0.129, 0.131] | 0.014 [0.007, 0.026] | 0.003 [0.002, 0.007] | 0.001 [0.000, 0.011] | 0.000 [0.000, 0.001] |
| OmniMatch CG | 0.129 [0.129, 0.131] | 0.012 [0.007, 0.021] | 0.004 [0.002, 0.006] | 0.001 [0.000, 0.008] | 0.000 [0.000, 0.001] |
| TUS Small | 0.138 [0.138, 0.138] | 0.006 [0.006, 0.006] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| TUS Big | 0.113 [0.109, 0.117] | 0.006 [0.004, 0.010] | 0.016 [0.010, 0.022] | 0.002 [0.003, 0.007] | 0.003 [0.001, 0.012] |

### Leave-one-out ECE, PRIMARY, other pools

| held-out benchmark | pool | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|
| FREYJA_BM | no_freyja_bm | 0.671 [0.577, 0.758] | 0.102 [0.080, 0.129] | 0.425 [0.322, 0.521] |
| FREYJA_BM (held-out rows) | no_freyja_bm | 0.542 [0.439, 0.674] | 0.139 [0.094, 0.205] | 0.376 [0.262, 0.531] |
| FREYJA_BM | no_shared_origin | n/a | n/a | n/a |
| FREYJA_BM (held-out rows) | no_shared_origin | n/a | n/a | n/a |
| SANTOS Small | no_freyja_bm | 0.557 [0.484, 0.632] | 0.073 [0.062, 0.134] | 0.017 [0.016, 0.047] |
| SANTOS Small | no_shared_origin | 0.573 [0.498, 0.646] | 0.051 [0.031, 0.115] | 0.092 [0.050, 0.165] |
| OmniMatch CR | no_freyja_bm | 0.675 [0.610, 0.739] | 0.099 [0.077, 0.154] | 0.068 [0.044, 0.098] |
| OmniMatch CR | no_shared_origin | 0.680 [0.617, 0.743] | 0.187 [0.146, 0.233] | 0.188 [0.141, 0.228] |
| OmniMatch CG | no_freyja_bm | 0.667 [0.613, 0.724] | 0.087 [0.057, 0.136] | 0.117 [0.089, 0.149] |
| OmniMatch CG | no_shared_origin | 0.672 [0.619, 0.728] | 0.197 [0.161, 0.242] | 0.215 [0.181, 0.264] |
| TUS Small | no_freyja_bm | 0.611 [0.578, 0.641] | 0.098 [0.083, 0.129] | 0.048 [0.036, 0.066] |
| TUS Small | no_shared_origin | 0.625 [0.592, 0.655] | 0.155 [0.129, 0.178] | 0.101 [0.076, 0.140] |
| TUS Big | no_freyja_bm | 0.408 [0.359, 0.458] | 0.046 [0.033, 0.094] | 0.128 [0.098, 0.160] |
| TUS Big | no_shared_origin | 0.445 [0.397, 0.493] | 0.071 [0.043, 0.120] | 0.107 [0.069, 0.152] |

### Paired difference ECE(c) − ECE(b), leave-one-out pool `all` [95% CI]

| held-out benchmark | PRIMARY | SECONDARY |
|---|---|---|
| FREYJA_BM | +0.323 [+0.208, +0.419] | +0.006 [+0.002, +0.009] |
| FREYJA_BM (held-out rows) | +0.237 [+0.111, +0.394] | -0.003 [-0.004, +0.000] |
| SANTOS Small | -0.051 [-0.104, -0.026] | +0.002 [+0.001, +0.004] |
| OmniMatch CR | +0.011 [-0.053, +0.076] | -0.011 [-0.020, -0.004] |
| OmniMatch CG | +0.008 [-0.035, +0.042] | -0.008 [-0.017, -0.003] |
| TUS Small | -0.029 [-0.071, -0.010] | -0.005 [-0.006, -0.005] |
| TUS Big | +0.006 [-0.045, +0.027] | +0.010 [+0.003, +0.015] |

Reading (c) of PREREGISTRATION.md §8 — benchmarks (FREYJA_BM on all rows) whose 95% interval of ECE(c) − ECE(b), leave-one-out pool `all`, lies below 0 / contains 0 / lies above 0:

- PRIMARY: below 0 ((c) better): 2 (SANTOS Small, TUS Small); contains 0: 3 (OmniMatch CR, OmniMatch CG, TUS Big); above 0 ((b) better): 1 (FREYJA_BM)
- SECONDARY: below 0 ((c) better): 3 (OmniMatch CR, OmniMatch CG, TUS Small); contains 0: 0 (none); above 0 ((b) better): 3 (FREYJA_BM, SANTOS Small, TUS Big)

### Summaries (median [min, max] of ECE)

| design | shared-origin variant | FREYJA_BM rows | set | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|---|---|
| leave_one_out | all | all | PRIMARY | 0.648 [0.445, 0.680] (n=6) | 0.092 [0.036, 0.102] (n=6) | 0.081 [0.019, 0.425] (n=6) |
| leave_one_out | excluded_as_fitting | all | PRIMARY | 0.625 [0.445, 0.680] (n=5) | 0.155 [0.051, 0.197] (n=5) | 0.107 [0.092, 0.215] (n=5) |
| leave_one_out | excluded_as_evaluation | all | PRIMARY | 0.671 [0.671, 0.671] (n=1) | 0.102 [0.102, 0.102] (n=1) | 0.425 [0.425, 0.425] (n=1) |
| leave_one_out | excluded_as_both | all | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | all | PRIMARY | 0.639 [0.408, 0.675] (n=6) | 0.093 [0.046, 0.102] (n=6) | 0.093 [0.017, 0.425] (n=6) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | all | PRIMARY | 0.671 [0.671, 0.671] (n=1) | 0.102 [0.102, 0.102] (n=1) | 0.425 [0.425, 0.425] (n=1) |
| pairwise | all | all | PRIMARY | 0.644 [0.404, 0.680] (n=30) | 0.108 [0.046, 0.197] (n=30) | 0.121 [0.026, 0.448] (n=30) |
| pairwise | excluded_as_fitting | all | PRIMARY | 0.625 [0.445, 0.680] (n=5) | 0.155 [0.051, 0.197] (n=5) | 0.107 [0.092, 0.215] (n=5) |
| pairwise | excluded_as_evaluation | all | PRIMARY | 0.670 [0.663, 0.671] (n=5) | 0.113 [0.085, 0.160] (n=5) | 0.384 [0.331, 0.448] (n=5) |
| pairwise | excluded_as_both | all | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | all | PRIMARY | – | 0.063 [0.034, 0.101] (n=6) | 0.021 [0.011, 0.038] (n=6) |
| within_lake | excluded_as_evaluation | all | PRIMARY | – | 0.034 [0.034, 0.034] (n=1) | 0.028 [0.028, 0.028] (n=1) |
| leave_one_out | all | all | SECONDARY | 0.134 [0.113, 0.142] (n=6) | 0.009 [0.006, 0.020] (n=6) | 0.006 [0.001, 0.026] (n=6) |
| leave_one_out | excluded_as_fitting | all | SECONDARY | 0.118 [0.113, 0.126] (n=5) | 0.018 [0.010, 0.040] (n=5) | 0.008 [0.001, 0.009] (n=5) |
| leave_one_out | excluded_as_evaluation | all | SECONDARY | 0.142 [0.142, 0.142] (n=1) | 0.020 [0.020, 0.020] (n=1) | 0.026 [0.026, 0.026] (n=1) |
| leave_one_out | excluded_as_both | all | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | all | SECONDARY | 0.139 [0.099, 0.148] (n=6) | 0.009 [0.006, 0.020] (n=6) | 0.009 [0.000, 0.026] (n=6) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | all | SECONDARY | 0.142 [0.142, 0.142] (n=1) | 0.020 [0.020, 0.020] (n=1) | 0.026 [0.026, 0.026] (n=1) |
| pairwise | all | all | SECONDARY | 0.101 [0.002, 0.148] (n=30) | 0.009 [0.000, 0.040] (n=30) | 0.005 [0.000, 0.031] (n=30) |
| pairwise | excluded_as_fitting | all | SECONDARY | 0.118 [0.113, 0.126] (n=5) | 0.018 [0.010, 0.040] (n=5) | 0.008 [0.001, 0.009] (n=5) |
| pairwise | excluded_as_evaluation | all | SECONDARY | 0.102 [0.038, 0.142] (n=5) | 0.029 [0.011, 0.029] (n=5) | 0.027 [0.012, 0.031] (n=5) |
| pairwise | excluded_as_both | all | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | all | SECONDARY | – | 0.001 [0.000, 0.003] (n=6) | 0.000 [0.000, 0.003] (n=6) |
| within_lake | excluded_as_evaluation | all | SECONDARY | – | 0.003 [0.003, 0.003] (n=1) | 0.002 [0.002, 0.002] (n=1) |
| leave_one_out | all | heldout_rows | PRIMARY | 0.598 [0.445, 0.680] (n=6) | 0.092 [0.036, 0.139] (n=6) | 0.081 [0.019, 0.376] (n=6) |
| leave_one_out | excluded_as_fitting | heldout_rows | PRIMARY | 0.625 [0.445, 0.680] (n=5) | 0.155 [0.051, 0.197] (n=5) | 0.107 [0.092, 0.215] (n=5) |
| leave_one_out | excluded_as_evaluation | heldout_rows | PRIMARY | 0.542 [0.542, 0.542] (n=1) | 0.139 [0.139, 0.139] (n=1) | 0.376 [0.376, 0.376] (n=1) |
| leave_one_out | excluded_as_both | heldout_rows | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | heldout_rows | PRIMARY | 0.584 [0.408, 0.675] (n=6) | 0.093 [0.046, 0.139] (n=6) | 0.093 [0.017, 0.376] (n=6) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | heldout_rows | PRIMARY | 0.542 [0.542, 0.542] (n=1) | 0.139 [0.139, 0.139] (n=1) | 0.376 [0.376, 0.376] (n=1) |
| pairwise | all | heldout_rows | PRIMARY | 0.587 [0.404, 0.680] (n=30) | 0.109 [0.046, 0.197] (n=30) | 0.121 [0.026, 0.428] (n=30) |
| pairwise | excluded_as_fitting | heldout_rows | PRIMARY | 0.625 [0.445, 0.680] (n=5) | 0.155 [0.051, 0.197] (n=5) | 0.107 [0.092, 0.215] (n=5) |
| pairwise | excluded_as_evaluation | heldout_rows | PRIMARY | 0.546 [0.541, 0.547] (n=5) | 0.144 [0.100, 0.171] (n=5) | 0.408 [0.352, 0.428] (n=5) |
| pairwise | excluded_as_both | heldout_rows | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | heldout_rows | PRIMARY | – | 0.082 [0.059, 0.101] (n=6) | 0.023 [0.011, 0.043] (n=6) |
| within_lake | excluded_as_evaluation | heldout_rows | PRIMARY | – | 0.100 [0.100, 0.100] (n=1) | 0.043 [0.043, 0.043] (n=1) |
| leave_one_out | all | heldout_rows | SECONDARY | 0.133 [0.113, 0.141] (n=6) | 0.007 [0.006, 0.014] (n=6) | 0.004 [0.001, 0.016] (n=6) |
| leave_one_out | excluded_as_fitting | heldout_rows | SECONDARY | 0.118 [0.113, 0.126] (n=5) | 0.018 [0.010, 0.040] (n=5) | 0.008 [0.001, 0.009] (n=5) |
| leave_one_out | excluded_as_evaluation | heldout_rows | SECONDARY | 0.136 [0.136, 0.136] (n=1) | 0.007 [0.007, 0.007] (n=1) | 0.004 [0.004, 0.004] (n=1) |
| leave_one_out | excluded_as_both | heldout_rows | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | heldout_rows | SECONDARY | 0.136 [0.099, 0.148] (n=6) | 0.007 [0.006, 0.014] (n=6) | 0.004 [0.000, 0.022] (n=6) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | heldout_rows | SECONDARY | 0.136 [0.136, 0.136] (n=1) | 0.007 [0.007, 0.007] (n=1) | 0.004 [0.004, 0.004] (n=1) |
| pairwise | all | heldout_rows | SECONDARY | 0.100 [0.002, 0.148] (n=30) | 0.008 [0.000, 0.040] (n=30) | 0.005 [0.000, 0.013] (n=30) |
| pairwise | excluded_as_fitting | heldout_rows | SECONDARY | 0.118 [0.113, 0.126] (n=5) | 0.018 [0.010, 0.040] (n=5) | 0.008 [0.001, 0.009] (n=5) |
| pairwise | excluded_as_evaluation | heldout_rows | SECONDARY | 0.088 [0.013, 0.136] (n=5) | 0.010 [0.007, 0.010] (n=5) | 0.010 [0.009, 0.011] (n=5) |
| pairwise | excluded_as_both | heldout_rows | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | heldout_rows | SECONDARY | – | 0.001 [0.000, 0.009] (n=6) | 0.000 [0.000, 0.005] (n=6) |
| within_lake | excluded_as_evaluation | heldout_rows | SECONDARY | – | 0.009 [0.009, 0.009] (n=1) | 0.005 [0.005, 0.005] (n=1) |

### Stratified reading: leave-one-out pool `all`, PRIMARY

| held-out benchmark | stratum | rows | positive rate | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|---|---|
| FREYJA_BM | same_origin | 9 | 0.000 | 0.600 [0.313, 0.813] | 0.901 [0.847, 0.938] | 0.109 [0.004, 0.259] |
| FREYJA_BM | different_origin | 491 | 0.935 | 0.694 [0.608, 0.772] | 0.112 [0.090, 0.135] | 0.432 [0.325, 0.531] |
| FREYJA_BM (held-out rows) | same_origin | 9 | 0.000 | 0.600 [0.313, 0.813] | 0.901 [0.847, 0.938] | 0.109 [0.004, 0.259] |
| FREYJA_BM (held-out rows) | different_origin | 171 | 0.819 | 0.596 [0.478, 0.706] | 0.110 [0.084, 0.177] | 0.394 [0.268, 0.556] |
| SANTOS Small | same_origin | 393 | 0.939 | 0.609 [0.528, 0.689] | 0.118 [0.086, 0.157] | 0.023 [0.017, 0.047] |
| SANTOS Small | different_origin | 107 | 0.607 | 0.438 [0.319, 0.575] | 0.104 [0.084, 0.208] | 0.072 [0.031, 0.155] |
| OmniMatch CR | same_origin | 1313 | 0.881 | 0.791 [0.753, 0.827] | 0.044 [0.033, 0.071] | 0.122 [0.082, 0.177] |
| OmniMatch CR | different_origin | 187 | 0.000 | 0.099 [0.049, 0.153] | 0.842 [0.841, 0.843] | 0.364 [0.188, 0.556] |
| OmniMatch CG | same_origin | 1356 | 0.846 | 0.750 [0.713, 0.783] | 0.030 [0.021, 0.049] | 0.075 [0.061, 0.097] |
| OmniMatch CG | different_origin | 144 | 0.000 | 0.060 [0.032, 0.103] | 0.842 [0.842, 0.842] | 0.428 [0.199, 0.636] |
| TUS Small | same_origin | 6000 | 0.891 | 0.624 [0.592, 0.654] | 0.094 [0.080, 0.126] | 0.065 [0.042, 0.081] |
| TUS Small | different_origin | 0 | – | no rows | no rows | no rows |
| TUS Big | same_origin | 5648 | 0.938 | 0.468 [0.419, 0.516] | 0.042 [0.037, 0.082] | 0.053 [0.038, 0.086] |
| TUS Big | different_origin | 352 | 0.219 | 0.147 [0.057, 0.281] | 0.560 [0.378, 0.734] | 0.161 [0.097, 0.251] |

### Benchmarks

| benchmark | tables | profiled columns | profiling (s) | queries | k | top-k rows | positive rate top-k | positive rate all | same-origin share of positives | GT pairs naming a missing column | P@k ours | P@k models.ipynb | P@k scores.txt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FREYJA_BM | 160 | 680 | 2.4 | 50 | 10 | 500 | 0.918 | 0.0435 | 0.000 | 0 of 1478 | 0.926 | 0.924 | 0.924 |
| SANTOS Small | 550 | 4301 | 9.7 | 50 | 10 | 500 | 0.868 | 0.0027 | 0.827 | 57 of 645 | 0.892 | 0.928 | 0.916 |
| OmniMatch CR | 480 | 1970 | 3.2 | 50 | 30 | 1500 | 0.771 | 0.0177 | 1.000 | 0 of 1742 | 0.748 | 0.609 | 0.547 |
| OmniMatch CG | 440 | 1938 | 3.5 | 50 | 30 | 1500 | 0.765 | 0.0165 | 1.000 | 0 of 1597 | 0.743 | 0.613 | 0.530 |
| TUS Small | 1526 | 12625 | 27.9 | 100 | 60 | 6000 | 0.891 | 0.0063 | 1.000 | 1665 of 9651 | 0.893 | 0.890 | 0.884 |
| TUS Big | 5045 | 49702 | 80.9 | 100 | 60 | 6000 | 0.896 | 0.0159 | 0.961 | 25064 of 103954 | 0.899 | 0.893 | 0.951 |
