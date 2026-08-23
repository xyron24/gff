"""Unit tests for TransactionGraphBuilder (Pillar 2: GENERATE)."""

import pytest
import pandas as pd
from generate.base_generator import BaseTransactionGenerator
from generate.graph_builder import TransactionGraphBuilder


@pytest.fixture
def sample_df():
    gen = BaseTransactionGenerator(num_accounts=30, num_merchants=10, random_seed=99)
    return gen.generate_batch(n=100)


def test_graph_builder_ingestion(sample_df: pd.DataFrame):
    """Verify nodes and edges are populated correctly in heterogeneous graph."""
    builder = TransactionGraphBuilder()
    builder.build_from_dataframe(sample_df)

    assert builder.graph.number_of_nodes() > 30
    assert builder.graph.number_of_edges() > 100

    # Verify node feature extraction
    sample_acc = sample_df["sender_account"].iloc[0]
    feats = builder.compute_node_features(sample_acc)
    assert "out_degree" in feats
    assert "in_degree" in feats
    assert "total_sent_volume" in feats
    assert feats["out_degree"] >= 1.0
    assert feats["total_sent_volume"] > 0.0


def test_graph_mule_cycle_detection():
    """Verify cycle detection identifies synthetic money-mule rings."""
    builder = TransactionGraphBuilder()

    # Create synthetic 3-hop ring: ACC-A -> ACC-B -> ACC-C -> ACC-A
    ring_txns = [
        {"txn_id": "T1", "sender_account": "ACC-A", "receiver_account": "ACC-B", "amount": 1000, "is_fraud": 1},
        {"txn_id": "T2", "sender_account": "ACC-B", "receiver_account": "ACC-C", "amount": 950, "is_fraud": 1},
        {"txn_id": "T3", "sender_account": "ACC-C", "receiver_account": "ACC-A", "amount": 900, "is_fraud": 1},
    ]
    for t in ring_txns:
        builder.add_transaction(t)

    cycles = builder.detect_mule_cycles(max_cycle_length=4)
    assert len(cycles) >= 1
    # Check if cycle contains ACC-A, ACC-B, ACC-C
    cycle_nodes = set(cycles[0])
    assert {"ACC-A", "ACC-B", "ACC-C"}.issubset(cycle_nodes)


def test_graph_to_d3_json(sample_df: pd.DataFrame):
    """Verify serialization to D3 JSON format."""
    builder = TransactionGraphBuilder()
    builder.build_from_dataframe(sample_df)

    d3_data = builder.to_d3_json(max_nodes=50)
    assert "nodes" in d3_data
    assert "links" in d3_data
    assert len(d3_data["nodes"]) <= 50
    assert len(d3_data["links"]) > 0
    assert "id" in d3_data["nodes"][0]
    assert "source" in d3_data["links"][0]
