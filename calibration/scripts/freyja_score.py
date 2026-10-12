"""FREYJA features and score for (query column, candidate column) pairs.

Features come from FREYJA's own ComputeDistances._compute_distances_vectorized
(app/core/distances) on the preprocessed normalized profiles; the score is the
unmodified FREYJA model's predict() on the 22 features it was trained on.
Nothing is written to CSV in between (FREYJA's API round-trips the distances
through a CSV file; we keep them in memory).
"""
import sys
from pathlib import Path

FREYJA = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FREYJA))

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from app.core.distances.compute_distances import ComputeDistances  # noqa: E402
from app.core.profiling.metrics import MetricProperties  # noqa: E402

MODEL_PATH = FREYJA / "app/core/model/gradient_boosting_ne100_lr0.05_md3_ss0.8_msl10.pkl"


def load_model():
    return joblib.load(MODEL_PATH)


class _Distances(ComputeDistances):
    """ComputeDistances without the file-reading constructor."""

    def __init__(self):
        self.distance_patterns = MetricProperties().distance_patterns


_DIST = _Distances()


def features_for_query(profiles: pd.DataFrame, q: int, feature_names) -> pd.DataFrame:
    """Features of query row q against every row of `profiles` (query row included).

    `profiles` is the preprocessed normalized profile table (as in FREYJA's .pkl),
    with a default RangeIndex. Returns one row per profile row, in profile order.
    """
    query_row = profiles.iloc[q]
    d = _DIST._compute_distances_vectorized(query_row, profiles)
    return d[list(feature_names)]


def score(model, features: pd.DataFrame) -> np.ndarray:
    return model.predict(features[list(model.feature_names_in_)])
