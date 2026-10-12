"""Fixed per-benchmark parameters (PREREGISTRATION.md §1, §6)."""
import re
from pathlib import Path

FREYJA = Path(__file__).resolve().parents[2]
SCRATCH = Path("/Users/sergi.nadal/UPC/ERC/scratch")
GT_DIR = FREYJA / "ground_truths"
CAL = FREYJA / "calibration"
TRAINING_PAIRS = SCRATCH / "other_assets/extract/data/models/ground_truth_models.csv"

R_SANTOS = r"_[0-9a-z]\.csv$"
R_TUS = r"____c\d+_\d+____\d+\.csv$"
R_OM = r"_\d+_noisy_\d+\.csv$"

BENCHMARKS = {
    "freyja_bm": dict(name="FREYJA_BM", lake=SCRATCH / "freyja_bm/extract/datalake", varchar_only=True,
                      k=10, step=1, gt="freyja_ground_truth.csv", origin=None, shared_origin=False),
    "santos_small": dict(name="SANTOS Small", lake=SCRATCH / "santos_small/extract/santos_benchmark/datalake",
                         varchar_only=True, k=10, step=1, gt="santos_small_ground_truth.csv",
                         origin=R_SANTOS, shared_origin=True),
    "om_cr": dict(name="OmniMatch CR", lake=SCRATCH / "omnimatch/extract/datasets/culture_recreation/train_tables",
                  varchar_only=False, k=30, step=5, gt="omnimatch_culture_recreation_ground_truth.csv",
                  origin=R_OM, shared_origin=True),
    "om_cg": dict(name="OmniMatch CG", lake=SCRATCH / "omnimatch/extract/datasets/city_government/train_tables",
                  varchar_only=False, k=30, step=5, gt="omnimatch_city_government_ground_truth.csv",
                  origin=R_OM, shared_origin=True),
    "tus_small": dict(name="TUS Small", lake=SCRATCH / "tus_small/extract/tus/datalake", varchar_only=True,
                      k=60, step=10, gt="tus_small_ground_truth.csv", origin=R_TUS, shared_origin=True),
    "tus_big": dict(name="TUS Big", lake=SCRATCH / "tus_big/extract/tusLarge/datalake", varchar_only=True,
                    k=60, step=10, gt="tus_big_ground_truth_sample.csv", origin=R_TUS, shared_origin=True),
}
ORDER = ["freyja_bm", "santos_small", "om_cr", "om_cg", "tus_small", "tus_big"]


def profiles_dir(b):
    return SCRATCH / b / "profiles"


def pairs_path(b):
    return SCRATCH / b / "pairs.csv.gz"


def strip_csv(s):
    return s[:-4] if s.endswith(".csv") else s


def origin(b, table_stem):
    """Origin of a table (stem, no .csv) under the benchmark's name rule."""
    rule = BENCHMARKS[b]["origin"]
    name = table_stem + ".csv"
    return name if rule is None else re.sub(rule, "", name)
