"""Unit tests for the Simulation Pipeline."""

import pytest
import pandas as pd
from generate.pipeline import SimulationPipeline


def test_simulation_pipeline_end_to_end():
    """Verify that the simulation pipeline generates a balanced mixed dataset with all attacks."""
    pipeline = SimulationPipeline(random_seed=42)
    df, summary = pipeline.generate_dataset(n_total=500, fraud_ratio=0.10)

    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 480
    assert "is_fraud" in df.columns
    assert "attack_type" in df.columns
    assert "timestamp" in df.columns

    # Verify both classes present
    legit_count = (df["is_fraud"] == 0).sum()
    fraud_count = (df["is_fraud"] == 1).sum()
    assert legit_count > 0
    assert fraud_count > 0

    # Verify multiple attack types present
    unique_attacks = df[df["is_fraud"] == 1]["attack_type"].unique()
    assert len(unique_attacks) == 12

    # Verify summary dictionary
    assert summary["total_transactions"] == len(df)
    assert summary["fraud_count"] == int(fraud_count)
    assert summary["legitimate_count"] == int(legit_count)
    assert 0.05 <= summary["empirical_fraud_ratio"] <= 0.20
    assert len(summary["per_attack_counts"]) == 12
    assert summary["total_volume_usd"] > 0.0


def test_simulation_pipeline_selective_attacks():
    """Verify simulation pipeline with a subset of attack vectors."""
    pipeline = SimulationPipeline(random_seed=99)
    selected = ["ATK-001", "ATK-006", "ATK-008"]
    df, summary = pipeline.generate_dataset(n_total=200, fraud_ratio=0.15, selected_attacks=selected)

    unique_attacks = set(df[df["is_fraud"] == 1]["attack_type"].unique())
    assert unique_attacks == set(selected)
    assert len(summary["attacks_included"]) == 3
