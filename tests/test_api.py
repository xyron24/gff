"""Unit tests for FastAPI REST Endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify /health status returns healthy and registered attacks count."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert data["total_attacks_registered"] == 12
    assert data["models_ready"] is True


def test_list_and_filter_attacks():
    """Verify /api/attacks listing and query filtering."""
    resp = client.get("/api/attacks")
    assert resp.status_code == 200
    cards = resp.json()
    assert len(cards) == 12

    # Filter by category
    resp_cat = client.get("/api/attacks?category=structuring")
    assert resp_cat.status_code == 200
    cat_cards = resp_cat.json()
    assert len(cat_cards) >= 1
    assert any(c["id"] == "ATK-001" for c in cat_cards)

    # Get single attack detail
    resp_detail = client.get("/api/attacks/ATK-001")
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    assert detail["name"] == "Agentic Micro-Smurfing"
    assert len(detail["kill_chain"]) >= 3


def test_generate_transactions_api():
    """Verify /api/generate produces synthetic datasets with ISO previews."""
    payload = {
        "n_transactions": 50,
        "fraud_ratio": 0.20,
        "selected_attacks": ["ATK-001", "ATK-006"],
    }
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "transactions" in data
    assert len(data["transactions"]) >= 45
    assert "iso_xml_preview" in data["transactions"][0]


def test_detect_single_and_batch_api():
    """Verify /api/detect real-time transaction scoring."""
    sample_txn = {
        "txn_id": "TXN-TEST-API-01",
        "amount": 25000.0,
        "channel": "WIRE",
        "sender_account": "ACC-001",
        "receiver_account": "ACC-OFFSHORE",
        "mcc": "4829",
        "session_duration_sec": 4.0,
        "biometric_friction_score": 0.02,
    }

    # Single transaction detection
    resp = client.post("/api/detect", json={"transaction": sample_txn, "generate_sar": True})
    assert resp.status_code == 200
    data = resp.json()
    assert "decision" in data
    assert "risk_score" in data
    assert "total_latency_ms" in data
    assert data["total_latency_ms"] < 100.0

    # Batch detection
    batch_resp = client.post("/api/detect/batch", json={"transactions": [sample_txn, sample_txn]})
    assert batch_resp.status_code == 200
    batch_data = batch_resp.json()
    assert batch_data["total_scored"] == 2
    assert len(batch_data["results"]) == 2


def test_dashboard_kpis_and_graph_api():
    """Verify dashboard KPI metrics and D3 graph endpoints."""
    resp_kpi = client.get("/api/dashboard/metrics")
    assert resp_kpi.status_code == 200
    kpi_data = resp_kpi.json()
    assert "kpis" in kpi_data
    assert "tier1_latency_p99_ms" in kpi_data["kpis"]

    resp_graph = client.get("/api/dashboard/graph?max_nodes=50")
    assert resp_graph.status_code == 200
    graph_data = resp_graph.json()
    assert "nodes" in graph_data
    assert "links" in graph_data


def test_closed_loop_run_epoch_api():
    """Verify /api/loop/run-epoch triggers co-evolution cycle."""
    resp = client.post("/api/loop/run-epoch", json={"n_transactions": 150, "fraud_ratio": 0.15})
    assert resp.status_code == 200
    data = resp.json()
    assert "epoch_record" in data
    assert data["epoch_record"]["transactions_simulated"] >= 140

    # Verify history
    resp_hist = client.get("/api/loop/history")
    assert resp_hist.status_code == 200
    hist = resp_hist.json()
    assert len(hist) >= 1
