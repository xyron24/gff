"""Unit tests for all 12 Attack Injectors (Pillar 2: GENERATE)."""

import pytest
import pandas as pd
from generate.base_generator import BaseTransactionGenerator
from generate.attack_injectors import INJECTOR_REGISTRY, get_injector


@pytest.fixture
def baseline_df():
    gen = BaseTransactionGenerator(num_accounts=20, num_merchants=5, random_seed=42)
    return gen.generate_batch(n=50)


def test_registry_contains_twelve_injectors():
    """Verify registry has all 12 injectors matching ATK-001 through ATK-012."""
    assert len(INJECTOR_REGISTRY) == 12
    for i in range(1, 13):
        atk_id = f"ATK-{i:03d}"
        assert atk_id in INJECTOR_REGISTRY


@pytest.mark.parametrize("atk_id", [f"ATK-{i:03d}" for i in range(1, 13)])
def test_all_injectors_produce_valid_attack_batches(atk_id: str, baseline_df: pd.DataFrame):
    """Verify that every single injector executes cleanly and produces labeled attack rows."""
    injector = get_injector(atk_id)
    n_attacks = 15
    df = injector.inject(baseline_df=baseline_df, n_attacks=n_attacks)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == n_attacks
    assert (df["is_fraud"] == 1).all(), f"All rows in {atk_id} batch must have is_fraud=1"
    assert (df["attack_type"] == atk_id).all(), f"attack_type must equal {atk_id}"
    assert "txn_id" in df.columns
    assert "amount" in df.columns
    assert "timestamp" in df.columns
    assert "sender_account" in df.columns
    assert "receiver_account" in df.columns
    assert "evasion_strategy" in df.columns
    assert (df["amount"] > 0).all()
