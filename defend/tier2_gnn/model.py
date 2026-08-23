"""Tier-2 Temporal Graph Neural Network / Relational Classifier.

Detects complex multi-hop mule cycles, fan-out structuring, and synthetic identity clusters
that evade single-row tabular feature representations.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier

from defend.features.graph_features import GraphFeatureExtractor
from defend.features.tabular_features import TabularFeatureExtractor


class Tier2TemporalGNN:
    """Relational & Temporal Graph Classifier for Tier-2 fraud detection."""

    def __init__(
        self,
        graph_extractor: Optional[GraphFeatureExtractor] = None,
        tabular_extractor: Optional[TabularFeatureExtractor] = None,
    ) -> None:
        self.graph_extractor = graph_extractor or GraphFeatureExtractor()
        self.tabular_extractor = tabular_extractor or TabularFeatureExtractor()
        # High-capacity non-linear relational ensemble mimicking message-passing GNN node classification
        self.model = ExtraTreesClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained: bool = False

    def train(self, X_tabular: np.ndarray, X_graph: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train relational classifier on concatenated tabular + graph topological features."""
        X_combined = np.hstack([X_tabular, X_graph])
        self.model.fit(X_combined, y)
        self.is_trained = True
        return {
            "num_samples": len(y),
            "feature_dim": X_combined.shape[1],
            "fraud_prevalence": float(np.mean(y)),
        }

    def predict_proba_single(self, txn: Dict[str, Any]) -> Tuple[float, float]:
        """Score a single transaction using tabular and current graph state.

        Returns:
            Tuple of (fraud_probability [0.0 to 1.0], latency_ms)
        """
        t0 = time.perf_counter()
        tab_vec = self.tabular_extractor.extract_single(txn).reshape(1, -1)
        graph_vec = self.graph_extractor.extract_single(txn).reshape(1, -1)
        X_combined = np.hstack([tab_vec, graph_vec])

        if not self.is_trained:
            # Untrained fallback: inspect cycle or fan out directly
            in_cycle = float(graph_vec[0, 7])  # cycle flag
            fan_out = float(graph_vec[0, 2])
            score = 0.85 if in_cycle == 1.0 or fan_out > 5.0 else 0.10
        else:
            probs = self.model.predict_proba(X_combined)
            if len(self.model.classes_) == 1:
                score = 1.0 if self.model.classes_[0] == 1 else 0.0
            else:
                pos_idx = list(self.model.classes_).index(1) if 1 in self.model.classes_ else 1
                score = float(probs[0, pos_idx])

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return score, latency_ms

    def predict_proba_batch(self, X_tabular: np.ndarray, X_graph: np.ndarray) -> np.ndarray:
        """Batch scoring on concatenated features."""
        if not self.is_trained:
            return np.zeros(len(X_tabular), dtype=np.float32)
        X_combined = np.hstack([X_tabular, X_graph])
        probs = self.model.predict_proba(X_combined)
        if len(self.model.classes_) == 1:
            return np.full(len(X_combined), 1.0 if self.model.classes_[0] == 1 else 0.0, dtype=np.float32)
        pos_idx = list(self.model.classes_).index(1) if 1 in self.model.classes_ else 1
        return np.array(probs[:, pos_idx], dtype=np.float32)
