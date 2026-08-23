"""Unit tests for ISO 20022 formatting and parsing (Pillar 2: GENERATE)."""

import pytest
from generate.base_generator import BaseTransactionGenerator
from generate.iso20022_formatter import (
    format_pacs008,
    format_pain001,
    parse_iso_message,
    inspect_unicode_anomalies,
)


@pytest.fixture
def sample_txn():
    gen = BaseTransactionGenerator(num_accounts=10, num_merchants=5, random_seed=42)
    return gen.generate_single_transaction()


def test_format_pacs008_valid_xml(sample_txn):
    """Verify pacs.008 XML format generation and structure."""
    xml_str = format_pacs008(sample_txn)
    assert xml_str.startswith("<?xml")
    assert "<FIToFICstmrCdtTrf>" in xml_str
    assert f"<TxId>{sample_txn.txn_id}</TxId>" in xml_str
    assert f"{sample_txn.amount:.2f}" in xml_str

    # Test parsing back
    parsed = parse_iso_message(xml_str)
    assert parsed["txn_id"] == sample_txn.txn_id
    assert abs(parsed["amount"] - sample_txn.amount) < 0.01
    assert parsed["sender_account"] == sample_txn.sender_account
    assert parsed["receiver_account"] == sample_txn.receiver_account


def test_format_pain001_valid_xml(sample_txn):
    """Verify pain.001 customer credit transfer initiation XML structure."""
    xml_str = format_pain001(sample_txn)
    assert "<CstmrCdtTrfInitn>" in xml_str
    assert f"PMT-{sample_txn.txn_id}" in xml_str

    parsed = parse_iso_message(xml_str)
    assert parsed["txn_id"] == f"E2E-{sample_txn.txn_id}" or parsed["txn_id"] == sample_txn.txn_id
    assert abs(parsed["amount"] - sample_txn.amount) < 0.01


def test_unicode_anomaly_inspection():
    """Verify homoglyph and zero-width character detection for ATK-004 screening."""
    clean_text = "Standard invoice payment for consultancy services"
    clean_result = inspect_unicode_anomalies(clean_text)
    assert clean_result["has_anomalies"] is False
    assert clean_result["zero_width_count"] == 0

    # Inject zero-width space and Cyrillic 'a' (\u0430)
    tampered_text = "St\u200Band\u0430rd invoice p\u200Bayment"
    tampered_result = inspect_unicode_anomalies(tampered_text)
    assert tampered_result["has_anomalies"] is True
    assert tampered_result["zero_width_count"] == 2
    assert "CYRILLIC" in tampered_result["scripts"]
