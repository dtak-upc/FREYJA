
### Leave-one-out ECE [95% CI], PRIMARY, pool `all`; within-lake reference last

| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |
|---|---|---|---|---|---|
| FREYJA_BM | 0.664 [0.568, 0.753] | 0.123 [0.095, 0.151] | 0.395 [0.303, 0.504] | 0.034 [0.022, 0.068] | 0.028 [0.009, 0.068] |
| FREYJA_BM (held-out rows) | 0.541 [0.435, 0.671] | 0.134 [0.090, 0.205] | 0.349 [0.241, 0.500] | 0.100 [0.056, 0.185] | 0.043 [0.016, 0.098] |
| SANTOS Small | 0.573 [0.498, 0.646] | 0.117 [0.084, 0.150] | 0.067 [0.047, 0.144] | 0.060 [0.040, 0.113] | 0.015 [0.005, 0.032] |
| OmniMatch CR | 0.680 [0.617, 0.743] | 0.168 [0.125, 0.212] | 0.162 [0.123, 0.207] | 0.096 [0.075, 0.147] | 0.031 [0.020, 0.059] |

### Leave-one-out ECE [95% CI], SECONDARY, pool `all`; within-lake reference last

| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |
|---|---|---|---|---|---|
| FREYJA_BM | 0.113 [0.107, 0.118] | 0.029 [0.027, 0.031] | 0.032 [0.030, 0.034] | 0.003 [0.003, 0.007] | 0.002 [0.001, 0.007] |
| FREYJA_BM (held-out rows) | 0.100 [0.098, 0.104] | 0.010 [0.007, 0.013] | 0.011 [0.008, 0.015] | 0.009 [0.007, 0.011] | 0.005 [0.002, 0.009] |
| SANTOS Small | 0.126 [0.126, 0.126] | 0.003 [0.002, 0.004] | 0.001 [0.001, 0.002] | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| OmniMatch CR | 0.118 [0.116, 0.119] | 0.018 [0.005, 0.033] | 0.002 [0.000, 0.006] | 0.001 [0.000, 0.011] | 0.000 [0.000, 0.001] |

### Leave-one-out ECE, PRIMARY, other pools

| held-out benchmark | pool | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|
| FREYJA_BM | no_freyja_bm | 0.664 [0.568, 0.753] | 0.123 [0.095, 0.151] | 0.395 [0.303, 0.504] |
| FREYJA_BM (held-out rows) | no_freyja_bm | 0.541 [0.435, 0.671] | 0.134 [0.090, 0.205] | 0.349 [0.241, 0.500] |
| FREYJA_BM | no_shared_origin | n/a | n/a | n/a |
| FREYJA_BM (held-out rows) | no_shared_origin | n/a | n/a | n/a |
| SANTOS Small | no_freyja_bm | 0.556 [0.482, 0.632] | 0.175 [0.123, 0.226] | 0.117 [0.087, 0.161] |
| SANTOS Small | no_shared_origin | 0.573 [0.498, 0.646] | 0.051 [0.031, 0.115] | 0.092 [0.050, 0.165] |
| OmniMatch CR | no_freyja_bm | 0.672 [0.606, 0.737] | 0.152 [0.109, 0.195] | 0.128 [0.093, 0.164] |
| OmniMatch CR | no_shared_origin | 0.680 [0.617, 0.743] | 0.187 [0.146, 0.233] | 0.188 [0.141, 0.228] |

### Paired difference ECE(c) − ECE(b), leave-one-out pool `all` [95% CI]

| held-out benchmark | PRIMARY | SECONDARY |
|---|---|---|
| FREYJA_BM | +0.272 [+0.163, +0.394] | +0.003 [+0.000, +0.006] |
| FREYJA_BM (held-out rows) | +0.216 [+0.072, +0.378] | +0.002 [+0.000, +0.003] |
| SANTOS Small | -0.050 [-0.079, +0.039] | -0.002 [-0.003, -0.001] |
| OmniMatch CR | -0.006 [-0.037, +0.028] | -0.016 [-0.028, -0.005] |

