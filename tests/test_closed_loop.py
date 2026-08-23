"""Unit tests for Co-Evolution & Closed-Loop Engine."""

import pytest
import numpy as np
import pandas as pd

from generate.pipeline import SimulationPipeline
from generate.rl_red_agent import RedTeamRLAgent
from closed_loop.false_negative_miner import FalseNegativeMiner
from closed_loop.replay_buffer import ExperienceReplayBuffer
from closed_loop.loop_orchestrator import ClosedLoopOrchestrator


def test_false_negative_miner():
    """Verify false negative mining and per-attack evasion calculation."""
    miner = FalseNegativeMiner(block_threshold=0.50)

    df = pd.DataFrame({
        "txn_id": ["T1", "T2", "T3", "T4", "T5"],
        "is_fraud": [0, 1, 1, 1, 0],
        "attack_type": [None, "ATK-001", "ATK-001", "ATK-006", None],
    })
    # T2 is caught (0.8), T3 evades (0.3), T4 evades (0.4)
    scores = np.array([0.05, 0.80, 0.30, 0.40, 0.10])

    fn_df, diag = miner.mine_false_negatives(df, scores)

    assert len(fn_df) == 2
    assert set(fn_df["txn_id"]) == {"T3", "T4"}
    assert diag["total_false_negatives"] == 2
    assert diag["overall_evasion_rate"] == round(2 / 3, 4)
    assert "ATK-001" in diag["per_vector_evasion"]
    assert diag["per_vector_evasion"]["ATK-001"]["evasion_rate"] == 0.50
    assert diag["per_vector_evasion"]["ATK-006"]["evasion_rate"] == 1.0


def test_experience_replay_buffer():
    """Verify buffer storage, FIFO eviction, and hardened sampling."""
    buffer = ExperienceReplayBuffer(max_capacity=50)

    df1 = pd.DataFrame({
        "txn_id": [f"TXN-{i}" for i in range(30)],
        "is_fraud": [0] * 25 + [1] * 5,
        "attack_type": [None] * 25 + ["ATK-001"] * 5,
    })
    buffer.add_transactions(df1)
    assert buffer.size() == 30

    # Add more to trigger FIFO eviction
    df2 = pd.DataFrame({
        "txn_id": [f"TXN-{i+30}" for i in range(30)],
        "is_fraud": [0] * 20 + [1] * 10,
        "attack_type": [None] * 20 + ["ATK-006"] * 10,
    })
    buffer.add_transactions(df2)
    assert buffer.size() == 50  # capped at max_capacity

    hardened = buffer.sample_hardened_dataset(n_samples=20, target_fraud_ratio=0.30)
    assert len(hardened) == 20
    assert (hardened["is_fraud"] == 1).sum() == 6  # 30% of 20


def test_red_team_rl_agent():
    """Verify Red-Team Boltzmann policy distribution and Q-learning updates."""
    agent = RedTeamRLAgent(learning_rate=0.2, exploration_rate=0.1)

    dist = agent.get_attack_distribution()
    assert len(dist) == 12
    assert abs(sum(dist.values()) - 1.0) < 1e-4

    # Simulate diagnostic feedback where ATK-001 evades 90% of the time
    diag = {
        "overall_evasion_rate": 0.55,
        "defense_catch_rate": 0.45,
        "per_vector_evasion": {
            "ATK-001": {"total_attempts": 20, "evasion_rate": 0.90},
            "ATK-002": {"total_attempts": 20, "evasion_rate": 0.10},
        },
    }
    update_res = agent.update_policy(diag)
    assert "policy_updates" in update_res
    # ATK-001 Q-value should increase, ATK-002 Q-value should decrease
    assert agent.q_values["ATK-001"] > agent.q_values["ATK-002"]


def test_closed_loop_orchestrator_epoch():
    """Verify end-to-end execution of a closed-loop co-evolution epoch."""
    orchestrator = ClosedLoopOrchestrator()
    epoch_res = orchestrator.run_epoch(n_transactions=300, fraud_ratio=0.15, retrain_defense=True)

    assert "epoch" in epoch_res
    assert epoch_res["epoch"] == 1
    assert epoch_res["transactions_simulated"] == 300
    assert epoch_res["fraud_attempts"] > 0
    assert "defense_metrics" in epoch_res
    assert "precision" in epoch_res["defense_metrics"]
    assert "recall" in epoch_res["defense_metrics"]
    assert orchestrator.replay_buffer.size() >= 300
