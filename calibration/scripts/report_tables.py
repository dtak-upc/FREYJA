"""Markdown tables for README.md and NUMBERS_FOR_B2.md, generated from
calibration/results/ (no number is typed by hand).

Writes calibration/results/tables.md. Usage: python -I report_tables.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from benchmarks import BENCHMARKS, CAL, ORDER  # noqa: E402

R = CAL / "results"


def ci(r):
    return f"{r.ece:.3f} [{r.ece_lo:.3f}, {r.ece_hi:.3f}]"


def cell(p, **kw):
    q = p
    for k, v in kw.items():
        q = q[q[k] == v]
    return ci(q.iloc[0]) if len(q) and pd.notna(q.iloc[0].ece) else "n/a"


def main():
    p = pd.read_csv(R / "pairs.csv")
    d = pd.read_csv(R / "descriptives.csv")
    prof = pd.read_csv(R / "profiling.csv").set_index("benchmark")
    pk = pd.read_csv(R / "precision_at_k.csv")
    gt = pd.read_csv(R / "gt_name_check.csv").set_index("benchmark")
    pd_ = pd.read_csv(R / "paired_differences.csv")
    st = pd.read_csv(R / "stratified.csv")
    s = pd.read_csv(R / "summary.csv")
    present = [b for b in ORDER if b in set(p["eval"])]
    out = []

    for sset in ["PRIMARY", "SECONDARY"]:
        out.append(f"\n### Leave-one-out ECE [95% CI], {sset}, pool `all`; within-lake reference last\n")
        out.append("| held-out benchmark | (a) raw | (b) isotonic | (c) features | within-lake (b) | within-lake (c) |")
        out.append("|---|---|---|---|---|---|")
        for b in present:
            for v in ["all", "heldout_rows"] if b == "freyja_bm" else ["all"]:
                x = p[(p["eval"] == b) & (p.set == sset) & (p.eval_rows == v)]
                lo = x[(x.design == "leave_one_out") & (x.fit == "all")]
                wl = x[x.design == "within_lake"]
                name = BENCHMARKS[b]["name"] + (" (held-out rows)" if v == "heldout_rows" else "")
                out.append(f"| {name} | " + " | ".join([cell(lo, estimator=e) for e in ["raw", "isotonic", "features"]]
                                                     + [cell(wl, estimator=e) for e in ["isotonic", "features"]]) + " |")

    out.append("\n### Leave-one-out ECE, PRIMARY, other pools\n")
    out.append("| held-out benchmark | pool | (a) raw | (b) isotonic | (c) features |")
    out.append("|---|---|---|---|---|")
    for b in present:
        for pool in ["no_freyja_bm", "no_shared_origin"]:
            for v in ["all", "heldout_rows"] if b == "freyja_bm" else ["all"]:
                x = p[(p["eval"] == b) & (p.set == "PRIMARY") & (p.eval_rows == v) & (p.design == "leave_one_out")
                      & (p.fit == pool)]
                name = BENCHMARKS[b]["name"] + (" (held-out rows)" if v == "heldout_rows" else "")
                out.append(f"| {name} | {pool} | " + " | ".join(cell(x, estimator=e) for e in ["raw", "isotonic", "features"]) + " |")

    out.append("\n### Paired difference ECE(c) − ECE(b), leave-one-out pool `all` [95% CI]\n")
    out.append("| held-out benchmark | PRIMARY | SECONDARY |")
    out.append("|---|---|---|")
    for b in present:
        for v in ["all", "heldout_rows"] if b == "freyja_bm" else ["all"]:
            cells = []
            for sset in ["PRIMARY", "SECONDARY"]:
                x = pd_[(pd_["eval"] == b) & (pd_.set == sset) & (pd_.eval_rows == v) & (pd_.design == "leave_one_out")
                        & (pd_.fit == "all") & (pd_.contrast == "ece_features_minus_isotonic")]
                cells.append(f"{x.iloc[0]['diff']:+.3f} [{x.iloc[0].lo:+.3f}, {x.iloc[0].hi:+.3f}]" if len(x) else "n/a")
            name = BENCHMARKS[b]["name"] + (" (held-out rows)" if v == "heldout_rows" else "")
            out.append(f"| {name} | " + " | ".join(cells) + " |")

    out.append("\nReading (c) of PREREGISTRATION.md §8 — benchmarks (FREYJA_BM on all rows) whose 95% interval of "
               "ECE(c) − ECE(b), leave-one-out pool `all`, lies below 0 / contains 0 / lies above 0:\n")
    for sset in ["PRIMARY", "SECONDARY"]:
        x = pd_[(pd_.design == "leave_one_out") & (pd_.fit == "all") & (pd_.set == sset) & (pd_.eval_rows == "all")
                & (pd_.contrast == "ece_features_minus_isotonic")]
        below, above = x[x.hi < 0]["eval"].tolist(), x[x.lo > 0]["eval"].tolist()
        contains = x[(x.lo <= 0) & (x.hi >= 0)]["eval"].tolist()
        nm = lambda bs: ", ".join(BENCHMARKS[b]["name"] for b in bs) or "none"  # noqa: E731
        out.append(f"- {sset}: below 0 ((c) better): {len(below)} ({nm(below)}); contains 0: {len(contains)} "
                   f"({nm(contains)}); above 0 ((b) better): {len(above)} ({nm(above)})")

    out.append("\n### Summaries (median [min, max] of ECE)\n")
    out.append("| design | shared-origin variant | FREYJA_BM rows | set | (a) raw | (b) isotonic | (c) features |")
    out.append("|---|---|---|---|---|---|---|")
    for (design, var, fb, sset), g in s.groupby(["design", "shared_origin_variant", "fbm_rows", "set"], sort=False):
        cells = []
        for e in ["raw", "isotonic", "features"]:
            r = g[g.estimator == e]
            if len(r) == 0:
                cells.append("–")
            elif r.iloc[0].n == 0:
                cells.append("no unseen benchmark remains")
            else:
                r = r.iloc[0]
                cells.append(f"{r.ece_median:.3f} [{r.ece_min:.3f}, {r.ece_max:.3f}] (n={int(r.n)})")
        out.append(f"| {design} | {var} | {fb} | {sset} | " + " | ".join(cells) + " |")

    out.append("\n### Stratified reading: leave-one-out pool `all`, PRIMARY\n")
    out.append("| held-out benchmark | stratum | rows | positive rate | (a) raw | (b) isotonic | (c) features |")
    out.append("|---|---|---|---|---|---|---|")
    for b in present:
        for v in ["all", "heldout_rows"] if b == "freyja_bm" else ["all"]:
            for stratum in ["same_origin", "different_origin"]:
                x = st[(st["eval"] == b) & (st.eval_rows == v) & (st.stratum == stratum)]
                if len(x) == 0:
                    continue
                n = int(x.iloc[0].n_rows)
                pr = f"{x.iloc[0].pos_rate:.3f}" if n else "–"
                cells = [cell(x, estimator=e) if n else "no rows" for e in ["raw", "isotonic", "features"]]
                name = BENCHMARKS[b]["name"] + (" (held-out rows)" if v == "heldout_rows" else "")
                out.append(f"| {name} | {stratum} | {n} | {pr} | " + " | ".join(cells) + " |")

    out.append("\n### Benchmarks\n")
    out.append("| benchmark | tables | profiled columns | profiling (s) | queries | k | top-k rows | positive rate top-k | positive rate all | same-origin share of positives | GT pairs naming a missing column | P@k ours | P@k models.ipynb | P@k scores.txt |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for b in present:
        dp = d[(d.benchmark == b) & (d.set == "PRIMARY") & (d.eval_rows == "all")].iloc[0]
        ds = d[(d.benchmark == b) & (d.set == "SECONDARY") & (d.eval_rows == "all")].iloc[0]
        last = pk[pk.benchmark == b].iloc[-1]
        out.append(f"| {BENCHMARKS[b]['name']} | {prof.loc[b, 'tables_profiled']} | {prof.loc[b, 'columns']} | "
                   f"{prof.loc[b, 'wall_time_s']:.1f} | {dp.queries} | {BENCHMARKS[b]['k']} | {dp.rows} | "
                   f"{dp.pos_rate:.3f} | {ds.pos_rate:.4f} | {ds.same_origin_share_of_positives:.3f} | "
                   f"{gt.loc[b, 'gt_pairs_naming_a_column_not_in_lake']} of {gt.loc[b, 'gt_pairs']} | {last.ours:.3f} | "
                   f"{last.published_models_ipynb:.3f} | {last.published_scores_txt:.3f} |")
    txt = "\n".join(out) + "\n"
    (R / "tables.md").write_text(txt)
    print(txt)

    # Table for NUMBERS_FOR_B2.md
    b2 = ["| benchmark | tables | columns | profiling (s) | positive rate in top-k | within-lake ECE (b) | "
          "within-lake ECE (c) | leave-one-out ECE (a) | leave-one-out ECE (b) | leave-one-out ECE (c) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for b in present:
        for v in ["all", "heldout_rows"] if b == "freyja_bm" else ["all"]:
            x = p[(p["eval"] == b) & (p.set == "PRIMARY") & (p.eval_rows == v)]
            lo = x[(x.design == "leave_one_out") & (x.fit == "all")]
            wl = x[x.design == "within_lake"]
            dp = d[(d.benchmark == b) & (d.set == "PRIMARY") & (d.eval_rows == v)].iloc[0]
            name = BENCHMARKS[b]["name"] + (" (held-out rows)" if v == "heldout_rows" else "")
            pre = (f"{prof.loc[b, 'tables_profiled']} | {prof.loc[b, 'columns']} | {prof.loc[b, 'wall_time_s']:.1f}"
                   if v == "all" else "″ | ″ | ″")
            b2.append(f"| {name} | {pre} | {dp.pos_rate:.3f} | {cell(wl, estimator='isotonic')} | "
                      f"{cell(wl, estimator='features')} | " + " | ".join(cell(lo, estimator=e) for e in
                                                                           ["raw", "isotonic", "features"]) + " |")
    if "santos_big" in prof.index:
        b2.append(f"| SANTOS Big (profiling only, no labels) | {prof.loc['santos_big', 'tables_profiled']} | "
                  f"{prof.loc['santos_big', 'columns']} | {prof.loc['santos_big', 'wall_time_s']:.1f} | – | – | – | – | – | – |")
    (R / "b2_table.md").write_text("\n".join(b2) + "\n")


if __name__ == "__main__":
    main()
