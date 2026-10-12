"""POST-HOC, not pre-registered. ECE rewards a constant prediction at the base rate.
This reading compares each Brier score with that of a constant equal to the
positive rate of the evaluated rows: skill = 1 - Brier / (r (1 - r)). Skill 0 =
no better than knowing the base rate; < 0 = worse. Leave-one-out (pool `all`)
and within-lake, PRIMARY; same predictions, same bootstrap draws (seed
20261012, queries resampled) as the pre-registered analysis.

Writes calibration/results/posthoc_brier_skill.csv. Usage: python -I posthoc_brier_skill.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import calib  # noqa: E402
from benchmarks import CAL, ORDER, SCRATCH, pairs_path  # noqa: E402


def skill_reps(p, y, qid):
    qi, nq = calib.query_index(qid)
    draws = np.random.default_rng(calib.SEED).integers(0, nq, size=(calib.N_BOOT, nq))
    sq = np.bincount(qi, weights=(p - y) ** 2, minlength=nq)
    pos = np.bincount(qi, weights=y, minlength=nq)
    n = np.bincount(qi, minlength=nq).astype(float)
    out = np.empty(calib.N_BOOT)
    for r in range(calib.N_BOOT):
        c = np.bincount(draws[r], minlength=nq)
        rate = c @ pos / (c @ n)
        out[r] = 1 - (c @ sq / (c @ n)) / (rate * (1 - rate))
    return out


def main():
    rows = []
    for b in ORDER:
        pr = pd.read_csv(pairs_path(b), usecols=lambda c: c in ("query_id", "rank", "primary", "in_training"))
        pr = pr[pr.primary == 1].reset_index(drop=True)
        for design, fit, ests in [("leave_one_out", "all", ["raw", "isotonic", "features"]),
                                  ("within_lake", "own_5fold", ["isotonic", "features"])]:
            d = pd.read_csv(SCRATCH / "eval/predictions" / f"{design}__{fit}__{b}__PRIMARY.csv.gz",
                            float_precision="round_trip")
            variants = [("all", np.ones(len(d), bool))]
            if "in_training" in pr:
                variants.append(("heldout_rows", pr.in_training.to_numpy() == 0))
            for v, m in variants:
                y, q = d.label.to_numpy()[m].astype(float), d.query_id.to_numpy()[m]
                rate = y.mean()
                for est in ests:
                    p = d[f"p_{est}"].to_numpy()[m]
                    sk = 1 - calib.brier(p, y) / (rate * (1 - rate))
                    lo, hi = calib.interval(skill_reps(p, y, q))
                    rows.append(dict(analysis="POST-HOC Brier skill vs constant at the evaluated positive rate",
                                     design=design, fit=fit, eval=b, set="PRIMARY", eval_rows=v, estimator=est,
                                     pos_rate=rate, brier_constant=rate * (1 - rate), brier=calib.brier(p, y),
                                     skill=sk, skill_lo=lo, skill_hi=hi))
    df = pd.DataFrame(rows)
    df.to_csv(CAL / "results/posthoc_brier_skill.csv", index=False)
    print(df[["design", "eval", "eval_rows", "estimator", "skill", "skill_lo", "skill_hi"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
