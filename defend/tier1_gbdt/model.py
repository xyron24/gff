"""Tier-1 Fast Tabular GBDT Classifier (Histogram-based GBDT / ONNX Compatible).

Provides sub-millisecond inference for high-frequency payment switch authorization.
"""

from __future__ import annotations

import pickle
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

from defend.features.tabular_features import TabularFeatureExtractor


class Tier1GBDTClassifier:
    """Fast tabular GBDT classifier for sub-millisecond Tier-1 transaction screening."""

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        feature_extractor: Optional[TabularFeatureExtractor] = None,
    ) -> None:
        self.feature_extractor = feature_extractor or TabularFeatureExtractor()
        self.model: Optional[HistGradientBoostingClassifier] = None
        self.is_trained: bool = False

        if model_path and Path(model_path).exists():
            self.load(model_path)

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        num_trees: int = 120,
        learning_rate: float = 0.05,
        max_depth: int = 7,
    ) -> Dict[str, float]:
        """Train Histogram Gradient Boosted Classifier on feature matrix."""
        n_pos = int(np.sum(y_train == 1))
        n_neg = int(np.sum(y_train == 0))
        scale_pos_weight = float(n_neg / max(1, n_pos))

        # Sample weights for class imbalance
        sample_weights = np.ones(len(y_train), dtype=np.float32)
        sample_weights[y_train == 1] = min(scale_pos_weight, 15.0)

        self.model = HistGradientBoostingClassifier(
            max_iter=num_trees,
            learning_rate=learning_rate,
            max_depth=max_depth,
            class_weight="balanced",
            random_state=42,
        )

        self.model.fit(X_train, y_train, sample_weight=sample_weights)
        self.is_trained = True

        train_preds = self.model.predict_proba(X_train)[:, 1]
        return {
            "train_samples": len(y_train),
            "scale_pos_weight": scale_pos_weight,
            "train_mean_pred": float(np.mean(train_preds)),
        }

    def predict_proba_single(self, txn: Dict[str, Any]) -> Tuple[float, float]:
        """Score a single raw transaction record with microsecond latency measurement.

        Returns:
            Tuple of (fraud_probability [0.0 to 1.0], latency_ms)
        """
        t0 = time.perf_counter()
        vec = self.feature_extractor.extract_single(txn).reshape(1, -1)

        if self.model is None or not self.is_trained:
            # Untrained fallback heuristic
            amt = float(txn.get("amount", 0.0))
            friction = float(txn.get("biometric_friction_score", 0.05))
            score = 0.5 if (amt > 20000 or friction > 0.8) else 0.05
        else:
            probs = self.model.predict_proba(vec)
            score = float(probs[0, 1])

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return score, latency_ms

    def predict_proba_batch(self, X: np.ndarray) -> np.ndarray:
        """Batch scoring on feature matrix."""
        if self.model is None or not self.is_trained:
            return np.zeros(len(X), dtype=np.float32)
        return np.array(self.model.predict_proba(X)[:, 1], dtype=np.float32)

    def save(self, model_path: Union[str, Path]) -> None:
        """Save model artifact to disk."""
        if self.model:
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            with open(model_path, "wb") as f:
                pickle.dump(self.model, f)

    def load(self, model_path: Union[str, Path]) -> None:
        """Load model artifact from disk."""
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
        self.is_trained = True
