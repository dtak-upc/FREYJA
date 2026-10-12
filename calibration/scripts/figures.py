"""Figures (PDF and PNG), sized for an 8 cm column: reliability diagrams per
held-out benchmark (leave-one-out, PRIMARY, pool 'all'), leave-one-out ECE per
benchmark, profiling time against columns.

Usage: python -I figures.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from benchmarks import BENCHMARKS, CAL, ORDER, SCRATCH  # noqa: E402

FIG = CAL / "figures"
WIDTH = 8 / 2.54  # 8 cm in inches
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
STYLE = {  # validated reference palette, first three categorical slots + marker shape
    "raw": dict(color="#2a78d6", marker="o", label="(a) raw score"),
    "isotonic": dict(color="#eb6834", marker="s", label="(b) isotonic on score"),
    "features": dict(color="#1baf7a", marker="^", label="(c) features"),
}
plt.rcParams.update({"font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7, "xtick.labelsize": 6.5,
                     "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42,
                     "savefig.dpi": 300, "figure.facecolor": "white"})


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def bins(p, y, n_bins=10):
    """The ECE's equal-mass bins (canonical order, stable sort by p)."""
    order = np.argsort(p, kind="stable")
    out = []
    for b in np.array_split(order, n_bins):
        if len(b):
            out.append((p[b].mean(), y[b].mean(), len(b)))
    return np.array(out)


def reliability(pairs):
    for b in ORDER:
        f = SCRATCH / "eval/predictions" / f"leave_one_out__all__{b}__PRIMARY.csv.gz"
        if not f.exists():
            continue
        d = pd.read_csv(f, float_precision="round_trip")
        fig, ax = plt.subplots(figsize=(WIDTH * 0.62, WIDTH * 0.55))
        ax.plot([0, 1], [0, 1], ls=(0, (3, 2)), lw=0.8, color=MUTED, zorder=1)
        nmax = None
        for est, st in STYLE.items():
            r = bins(d[f"p_{est}"].to_numpy(), d["label"].to_numpy())
            nmax = r[:, 2].max() if nmax is None else max(nmax, r[:, 2].max())
            row = pairs[(pairs.design == "leave_one_out") & (pairs.fit == "all") & (pairs["eval"] == b)
                        & (pairs.set == "PRIMARY") & (pairs.eval_rows == "all") & (pairs.estimator == est)].iloc[0]
            ax.plot(r[:, 0], r[:, 1], color=st["color"], lw=1, zorder=2)
            ax.scatter(r[:, 0], r[:, 1], s=6 + 26 * r[:, 2] / r[:, 2].max(), color=st["color"], marker=st["marker"],
                       edgecolors="white", linewidths=0.5, zorder=3,
                       label=f"{st['label']}\nECE {row.ece:.3f} [{row.ece_lo:.3f}, {row.ece_hi:.3f}]")
        ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel("predicted probability (bin mean)"); ax.set_ylabel("observed join rate")
        ax.set_aspect("equal"); ax.grid(color=GRID, lw=0.4); ax.set_axisbelow(True)
        ax.set_title(f"{BENCHMARKS[b]['name']} held out (top-{BENCHMARKS[b]['k']}, {len(d)} pairs)", loc="left")
        ax.legend(loc="center left", bbox_to_anchor=(1.03, 0.5), frameon=False,
                  title="marker area ∝ pairs in bin", title_fontsize=6, alignment="left")
        save(fig, f"reliability_loo_primary_{b}")


def loo_ece(pairs):
    p = pairs[(pairs.design == "leave_one_out") & (pairs.fit == "all") & (pairs.set == "PRIMARY")
              & (pairs.eval_rows == "all")]
    w = pairs[(pairs.design == "within_lake") & (pairs.set == "PRIMARY") & (pairs.eval_rows == "all")
              & (pairs.estimator == "isotonic")]
    bs = [b for b in ORDER if b in set(p["eval"])]
    if not bs:
        return
    fig, ax = plt.subplots(figsize=(WIDTH, WIDTH * 0.42))
    x = np.arange(len(bs))
    for j, (est, st) in enumerate(STYLE.items()):
        r = p[p.estimator == est].set_index("eval").loc[bs]
        xs = x + (j - 1) * 0.22
        ax.errorbar(xs, r.ece, yerr=[r.ece - r.ece_lo, r.ece_hi - r.ece], fmt="none", ecolor=st["color"], lw=0.9,
                    capsize=0)
        ax.scatter(xs, r.ece, color=st["color"], marker=st["marker"], s=14, edgecolors="white", linewidths=0.5,
                   zorder=3, label=st["label"])
    wr = w.set_index("eval").reindex(bs)
    ax.scatter(x, wr.ece, marker="D", s=16, facecolors="none", edgecolors=INK, linewidths=0.8, zorder=4,
               label="within-lake reference for (b)")
    short = {"freyja_bm": "FREYJA\nBM", "santos_small": "SANTOS\nSmall", "om_cr": "OmniM.\nCR",
             "om_cg": "OmniM.\nCG", "tus_small": "TUS\nSmall", "tus_big": "TUS\nBig"}
    ax.set_xticks(x, [short[b] for b in bs])
    ax.set_ylabel("ECE, top-k (leave-one-out)")
    ax.set_ylim(bottom=0); ax.grid(axis="y", color=GRID, lw=0.4); ax.set_axisbelow(True)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2, frameon=False, columnspacing=1, handletextpad=0.3)
    save(fig, "loo_ece_primary")


def profiling_time():
    f = CAL / "results/profiling.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    names = {**{b: BENCHMARKS[b]["name"] for b in BENCHMARKS}, "santos_big": "SANTOS Big"}
    fig, ax = plt.subplots(figsize=(WIDTH, WIDTH * 0.42))
    ax.scatter(d["columns"], d.wall_time_s, color=STYLE["raw"]["color"], s=14, edgecolors="white", linewidths=0.5,
               zorder=3)
    offsets = {"om_cg": (5, 2), "om_cr": (5, -6), "freyja_bm": (4, -11)}  # avoid label collisions
    for _, r in d.iterrows():
        ax.annotate(f"{names[r.benchmark]} ({r.wall_time_s:.1f} s)", (r["columns"], r.wall_time_s),
                    xytext=offsets.get(r.benchmark, (4, -2)), textcoords="offset points", fontsize=6, color=INK)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("profiled columns"); ax.set_ylabel("profiling wall time (s)")
    ax.grid(color=GRID, lw=0.4, which="major"); ax.set_axisbelow(True)
    ax.set_xlim(d["columns"].min() / 2, d["columns"].max() * 6)
    ax.set_ylim(d.wall_time_s.min() / 3, d.wall_time_s.max() * 2)
    fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}" if v >= 1 else f"{v:g}")
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(fmt); axis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_title("FREYJA profiler, 8 workers, Apple M3 Pro", loc="left", color=MUTED)
    save(fig, "profiling_time")


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    pairs = pd.read_csv(CAL / "results/pairs.csv")
    reliability(pairs)
    loo_ece(pairs)
    profiling_time()
    print(sorted(p.name for p in FIG.glob("*.png")))
