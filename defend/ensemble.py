"""Cascading Multi-Tier Detection Grid.

Implements sub-30ms production-viable payment switch authorization cascade:
Tier 1 (Fast Tabular GBDT, <1ms) -> Tier 2 (Temporal GNN, <25ms) -> Tier 3 (Async LLM SAR Explainer).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from defend.tier1_gbdt.model import Tier1GBDTClassifier
from defend.tier2_gnn.model import Tier2TemporalGNN
from defend.tier3_explainer.explainer import Tier3LLMExplainer


class DetectionGrid:
    """Production-grade cascading fraud defense grid."""

    def __init__(
        self,
        tier1: Optional[Tier1GBDTClassifier] = None,
        tier2: Optional[Tier2TemporalGNN] = None,
        tier3: Optional[Tier3LLMExplainer] = None,
        tier1_low_threshold: float = 0.25,
        tier1_high_threshold: float = 0.85,
        block_threshold: float = 0.60,
    ) -> None:
        self.tier1 = tier1 or Tier1GBDTClassifier()
        self.tier2 = tier2 or Tier2TemporalGNN()
        self.tier3 = tier3 or Tier3LLMExplainer()

        self.tier1_low_threshold = tier1_low_threshold
        self.tier1_high_threshold = tier1_high_threshold
        self.block_threshold = block_threshold

    def score_transaction(
        self,
        txn: Dict[str, Any],
        generate_sar: bool = False,
    ) -> Dict[str, Any]:
        """Score a single transaction through the cascading multi-tier defense grid.

        Returns:
            Dict containing decision (APPROVE/CHALLENGE/BLOCK), final risk score,
            total latency in milliseconds, tier activations, and SAR package if flagged.
        """
        t_start = time.perf_counter()

        # Tier 1: Sub-millisecond tabular check
        t1_score, t1_lat = self.tier1.predict_proba_single(txn)

        decision = "APPROVE"
        final_score = t1_score
        tier_activated = 1
        t2_score = None
        t2_lat = 0.0

        if t1_score <= self.tier1_low_threshold:
            # Fast Path: Approved directly by Tier 1
            decision = "APPROVE"
        elif t1_score >= self.tier1_high_threshold:
            # Fast Path: Blocked directly by Tier 1
            decision = "BLOCK"
        else:
            # Escalation Path: Ambiguous risk -> Tier 2 Temporal GNN (<25ms)
            tier_activated = 2
            t2_score, t2_lat = self.tier2.predict_proba_single(txn)
            final_score = 0.40 * t1_score + 0.60 * t2_score

            if final_score >= self.block_threshold:
                decision = "BLOCK"
            elif final_score >= 0.45:
                decision = "CHALLENGE"  # Step-up 3DS / biometric challenge
            else:
                decision = "APPROVE"

        total_latency_ms = (time.perf_counter() - t_start) * 1000.0

        # Optional Tier 3 Async SAR Generation on High-Risk Blocks
        sar_report = None
        if (decision == "BLOCK" or generate_sar) and self.tier3:
            suspected = txn.get("attack_type") or "ATK-001"
            sar_report = self.tier3.generate_sar_report(
                txn=txn,
                tier1_score=t1_score,
                tier2_score=t2_score or t1_score,
                suspected_attack=suspected,
            )

        return {
            "txn_id": txn.get("txn_id"),
            "decision": decision,
            "risk_score": round(float(final_score), 4),
            "tier1_score": round(float(t1_score), 4),
            "tier2_score": round(float(t2_score), 4) if t2_score is not None else None,
            "tier_activated": tier_activated,
            "total_latency_ms": round(float(total_latency_ms), 3),
            "tier1_latency_ms": round(float(t1_lat), 3),
            "tier2_latency_ms": round(float(t2_lat), 3),
            "is_fraud_ground_truth": int(txn.get("is_fraud", 0)),
            "sar_report": sar_report,
        }
