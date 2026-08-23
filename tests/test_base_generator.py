"""Unit tests for BaseTransactionGenerator (Pillar 2: GENERATE)."""

import pytest
import pandas as pd
from datetime import datetime, timezone

from generate.base_generator import BaseTransactionGenerator
from data.schema import PaymentTransaction


@pytest.fixture
def generator():
    return BaseTransactionGenerator(num_accounts=50, num_merchants=20, random_seed=123)


def test_generate_single_transaction(generator: BaseTransactionGenerator):
    """Verify single transaction creation and attribute validity."""
    txn = generator.generate_single_transaction()
    assert isinstance(txn, PaymentTransaction)
    assert txn.txn_id.startswith("TXN-")
    assert txn.amount > 0.0
    assert txn.is_fraud == 0
    assert txn.attack_type is None
    assert txn.sender_account.startswith("ACC-")
    assert txn.receiver_account.startswith("MERCH-") or txn.receiver_account.startswith("ACC-")
    assert txn.mcc in ["5411", "5812", "5814", "5541", "5311", "5732", "4829", "3000", "7011", "5942"]


def test_generate_batch_dataframe(generator: BaseTransactionGenerator):
    """Verify batch DataFrame synthesis."""
    df = generator.generate_batch(n=200, time_span_days=3.0)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 200
    assert "txn_id" in df.columns
    assert "amount" in df.columns
    assert "timestamp" in df.columns
    assert "is_fraud" in df.columns
    assert df["is_fraud"].sum() == 0  # all baseline legitimate

    # Amounts must be strictly positive
    assert (df["amount"] > 0).all()
    assert df["amount"].mean() > 5.0

    # Sorted by timestamp
    assert df["timestamp"].is_monotonic_increasing
