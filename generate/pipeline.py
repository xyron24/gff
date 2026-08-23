"""End-to-End Adversarial Simulation Pipeline.

Coordinates baseline legitimate transaction generation and dispatches attack
injectors across the Threat Taxonomy to generate realistic labeled datasets.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

from generate.base_generator import BaseTransactionGenerator
from generate.attack_injectors import INJECTOR_REGISTRY, get_injector


class SimulationPipeline:
    """Orchestrates generation of mixed legitimate and adversarial fraud payment datasets."""

    def __init__(
        self,
        base_generator: Optional[BaseTransactionGenerator] = None,
        random_seed: int = 42,
    ) -> None:
        self.base_generator = base_generator or BaseTransactionGenerator(random_seed=random_seed)

    def generate_dataset(
        self,
        n_total: int = 2000,
        fraud_ratio: float = 0.08,
        selected_attacks: Optional[List[str]] = None,
        attack_weights: Optional[Dict[str, float]] = None,
        time_span_days: float = 7.0,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a complete labeled dataset combining baseline traffic with specified attacks.

        Args:
            n_total: Total number of transactions in the dataset.
            fraud_ratio: Fraction of fraudulent transactions (e.g. 0.08 = 8%).
            selected_attacks: List of attack IDs to include (defaults to all 12).
            attack_weights: Relative frequency weights for each attack vector.
            time_span_days: Temporal span of the generated transactions.

        Returns:
            Tuple of (DataFrame sorted by timestamp, metadata summary dictionary).
        """
        n_fraud = max(1, int(n_total * fraud_ratio))
        active_attacks = selected_attacks or list(INJECTOR_REGISTRY.keys())
        if not active_attacks:
            active_attacks = list(INJECTOR_REGISTRY.keys())

        # Distribute fraud count among active attacks
        if attack_weights:
            total_w = sum(attack_weights.get(atk, 1.0) for atk in active_attacks)
            counts = {
                atk: max(1, int(n_fraud * (attack_weights.get(atk, 1.0) / total_w)))
                for atk in active_attacks
            }
        else:
            base_count = max(1, n_fraud // len(active_attacks))
            counts = {atk: base_count for atk in active_attacks}

        actual_fraud_total = sum(counts.values())
        actual_n_legit = max(1, n_total - actual_fraud_total)

        # 1. Generate legitimate baseline to exact balance
        legit_df = self.base_generator.generate_batch(n=actual_n_legit, time_span_days=time_span_days)

        # 2. Run injectors
        fraud_dfs = []
        for atk_id in active_attacks:
            injector = get_injector(atk_id)
            count = counts.get(atk_id, 10)
            atk_df = injector.inject(baseline_df=legit_df, n_attacks=count)
            fraud_dfs.append(atk_df)

        # 3. Merge and sort
        all_dfs = [legit_df] + fraud_dfs
        full_df = pd.concat(all_dfs, ignore_index=True)
        full_df["timestamp"] = pd.to_datetime(full_df["timestamp"])
        full_df = full_df.sort_values("timestamp").reset_index(drop=True)

        # 4. Metadata
        summary = {
            "total_transactions": len(full_df),
            "legitimate_count": int((full_df["is_fraud"] == 0).sum()),
            "fraud_count": int((full_df["is_fraud"] == 1).sum()),
            "empirical_fraud_ratio": round(float((full_df["is_fraud"] == 1).mean()), 4),
            "attacks_included": list(full_df[full_df["is_fraud"] == 1]["attack_type"].unique()),
            "per_attack_counts": full_df[full_df["is_fraud"] == 1]["attack_type"].value_counts().to_dict(),
            "total_volume_usd": round(float(full_df["amount"].sum()), 2),
            "fraud_volume_usd": round(float(full_df[full_df["is_fraud"] == 1]["amount"].sum()), 2),
            "start_time": full_df["timestamp"].min().isoformat(),
            "end_time": full_df["timestamp"].max().isoformat(),
        }

        return full_df, summary
