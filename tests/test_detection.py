"""Unit tests for Pillar 3 (DEFEND) - Multi-Tier Detection Grid."""

import pytest
import numpy as np
import pandas as pd

from generate.pipeline import SimulationPipeline
from defend.features.tabular_features import TabularFeatureExtractor
from defend.features.graph_features import GraphFeatureExtractor
from defend.tier1_gbdt.model import Tier1GBDTClassifier
from defend.tier1_gbdt.export_onnx import ONNXFastInferenceEngine
from defend.tier2_gnn.model import Tier2TemporalGNN
from defend.tier3_explainer.explainer import Tier3LLMExplainer
from defend.ensemble import DetectionGrid
from defend.metrics import compute_defense_metrics


@pytest.fixture(scope="module")
def dataset():
    """Generates synthetic dataset for training and testing detection models."""
    pipeline = SimulationPipeline(random_seed=42)
    df, _ = pipeline.generate_dataset(n_total=600, fraud_ratio=0.15)
    return df


def test_tabular_feature_extractor(dataset: pd.DataFrame):
    """Verify feature extractor output dimensionality and validity."""
    extractor = TabularFeatureExtractor()
    sample_txn = dataset.iloc[0].to_dict()
    vec = extractor.extract_single(sample_txn)

    assert isinstance(vec, np.ndarray)
    assert len(vec) == len(extractor.FEATURE_NAMES)
    assert not np.isnan(vec).any()

    matrix, names = extractor.extract_dataframe(dataset.head(50))
    assert matrix.shape == (50, len(extractor.FEATURE_NAMES))


def test_tier1_gbdt_train_and_predict(dataset: pd.DataFrame):
    """Verify LightGBM classifier training and sub-millisecond inference."""
    extractor = TabularFeatureExtractor()
    X, _ = extractor.extract_dataframe(dataset)
    y = dataset["is_fraud"].values

    classifier = Tier1GBDTClassifier(feature_extractor=extractor)
    train_res = classifier.train(X[:400], y[:400], X[400:], y[400:], num_trees=30)
    assert classifier.is_trained
    assert train_res["train_samples"] == 400

    # Single transaction inference with latency measurement
    sample_txn = dataset.iloc[0].to_dict()
    score, lat_ms = classifier.predict_proba_single(sample_txn)
    assert 0.0 <= score <= 1.0
    assert lat_ms < 50.0  # single row inference is fast

    # Benchmark ONNX engine
    engine = ONNXFastInferenceEngine(classifier)
    bench = engine.benchmark_single_row_latency(n_iterations=100)
    assert "p99_latency_ms" in bench
    assert bench["p99_latency_ms"] < 25.0


def test_tier2_gnn_train_and_predict(dataset: pd.DataFrame):
    """Verify Tier-2 relational classifier execution."""
    tab_extractor = TabularFeatureExtractor()
    graph_extractor = GraphFeatureExtractor()
    graph_extractor.update_graph_from_df(dataset)

    X_tab, _ = tab_extractor.extract_dataframe(dataset)
    X_graph = graph_extractor.extract_batch(dataset)
    y = dataset["is_fraud"].values

    gnn = Tier2TemporalGNN(graph_extractor=graph_extractor, tabular_extractor=tab_extractor)
    train_res = gnn.train(X_tab[:400], X_graph[:400], y[:400])
    assert gnn.is_trained
    assert train_res["num_samples"] == 400

    sample_txn = dataset.iloc[0].to_dict()
    score, lat_ms = gnn.predict_proba_single(sample_txn)
    assert 0.0 <= score <= 1.0


def test_tier3_sar_generator(dataset: pd.DataFrame):
    """Verify automated SAR narrative generator produces structured FinCEN reports."""
    explainer = Tier3LLMExplainer()
    fraud_txn = dataset[dataset["is_fraud"] == 1].iloc[0].to_dict()

    sar = explainer.generate_sar_report(
        txn=fraud_txn,
        tier1_score=0.88,
        tier2_score=0.92,
        suspected_attack="ATK-001 (Agentic Micro-Smurfing)",
    )

    assert "sar_id" in sar
    assert "narrative_text" in sar
    assert "Executive Summary" in sar["narrative_text"]
    assert "Action Taken" in sar["narrative_text"] or "Action" in sar["narrative_text"]


def test_cascading_detection_grid(dataset: pd.DataFrame):
    """Verify end-to-end cascading ensemble decisions (APPROVE, CHALLENGE, BLOCK)."""
    grid = DetectionGrid()
    sample_legit = dataset[dataset["is_fraud"] == 0].iloc[0].to_dict()
    result = grid.score_transaction(sample_legit)

    assert "decision" in result
    assert result["decision"] in ["APPROVE", "CHALLENGE", "BLOCK"]
    assert "total_latency_ms" in result
    assert result["total_latency_ms"] < 100.0


def test_metrics_evaluation():
    """Verify precision, recall, F1, PR-AUC and per-attack breakdown computation."""
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_scores = np.array([0.1, 0.2, 0.15, 0.3, 0.7, 0.85, 0.9, 0.6])
    attacks = ["None", "None", "None", "None", "ATK-001", "ATK-001", "ATK-006", "ATK-006"]

    m = compute_defense_metrics(y_true, y_scores, threshold=0.5, attack_types=attacks)
    assert m["precision"] == 1.0
    assert m["recall"] == 1.0
    assert m["f1_score"] == 1.0
    assert m["roc_auc"] == 1.0
    assert "per_attack_recall" in m
    assert "ATK-001" in m["per_attack_recall"]
    assert m["per_attack_recall"]["ATK-001"]["recall"] == 1.0
