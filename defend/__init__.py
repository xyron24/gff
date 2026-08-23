"""Defend Package (Pillar 3: DEFEND).

Exports multi-tier detection models, feature extractors, cascading ensemble, and metrics.
"""

from defend.ensemble import DetectionGrid
from defend.metrics import compute_defense_metrics
from defend.tier1_gbdt import Tier1GBDTClassifier, ONNXFastInferenceEngine
from defend.tier2_gnn import Tier2TemporalGNN
from defend.tier3_explainer import Tier3LLMExplainer

__all__ = [
    "DetectionGrid",
    "compute_defense_metrics",
    "Tier1GBDTClassifier",
    "ONNXFastInferenceEngine",
    "Tier2TemporalGNN",
    "Tier3LLMExplainer",
]
