"""Transaction Data Schema & Record Definitions.

Defines the canonical data structures for payment transactions, device telemetry,
and graph nodes used across the simulation and detection grid.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TransactionChannel(str, Enum):
    POS = "POS"
    ONLINE = "ONLINE"
    WIRE = "WIRE"
    P2P = "P2P"
    ATM = "ATM"
    API = "API"


class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    SGD = "SGD"
    AED = "AED"
    INR = "INR"
    JPY = "JPY"


class PaymentTransaction(BaseModel):
    """Canonical payment transaction record."""

    # Identifiers
    txn_id: str = Field(..., description="Unique transaction ID e.g. TXN-100293")
    timestamp: datetime = Field(..., description="UTC timestamp of transaction initiation")
    sender_account: str = Field(..., description="Originating account / IBAN / Card ID")
    receiver_account: str = Field(..., description="Beneficiary account / IBAN / Merchant ID")
    sender_bank_bic: str = Field(default="MSTRUS33XXX", description="Originating BIC")
    receiver_bank_bic: str = Field(default="CHASUS33XXX", description="Beneficiary BIC")

    # Transaction Details
    amount: float = Field(..., gt=0.0, description="Transaction monetary amount")
    currency: CurrencyCode = Field(default=CurrencyCode.USD)
    channel: TransactionChannel = Field(default=TransactionChannel.ONLINE)
    mcc: str = Field(default="5411", description="Merchant Category Code (e.g. 5411 Grocery, 5732 Electronics)")
    mcc_description: str = Field(default="Grocery Stores, Supermarkets")

    # Device & Network Telemetry
    device_id: str = Field(..., description="Unique hardware canvas/IMEI fingerprint hash")
    ip_address: str = Field(..., description="Client IP address")
    ip_country: str = Field(default="US", description="Two-letter ISO country code")
    user_agent: str = Field(default="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4)", description="Client browser / app agent")
    is_foreign_transaction: bool = Field(default=False)

    # Passive Behavioral Telemetry
    session_duration_sec: float = Field(default=45.0, ge=0.0, description="Dwell time in checkout flow")
    biometric_friction_score: float = Field(default=0.05, ge=0.0, le=1.0, description="0=Human, 1=Bot anomaly")

    # Payment Message Envelope
    iso_message_type: str = Field(default="pacs.008.001.08")
    remittance_info: str = Field(default="Monthly invoice settlement", description="Unstructured remittance text")
    purpose_code: str = Field(default="GDDS", description="ISO 20022 Purpose Code e.g. GDDS, INTE, SALA")

    # Ground Truth Labels (Set by Simulator)
    is_fraud: int = Field(default=0, ge=0, le=1, description="0=Legitimate, 1=Fraud")
    attack_type: Optional[str] = Field(default=None, description="Attack vector ID e.g. ATK-001")
    evasion_strategy: Optional[str] = Field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with ISO formatted datetime."""
        d = self.model_dump()
        d["timestamp"] = self.timestamp.isoformat()
        return d


class GraphNode(BaseModel):
    """Graph node representation for temporal payment network."""
    node_id: str
    node_type: str  # Account, Merchant, Device, IP
    created_at: datetime
    risk_prior: float = 0.0
    attributes: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Graph edge representing a transaction or authentication link."""
    source_id: str
    target_id: str
    edge_type: str  # TRANSACTS_WITH, AUTHENTICATES_FROM, RESOLVES_TO
    timestamp: datetime
    amount: float = 0.0
    is_fraud: int = 0
    attack_type: Optional[str] = None
