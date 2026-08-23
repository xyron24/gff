"""Attack Injectors Module.

Exports all 12 pluggable attack injection modules and an injector factory.
"""

from typing import Dict, Type

from generate.attack_injectors.base import AttackInjector
from generate.attack_injectors.micro_smurfing import MicroSmurfingInjector
from generate.attack_injectors.deepfake_auth import DeepfakeAuthInjector
from generate.attack_injectors.synthetic_identity import SyntheticIdentityInjector
from generate.attack_injectors.metadata_tamper import MetadataTamperInjector
from generate.attack_injectors.biometric_masquerade import BiometricMasqueradeInjector
from generate.attack_injectors.mule_ring import MuleRingInjector
from generate.attack_injectors.llm_phishing import LLMPhishingInjector
from generate.attack_injectors.feature_perturbation import FeaturePerturbationInjector
from generate.attack_injectors.ghost_merchant import GhostMerchantInjector
from generate.attack_injectors.fx_arbitrage import FXArbitrageInjector
from generate.attack_injectors.token_replay import TokenReplayInjector
from generate.attack_injectors.session_hijack import SessionHijackInjector

INJECTOR_REGISTRY: Dict[str, Type[AttackInjector]] = {
    "ATK-001": MicroSmurfingInjector,
    "ATK-002": DeepfakeAuthInjector,
    "ATK-003": SyntheticIdentityInjector,
    "ATK-004": MetadataTamperInjector,
    "ATK-005": BiometricMasqueradeInjector,
    "ATK-006": MuleRingInjector,
    "ATK-007": LLMPhishingInjector,
    "ATK-008": FeaturePerturbationInjector,
    "ATK-009": GhostMerchantInjector,
    "ATK-010": FXArbitrageInjector,
    "ATK-011": TokenReplayInjector,
    "ATK-012": SessionHijackInjector,
}


def get_injector(attack_id: str) -> AttackInjector:
    """Retrieve initialized attack injector instance by ID."""
    cls = INJECTOR_REGISTRY.get(attack_id.upper())
    if not cls:
        raise ValueError(f"Unknown attack injector: {attack_id}. Available: {list(INJECTOR_REGISTRY.keys())}")
    return cls()


__all__ = [
    "AttackInjector",
    "INJECTOR_REGISTRY",
    "get_injector",
    "MicroSmurfingInjector",
    "DeepfakeAuthInjector",
    "SyntheticIdentityInjector",
    "MetadataTamperInjector",
    "BiometricMasqueradeInjector",
    "MuleRingInjector",
    "LLMPhishingInjector",
    "FeaturePerturbationInjector",
    "GhostMerchantInjector",
    "FXArbitrageInjector",
    "TokenReplayInjector",
    "SessionHijackInjector",
]
