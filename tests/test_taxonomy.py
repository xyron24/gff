"""Unit tests for Pillar 1 (IDENTIFY) - Threat Taxonomy & Attack Registry."""

import pytest
from pathlib import Path

from identify.taxonomy import (
    AttackCard,
    AttackCategory,
    DetectionLayer,
    PaymentChannel,
    SeverityLevel,
)
from identify.loader import AttackRegistry, get_default_registry


@pytest.fixture
def registry():
    """Returns a loaded registry instance."""
    return get_default_registry()


def test_registry_loads_all_twelve_attacks(registry: AttackRegistry):
    """Verify that all 12 attack cards are loaded successfully."""
    cards = registry.list_all()
    assert len(cards) == 12, f"Expected 12 attack cards, got {len(cards)}"


def test_attack_card_ids_and_sequence(registry: AttackRegistry):
    """Verify attack card IDs follow ATK-001 through ATK-012 sequentially."""
    expected_ids = [f"ATK-{i:03d}" for i in range(1, 13)]
    loaded_ids = [c.id for c in registry.list_all()]
    assert loaded_ids == expected_ids


def test_attack_card_structural_integrity(registry: AttackRegistry):
    """Verify each attack card has comprehensive metadata, kill chain, and signals."""
    for card in registry.list_all():
        assert isinstance(card, AttackCard)
        assert len(card.name) >= 3
        assert len(card.genai_role) > 20
        assert len(card.attack_description) > 50
        assert len(card.kill_chain) >= 3, f"Card {card.id} must have at least 3 kill chain steps"
        assert len(card.detection_signals) >= 2, f"Card {card.id} must have at least 2 detection signals"
        assert card.iso_mapping.message_type in [
            "pacs.008.001.08",
            "pain.001.001.09",
            "camt.053.001.08",
        ]
        assert len(card.evasion_strategies) >= 1
        assert len(card.mitigation_strategies) >= 1


def test_registry_get_by_id(registry: AttackRegistry):
    """Verify individual attack cards can be retrieved by ID."""
    card = registry.get("ATK-001")
    assert card is not None
    assert card.name == "Agentic Micro-Smurfing"
    assert card.category == AttackCategory.STRUCTURING

    non_existent = registry.get("ATK-999")
    assert non_existent is None


def test_registry_filters(registry: AttackRegistry):
    """Verify filtering by category, channel, and severity."""
    structuring_attacks = registry.filter_by_category(AttackCategory.STRUCTURING)
    assert len(structuring_attacks) >= 1
    assert any(c.id == "ATK-001" for c in structuring_attacks)

    swift_attacks = registry.filter_by_channel(PaymentChannel.WIRE_SWIFT)
    assert len(swift_attacks) >= 1
    assert any(c.id == "ATK-002" for c in swift_attacks)

    critical_attacks = registry.filter_by_severity(SeverityLevel.CRITICAL)
    assert len(critical_attacks) >= 1
    assert any(c.id == "ATK-003" for c in critical_attacks)


def test_summary_dataframe_and_dict_export(registry: AttackRegistry):
    """Verify DataFrame summary and serialization formats."""
    df = registry.summary_dataframe()
    assert len(df) == 12
    assert "ID" in df.columns
    assert "Name" in df.columns
    assert "Category" in df.columns
    assert "ISO Message" in df.columns

    dict_list = registry.to_dict_list()
    assert len(dict_list) == 12
    assert isinstance(dict_list[0], dict)
    assert dict_list[0]["id"] == "ATK-001"
