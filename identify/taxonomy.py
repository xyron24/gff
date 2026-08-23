"""Threat Taxonomy & Attack Card Data Models.

Defines the structured schemas for cataloging, validating, and querying
novel GenAI-powered payment fraud vectors in the Mastercard AI Defense Lab.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AttackCategory(str, Enum):
    """Primary categorizations of GenAI fraud attacks."""
    STRUCTURING = "structuring"
    IDENTITY_SYNTHESIS = "identity_synthesis"
    VOICE_BIOMETRIC_SPOOFING = "voice_biometric_spoofing"
    METADATA_TAMPERING = "metadata_tampering"
    BEHAVIORAL_MIMICRY = "behavioral_mimicry"
    GRAPH_MULE_ORCHESTRATION = "graph_mule_orchestration"
    SOCIAL_ENGINEERING_BEC = "social_engineering_bec"
    ADVERSARIAL_PERTURBATION = "adversarial_perturbation"
    MERCHANT_COLLUSION = "merchant_collusion"
    CROSS_BORDER_LAYERING = "cross_border_layering"
    TOKEN_EXPLOITATION = "token_exploitation"
    ACCOUNT_TAKEOVER = "account_takeover"


class PaymentChannel(str, Enum):
    """Payment channels and rails targeted by the attacks."""
    CARD_NOT_PRESENT = "card_not_present"
    CARD_PRESENT = "card_present"
    WIRE_SWIFT = "wire_swift"
    ACH_BATCH = "ach_batch"
    P2P_REALTIME = "p2p_realtime"
    CROSS_BORDER_REMITTANCE = "cross_border_remittance"
    MOBILE_WALLET_NFC = "mobile_wallet_nfc"
    OPEN_BANKING_API = "open_banking_api"


class SeverityLevel(str, Enum):
    """Risk/severity classification of the attack vector."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionLayer(str, Enum):
    """Defense tier best suited to intercept the attack."""
    TIER_1_GBDT = "Tier 1 (Fast Tabular GBDT)"
    TIER_2_GNN = "Tier 2 (Temporal Graph Neural Network)"
    TIER_3_LLM = "Tier 3 (Cognitive SAR Explainer / Policy)"
    MULTI_TIER = "Multi-Tier Cascaded"


class KillChainStage(BaseModel):
    """A discrete stage in the adversary attack lifecycle."""
    step_number: int = Field(..., ge=1, le=10, description="Chronological sequence number")
    stage_name: str = Field(..., description="Stage title e.g. Reconnaissance, Synthesis, Injection")
    adversary_action: str = Field(..., description="Tactical action performed by the fraudster/agent")
    genai_technique: str = Field(..., description="GenAI model or method leveraged (e.g. LLM, Diffusion, Voice Clone)")


class DetectionSignal(BaseModel):
    """Telemetry indicator used by the defense grid to flag the attack."""
    signal_id: str = Field(..., description="Unique signal identifier e.g. SIG-SMURF-01")
    indicator: str = Field(..., description="Observable anomaly or pattern")
    telemetry_source: str = Field(..., description="Source data stream e.g. ISO 20022 XML, Device Fingerprint, Graph Ledger")
    recommended_layer: DetectionLayer = Field(default=DetectionLayer.TIER_1_GBDT)
    evasion_difficulty: str = Field(default="Medium", description="Estimated attacker difficulty to evade (Low/Medium/High)")


class ISOMapping(BaseModel):
    """Mapping of attack attributes into standard ISO 20022 message structures."""
    message_type: str = Field(..., description="ISO 20022 message type e.g. pacs.008.001.08, pain.001.001.09")
    impacted_elements: List[str] = Field(default_factory=list, description="XML XPath or tag names targeted")
    tampering_pattern: Optional[str] = Field(None, description="How the payload or metadata is manipulated")


class SimulationParams(BaseModel):
    """Configurable hyperparameters for generating and simulating this attack."""
    default_intensity: float = Field(default=1.0, ge=0.0, le=5.0)
    tunable_parameters: Dict[str, Any] = Field(default_factory=dict)
    synthetic_noise_level: float = Field(default=0.05, ge=0.0, le=1.0)
    target_evasion_rate: float = Field(default=0.75, ge=0.0, le=1.0)


class AttackCard(BaseModel):
    """Complete specification of a GenAI Payment Fraud Attack Vector."""
    id: str = Field(..., pattern=r"^ATK-\d{3}$", description="Unique vector ID e.g. ATK-001")
    name: str = Field(..., min_length=3, description="Descriptive title of the attack")
    category: AttackCategory = Field(..., description="Taxonomy category")
    channel: PaymentChannel = Field(..., description="Targeted payment rail/channel")
    severity: SeverityLevel = Field(default=SeverityLevel.HIGH)
    genai_role: str = Field(..., description="Concise summary of how GenAI is leveraged in the attack")
    attack_description: str = Field(..., description="Comprehensive explanation of mechanics and intent")
    kill_chain: List[KillChainStage] = Field(..., min_length=3)
    detection_signals: List[DetectionSignal] = Field(..., min_length=2)
    iso_mapping: ISOMapping = Field(...)
    simulation_params: SimulationParams = Field(default_factory=SimulationParams)
    evasion_strategies: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)
    real_world_precedent: Optional[str] = Field(None, description="Known industry case or emerging threat intelligence reference")

    model_config = ConfigDict(use_enum_values=True)
