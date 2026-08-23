"""False-Negative Mining Engine for Closed-Loop Co-Evolution.

Automatically extracts, tags, and profiles fraudulent transactions that successfully
evaded the detection grid (predicted score < threshold despite is_fraud == 1)
to feed the Experience Replay Buffer for active defense retraining.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class FalseNegativeMiner:
    """Mines and analyzes defense blind spots (false negatives)."""

    def __init__(self, block_threshold: float = 0.50) -> None:
        self.block_threshold = block_threshold

    def mine_false_negatives(
        self,
        df_transactions: pd.DataFrame,
        predicted_scores: np.ndarray,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Identify all transactions where is_fraud == 1 but predicted_score < threshold.

        Args:
            df_transactions: Labeled transaction DataFrame.
            predicted_scores: Model predicted fraud probability array.

        Returns:
            Tuple of (DataFrame of mined false negative transactions, diagnostic summary).
        """
        df = df_transactions.copy()
        df["predicted_score"] = predicted_scores
        df["evaded"] = (df["is_fraud"] == 1) & (df["predicted_score"] < self.block_threshold)

        fn_df = df[df["evaded"]].copy()

        # Calculate per-vector evasion rates
        fraud_df = df[df["is_fraud"] == 1]
        total_fraud = len(fraud_df)
        total_evaded = len(fn_df)

        overall_evasion_rate = float(total_evaded / max(1, total_fraud))

        per_vector_evasion = {}
        for atk, grp in fraud_df.groupby("attack_type"):
            evaded_in_grp = (grp["predicted_score"] < self.block_threshold).sum()
            per_vector_evasion[str(atk)] = {
                "total_attempts": len(grp),
                "successful_evasions": int(evaded_in_grp),
                "evasion_rate": round(float(evaded_in_grp / len(grp)), 4),
                "mean_evasion_score": round(float(grp["predicted_score"].mean()), 4),
            }

        # Identify most evasive attack vectors (highest evasion rate)
        sorted_evasive = sorted(
            per_vector_evasion.items(),
            key=lambda x: x[1]["evasion_rate"],
            reverse=True,
        )

        diagnostics = {
            "total_fraud_attempts": total_fraud,
            "total_false_negatives": total_evaded,
            "overall_evasion_rate": round(overall_evasion_rate, 4),
            "defense_catch_rate": round(1.0 - overall_evasion_rate, 4),
            "most_evasive_vectors": [k for k, _ in sorted_evasive[:3]],
            "per_vector_evasion": per_vector_evasion,
        }

        return fn_df.reset_index(drop=True), diagnostics
