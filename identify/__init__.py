"""Threat Identification & Taxonomy Package (Pillar 1: IDENTIFY).

Exposes core threat taxonomy classes, attack card schemas, and registry loader.
"""

from identify.taxonomy import (
    AttackCard,
    AttackCategory,
    DetectionLayer,
    DetectionSignal,
    ISOMapping,
    KillChainStage,
    PaymentChannel,
    SeverityLevel,
    SimulationParams,
)
from identify.loader import AttackRegistry, get_default_registry

__all__ = [
    "AttackCard",
    "AttackCategory",
    "DetectionLayer",
    "DetectionSignal",
    "ISOMapping",
    "KillChainStage",
    "PaymentChannel",
    "SeverityLevel",
    "SimulationParams",
    "AttackRegistry",
    "get_default_registry",
]
