"""Threat Taxonomy & Attack Registry API Router."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from identify.loader import get_default_registry
from identify.taxonomy import AttackCategory, PaymentChannel, SeverityLevel

router = APIRouter(prefix="/api/attacks", tags=["Threat Taxonomy"])


@router.get("", response_model=List[Dict[str, Any]])
def list_attack_cards(
    category: Optional[str] = Query(None, description="Filter by category e.g. structuring, voice_biometric_spoofing"),
    channel: Optional[str] = Query(None, description="Filter by payment channel e.g. wire_swift, card_not_present"),
    severity: Optional[str] = Query(None, description="Filter by severity e.g. CRITICAL, HIGH"),
):
    """Retrieve all registered GenAI attack vectors with optional category/channel filters."""
    registry = get_default_registry()
    cards = registry.list_all()

    if category:
        cards = [c for c in cards if c.category == category]
    if channel:
        cards = [c for c in cards if c.channel == channel]
    if severity:
        cards = [c for c in cards if c.severity == severity]

    return [c.model_dump() for c in cards]


@router.get("/{attack_id}", response_model=Dict[str, Any])
def get_attack_detail(attack_id: str):
    """Retrieve full attack card specifications, kill chain, detection signals, and ISO mappings."""
    registry = get_default_registry()
    card = registry.get(attack_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Attack vector {attack_id} not found in registry.")
    return card.model_dump()