### Summaries (median [min, max] of ECE)

| design | shared-origin variant | FREYJA_BM rows | set | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|---|---|
| leave_one_out | all | all | PRIMARY | 0.664 [0.573, 0.680] (n=3) | 0.123 [0.117, 0.168] (n=3) | 0.162 [0.067, 0.395] (n=3) |
| leave_one_out | excluded_as_fitting | all | PRIMARY | 0.626 [0.573, 0.680] (n=2) | 0.119 [0.051, 0.187] (n=2) | 0.140 [0.092, 0.188] (n=2) |
| leave_one_out | excluded_as_evaluation | all | PRIMARY | 0.664 [0.664, 0.664] (n=1) | 0.123 [0.123, 0.123] (n=1) | 0.395 [0.395, 0.395] (n=1) |
| leave_one_out | excluded_as_both | all | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | all | PRIMARY | 0.664 [0.556, 0.672] (n=3) | 0.152 [0.123, 0.175] (n=3) | 0.128 [0.117, 0.395] (n=3) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | all | PRIMARY | 0.664 [0.664, 0.664] (n=1) | 0.123 [0.123, 0.123] (n=1) | 0.395 [0.395, 0.395] (n=1) |
| pairwise | all | all | PRIMARY | 0.667 [0.556, 0.680] (n=6) | 0.156 [0.051, 0.187] (n=6) | 0.158 [0.092, 0.443] (n=6) |
| pairwise | excluded_as_fitting | all | PRIMARY | 0.626 [0.573, 0.680] (n=2) | 0.119 [0.051, 0.187] (n=2) | 0.140 [0.092, 0.188] (n=2) |
| pairwise | excluded_as_evaluation | all | PRIMARY | 0.667 [0.663, 0.671] (n=2) | 0.123 [0.085, 0.160] (n=2) | 0.414 [0.384, 0.443] (n=2) |
| pairwise | excluded_as_both | all | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | all | PRIMARY | – | 0.060 [0.034, 0.096] (n=3) | 0.028 [0.015, 0.031] (n=3) |
| within_lake | excluded_as_evaluation | all | PRIMARY | – | 0.034 [0.034, 0.034] (n=1) | 0.028 [0.028, 0.028] (n=1) |
| leave_one_out | all | all | SECONDARY | 0.118 [0.113, 0.126] (n=3) | 0.018 [0.003, 0.029] (n=3) | 0.002 [0.001, 0.032] (n=3) |
| leave_one_out | excluded_as_fitting | all | SECONDARY | 0.122 [0.118, 0.126] (n=2) | 0.026 [0.012, 0.040] (n=2) | 0.006 [0.004, 0.008] (n=2) |
| leave_one_out | excluded_as_evaluation | all | SECONDARY | 0.113 [0.113, 0.113] (n=1) | 0.029 [0.029, 0.029] (n=1) | 0.032 [0.032, 0.032] (n=1) |
| leave_one_out | excluded_as_both | all | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | all | SECONDARY | 0.107 [0.002, 0.113] (n=3) | 0.002 [0.000, 0.029] (n=3) | 0.005 [0.000, 0.032] (n=3) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | all | SECONDARY | 0.113 [0.113, 0.113] (n=1) | 0.029 [0.029, 0.029] (n=1) | 0.032 [0.032, 0.032] (n=1) |
| pairwise | all | all | SECONDARY | 0.110 [0.002, 0.126] (n=6) | 0.020 [0.000, 0.040] (n=6) | 0.007 [0.000, 0.031] (n=6) |
| pairwise | excluded_as_fitting | all | SECONDARY | 0.122 [0.118, 0.126] (n=2) | 0.026 [0.012, 0.040] (n=2) | 0.006 [0.004, 0.008] (n=2) |
| pairwise | excluded_as_evaluation | all | SECONDARY | 0.076 [0.038, 0.113] (n=2) | 0.029 [0.029, 0.029] (n=2) | 0.029 [0.027, 0.031] (n=2) |
| pairwise | excluded_as_both | all | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | all | SECONDARY | – | 0.001 [0.000, 0.003] (n=3) | 0.000 [0.000, 0.002] (n=3) |
| within_lake | excluded_as_evaluation | all | SECONDARY | – | 0.003 [0.003, 0.003] (n=1) | 0.002 [0.002, 0.002] (n=1) |
| leave_one_out | all | heldout_rows | PRIMARY | 0.573 [0.541, 0.680] (n=3) | 0.134 [0.117, 0.168] (n=3) | 0.162 [0.067, 0.349] (n=3) |
| leave_one_out | excluded_as_fitting | heldout_rows | PRIMARY | 0.626 [0.573, 0.680] (n=2) | 0.119 [0.051, 0.187] (n=2) | 0.140 [0.092, 0.188] (n=2) |
| leave_one_out | excluded_as_evaluation | heldout_rows | PRIMARY | 0.541 [0.541, 0.541] (n=1) | 0.134 [0.134, 0.134] (n=1) | 0.349 [0.349, 0.349] (n=1) |
| leave_one_out | excluded_as_both | heldout_rows | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | heldout_rows | PRIMARY | 0.556 [0.541, 0.672] (n=3) | 0.152 [0.134, 0.175] (n=3) | 0.128 [0.117, 0.349] (n=3) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | heldout_rows | PRIMARY | 0.541 [0.541, 0.541] (n=1) | 0.134 [0.134, 0.134] (n=1) | 0.349 [0.349, 0.349] (n=1) |
| pairwise | all | heldout_rows | PRIMARY | 0.565 [0.541, 0.680] (n=6) | 0.155 [0.051, 0.187] (n=6) | 0.158 [0.092, 0.425] (n=6) |
| pairwise | excluded_as_fitting | heldout_rows | PRIMARY | 0.626 [0.573, 0.680] (n=2) | 0.119 [0.051, 0.187] (n=2) | 0.140 [0.092, 0.188] (n=2) |
| pairwise | excluded_as_evaluation | heldout_rows | PRIMARY | 0.544 [0.541, 0.546] (n=2) | 0.134 [0.109, 0.158] (n=2) | 0.416 [0.408, 0.425] (n=2) |
| pairwise | excluded_as_both | heldout_rows | PRIMARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | heldout_rows | PRIMARY | – | 0.096 [0.060, 0.100] (n=3) | 0.031 [0.015, 0.043] (n=3) |
| within_lake | excluded_as_evaluation | heldout_rows | PRIMARY | – | 0.100 [0.100, 0.100] (n=1) | 0.043 [0.043, 0.043] (n=1) |
| leave_one_out | all | heldout_rows | SECONDARY | 0.118 [0.100, 0.126] (n=3) | 0.010 [0.003, 0.018] (n=3) | 0.002 [0.001, 0.011] (n=3) |
| leave_one_out | excluded_as_fitting | heldout_rows | SECONDARY | 0.122 [0.118, 0.126] (n=2) | 0.026 [0.012, 0.040] (n=2) | 0.006 [0.004, 0.008] (n=2) |
| leave_one_out | excluded_as_evaluation | heldout_rows | SECONDARY | 0.100 [0.100, 0.100] (n=1) | 0.010 [0.010, 0.010] (n=1) | 0.011 [0.011, 0.011] (n=1) |
| leave_one_out | excluded_as_both | heldout_rows | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| leave_one_out | all [pool without FREYJA_BM] | heldout_rows | SECONDARY | 0.100 [0.002, 0.107] (n=3) | 0.002 [0.000, 0.010] (n=3) | 0.005 [0.000, 0.011] (n=3) |
| leave_one_out | excluded_as_evaluation [pool without FREYJA_BM] | heldout_rows | SECONDARY | 0.100 [0.100, 0.100] (n=1) | 0.010 [0.010, 0.010] (n=1) | 0.011 [0.011, 0.011] (n=1) |
| pairwise | all | heldout_rows | SECONDARY | 0.104 [0.002, 0.126] (n=6) | 0.010 [0.000, 0.040] (n=6) | 0.007 [0.000, 0.011] (n=6) |
| pairwise | excluded_as_fitting | heldout_rows | SECONDARY | 0.122 [0.118, 0.126] (n=2) | 0.026 [0.012, 0.040] (n=2) | 0.006 [0.004, 0.008] (n=2) |
| pairwise | excluded_as_evaluation | heldout_rows | SECONDARY | 0.057 [0.013, 0.101] (n=2) | 0.010 [0.010, 0.010] (n=2) | 0.010 [0.009, 0.011] (n=2) |
| pairwise | excluded_as_both | heldout_rows | SECONDARY | no unseen benchmark remains | no unseen benchmark remains | no unseen benchmark remains |
| within_lake | all | heldout_rows | SECONDARY | – | 0.001 [0.000, 0.009] (n=3) | 0.000 [0.000, 0.005] (n=3) |
| within_lake | excluded_as_evaluation | heldout_rows | SECONDARY | – | 0.009 [0.009, 0.009] (n=1) | 0.005 [0.005, 0.005] (n=1) |

