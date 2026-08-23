"""FastAPI Request and Response Pydantic Schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DetectionRequest(BaseModel):
    transaction: Dict[str, Any] = Field(..., description="Raw transaction dictionary")
    generate_sar: bool = Field(default=False, description="Whether to generate Tier-3 SAR narrative if blocked")


class DetectionResponse(BaseModel):
    txn_id: Optional[str]
    decision: str
    risk_score: float
    tier1_score: float
    tier2_score: Optional[float]
    tier_activated: int
    total_latency_ms: float
    tier1_latency_ms: float
    tier2_latency_ms: float
    is_fraud_ground_truth: int
    sar_report: Optional[Dict[str, Any]] = None


class BatchDetectionRequest(BaseModel):
    transactions: List[Dict[str, Any]]


class BatchDetectionResponse(BaseModel):
    total_scored: int
    results: List[DetectionResponse]
    mean_latency_ms: float


class GenerationRequest(BaseModel):
    n_transactions: int = Field(default=100, ge=10, le=10000)
    fraud_ratio: float = Field(default=0.10, ge=0.0, le=1.0)
    selected_attacks: Optional[List[str]] = Field(default=None, description="Optional subset of ATK-001..ATK-012")


class GenerationResponse(BaseModel):
    summary: Dict[str, Any]
    transactions: List[Dict[str, Any]]


class RunEpochRequest(BaseModel):
    n_transactions: int = Field(default=500, ge=50, le=5000)
    fraud_ratio: float = Field(default=0.15, ge=0.0, le=1.0)
    retrain_defense: bool = Field(default=True)


class RunEpochResponse(BaseModel):
    epoch_record: Dict[str, Any]


class SystemHealthResponse(BaseModel):
    status: str
    version: str
    models_ready: bool
    total_attacks_registered: int
    replay_buffer_size: int
    co_evolution_epochs_completed: int
