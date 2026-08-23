"""Graph Feature Extraction Pipeline for Relational Fraud Detection.

Extracts network topological invariants, node centralities, mule cycle indicators,
and shared infrastructure connectivity metrics from the transaction graph.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from generate.graph_builder import TransactionGraphBuilder


class GraphFeatureExtractor:
    """Extracts graph topological and relational features for Tier-2 detection."""

    GRAPH_FEATURE_NAMES: List[str] = [
        "graph_in_degree",
        "graph_out_degree",
        "graph_fan_out_ratio",
        "graph_total_sent_vol",
        "graph_total_recv_vol",
        "graph_shared_device_count",
        "graph_shared_ip_count",
        "is_in_mule_cycle",
    ]

    def __init__(self, graph_builder: Optional[TransactionGraphBuilder] = None) -> None:
        self.graph_builder = graph_builder or TransactionGraphBuilder()

    def update_graph_from_df(self, df: pd.DataFrame) -> None:
        """Feed a transaction batch into the active graph."""
        self.graph_builder.build_from_dataframe(df)

    def extract_single(self, txn: Dict[str, Any]) -> np.ndarray:
        """Extract graph features for a single transaction based on current graph state."""
        sender = str(txn.get("sender_account", "ACC-UNKNOWN"))
        receiver = str(txn.get("receiver_account", "ACC-UNKNOWN"))

        sender_feats = self.graph_builder.compute_node_features(sender)

        # Fast cycle check: is sender involved in a detected cycle?
        cycles = self.graph_builder.detect_mule_cycles(max_cycle_length=6)
        in_cycle = 1.0 if any(sender in c or receiver in c for c in cycles) else 0.0

        vec = [
            sender_feats["in_degree"],
            sender_feats["out_degree"],
            sender_feats["fan_out_ratio"],
            sender_feats["total_sent_volume"],
            sender_feats["total_received_volume"],
            sender_feats["shared_device_count"],
            sender_feats["shared_ip_count"],
            in_cycle,
        ]
        return np.array(vec, dtype=np.float32)

    def extract_batch(self, df: pd.DataFrame) -> np.ndarray:
        """Extract graph feature matrix for a batch of transactions."""
        matrix = []
        for _, row in df.iterrows():
            matrix.append(self.extract_single(row.to_dict()))
        return np.vstack(matrix)