### Stratified reading: leave-one-out pool `all`, PRIMARY

| held-out benchmark | stratum | rows | positive rate | (a) raw | (b) isotonic | (c) features |
|---|---|---|---|---|---|---|
| FREYJA_BM | same_origin | 9 | 0.000 | 0.619 [0.323, 0.838] | 0.910 [0.841, 0.957] | 0.028 [0.028, 0.028] |
| FREYJA_BM | different_origin | 491 | 0.935 | 0.688 [0.600, 0.767] | 0.130 [0.105, 0.157] | 0.403 [0.305, 0.518] |
| FREYJA_BM (held-out rows) | same_origin | 9 | 0.000 | 0.619 [0.323, 0.838] | 0.910 [0.841, 0.957] | 0.028 [0.028, 0.028] |
| FREYJA_BM (held-out rows) | different_origin | 171 | 0.819 | 0.591 [0.469, 0.702] | 0.123 [0.087, 0.181] | 0.372 [0.255, 0.524] |
| SANTOS Small | same_origin | 393 | 0.939 | 0.610 [0.528, 0.690] | 0.134 [0.106, 0.172] | 0.039 [0.035, 0.099] |
| SANTOS Small | different_origin | 107 | 0.607 | 0.438 [0.319, 0.575] | 0.158 [0.096, 0.216] | 0.318 [0.176, 0.479] |
| OmniMatch CR | same_origin | 1313 | 0.881 | 0.791 [0.753, 0.827] | 0.084 [0.064, 0.108] | 0.119 [0.090, 0.141] |
| OmniMatch CR | different_origin | 187 | 0.000 | 0.099 [0.049, 0.152] | 0.919 [0.895, 0.939] | 0.732 [0.653, 0.797] |

### Benchmarks

| benchmark | tables | profiled columns | profiling (s) | queries | k | top-k rows | positive rate top-k | positive rate all | same-origin share of positives | GT pairs naming a missing column | P@k ours | P@k models.ipynb | P@k scores.txt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FREYJA_BM | 160 | 680 | 2.4 | 50 | 10 | 500 | 0.918 | 0.0435 | 0.000 | 0 of 1478 | 0.926 | 0.924 | 0.924 |
| SANTOS Small | 550 | 4301 | 9.7 | 50 | 10 | 500 | 0.868 | 0.0027 | 0.827 | 57 of 645 | 0.892 | 0.928 | 0.916 |
| OmniMatch CR | 480 | 1970 | 3.2 | 50 | 30 | 1500 | 0.771 | 0.0177 | 1.000 | 0 of 1742 | 0.748 | 0.609 | 0.547 |
