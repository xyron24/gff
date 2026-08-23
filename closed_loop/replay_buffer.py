"""Experience Replay Buffer for Adversarial Co-Evolution.

Maintains historical memory of transaction events with prioritized oversampling
of adversarial false negatives to harden the Blue Team classifier against catastrophic forgetting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


class ExperienceReplayBuffer:
    """Prioritized experience replay buffer storing past payment traffic and evasion cases."""

    def __init__(self, max_capacity: int = 20000) -> None:
        self.max_capacity = max_capacity
        self._buffer: Optional[pd.DataFrame] = None

    def add_transactions(self, df_new: pd.DataFrame) -> int:
        """Append new transactions to replay memory with FIFO eviction on capacity overflow."""
        if df_new.empty:
            return self.size()

        if self._buffer is None or self._buffer.empty:
            self._buffer = df_new.copy()
        else:
            self._buffer = pd.concat([self._buffer, df_new], ignore_index=True)

        # Evict oldest if exceeding capacity
        if len(self._buffer) > self.max_capacity:
            self._buffer = self._buffer.iloc[-self.max_capacity:].reset_index(drop=True)

        return len(self._buffer)

    def sample_hardened_dataset(
        self,
        n_samples: int = 1500,
        target_fraud_ratio: float = 0.20,
    ) -> pd.DataFrame:
        """Sample a training batch with controlled ratio of legitimate vs mined fraud cases."""
        if self._buffer is None or self._buffer.empty:
            return pd.DataFrame()

        legit_pool = self._buffer[self._buffer["is_fraud"] == 0]
        fraud_pool = self._buffer[self._buffer["is_fraud"] == 1]

        n_fraud = int(n_samples * target_fraud_ratio)
        n_legit = n_samples - n_fraud

        # Sample with replacement if pool size is smaller than requested
        sampled_legit = (
            legit_pool.sample(n=min(len(legit_pool), n_legit), replace=len(legit_pool) < n_legit, random_state=42)
            if not legit_pool.empty
            else pd.DataFrame()
        )
        sampled_fraud = (
            fraud_pool.sample(n=min(len(fraud_pool), n_fraud), replace=len(fraud_pool) < n_fraud, random_state=42)
            if not fraud_pool.empty
            else pd.DataFrame()
        )

        combined = pd.concat([sampled_legit, sampled_fraud], ignore_index=True)
        if "timestamp" in combined.columns:
            combined["timestamp"] = pd.to_datetime(combined["timestamp"])
            combined = combined.sort_values("timestamp").reset_index(drop=True)
        return combined

    def size(self) -> int:
        """Total records in buffer."""
        return len(self._buffer) if self._buffer is not None else 0

    def get_statistics(self) -> Dict[str, Any]:
        """Summary diagnostics of current buffer contents."""
        if self._buffer is None or self._buffer.empty:
            return {
                "total_records": 0,
                "legitimate_count": 0,
                "fraud_count": 0,
                "attack_types_present": [],
            }

        fraud_df = self._buffer[self._buffer["is_fraud"] == 1]
        return {
            "total_records": len(self._buffer),
            "legitimate_count": int((self._buffer["is_fraud"] == 0).sum()),
            "fraud_count": len(fraud_df),
            "attack_types_present": list(fraud_df["attack_type"].unique()),
            "attack_type_counts": fraud_df["attack_type"].value_counts().to_dict(),
        }
