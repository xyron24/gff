"""Closed-Loop Co-Evolution Orchestrator.

Drives the autonomous Red-Team vs. Blue-Team loop:
Generate Attacks (RL Policy) -> Defend (Cascading Grid) -> Mine False Negatives -> Experience Replay Retrain -> Update Policy.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from generate.pipeline import SimulationPipeline
from generate.rl_red_agent import RedTeamRLAgent
from defend.ensemble import DetectionGrid
from defend.features.tabular_features import TabularFeatureExtractor
from defend.features.graph_features import GraphFeatureExtractor
from defend.metrics import compute_defense_metrics
from closed_loop.false_negative_miner import FalseNegativeMiner
from closed_loop.replay_buffer import ExperienceReplayBuffer


class ClosedLoopOrchestrator:
    """Coordinates multi-epoch adversarial co-evolution between Red Team and Blue Team."""

    def __init__(
        self,
        pipeline: Optional[SimulationPipeline] = None,
        red_agent: Optional[RedTeamRLAgent] = None,
        detection_grid: Optional[DetectionGrid] = None,
        fn_miner: Optional[FalseNegativeMiner] = None,
        replay_buffer: Optional[ExperienceReplayBuffer] = None,
    ) -> None:
        self.pipeline = pipeline or SimulationPipeline(random_seed=42)
        self.red_agent = red_agent or RedTeamRLAgent()
        self.detection_grid = detection_grid or DetectionGrid()
        self.fn_miner = fn_miner or FalseNegativeMiner(block_threshold=0.50)
        self.replay_buffer = replay_buffer or ExperienceReplayBuffer(max_capacity=30000)

        self.epoch_history: List[Dict[str, Any]] = []

    def run_epoch(
        self,
        n_transactions: int = 800,
        fraud_ratio: float = 0.15,
        retrain_defense: bool = True,
    ) -> Dict[str, Any]:
        """Execute one complete co-evolutionary cycle.

        Returns:
            Comprehensive telemetry dictionary of epoch performance and evolution metrics.
        """
        epoch_idx = len(self.epoch_history) + 1
        t_epoch_start = time.perf_counter()

        # Step 1: Red-Team Policy Attack Distribution
        attack_weights = self.red_agent.get_attack_distribution()

        # Step 2: Generate Mixed Dataset
        df_batch, gen_summary = self.pipeline.generate_dataset(
            n_total=n_transactions,
            fraud_ratio=fraud_ratio,
            attack_weights=attack_weights,
        )

        # Step 3: Blue-Team Cascading Defense Scoring
        scores = []
        latencies = []
        for _, row in df_batch.iterrows():
            res = self.detection_grid.score_transaction(row.to_dict())
            scores.append(res["risk_score"])
            latencies.append(res["total_latency_ms"])

        scores_arr = np.array(scores, dtype=np.float32)

        # Step 4: Defense Metrics Evaluation (Pre-retrain performance)
        metrics = compute_defense_metrics(
            y_true=df_batch["is_fraud"].values,
            y_scores=scores_arr,
            threshold=self.detection_grid.block_threshold,
            latencies_ms=latencies,
            attack_types=df_batch["attack_type"].tolist(),
        )

        # Step 5: Mine False Negatives (Defense Blind Spots)
        fn_df, diagnostics = self.fn_miner.mine_false_negatives(df_batch, scores_arr)

        # Step 6: Ingest into Experience Replay Buffer
        self.replay_buffer.add_transactions(df_batch)

        # Step 7: Red-Team RL Policy Update (Reward on successful evasions)
        red_update = self.red_agent.update_policy(diagnostics)

        # Step 8: Retrain Blue-Team Defense on Hardened Experience Replay Sample
        retrain_info = {}
        if retrain_defense and self.replay_buffer.size() >= 400:
            hardened_df = self.replay_buffer.sample_hardened_dataset(n_samples=1200, target_fraud_ratio=0.25)
            if not hardened_df.empty and len(hardened_df["is_fraud"].unique()) > 1:
                tab_ext = self.detection_grid.tier1.feature_extractor
                X_tab, _ = tab_ext.extract_dataframe(hardened_df)
                y_train = hardened_df["is_fraud"].values

                # Retrain Tier 1 GBDT
                retrain_info = self.detection_grid.tier1.train(X_tab, y_train, num_trees=100)

                # Retrain Tier 2 GNN
                graph_ext = self.detection_grid.tier2.graph_extractor
                graph_ext.update_graph_from_df(hardened_df)
                X_graph = graph_ext.extract_batch(hardened_df)
                self.detection_grid.tier2.train(X_tab, X_graph, y_train)

        total_epoch_duration = round((time.perf_counter() - t_epoch_start), 3)

        epoch_record = {
            "epoch": epoch_idx,
            "duration_seconds": total_epoch_duration,
            "transactions_simulated": len(df_batch),
            "fraud_attempts": int(gen_summary["fraud_count"]),
            "false_negatives_mined": len(fn_df),
            "evasion_rate": diagnostics["overall_evasion_rate"],
            "defense_metrics": metrics,
            "most_evasive_attacks": diagnostics["most_evasive_vectors"],
            "replay_buffer_size": self.replay_buffer.size(),
            "retrained": bool(retrain_info),
        }

        self.epoch_history.append(epoch_record)
        return epoch_record

    def run_multi_epoch_simulation(self, epochs: int = 5) -> List[Dict[str, Any]]:
        """Run continuous multi-epoch training and log evolution trajectories."""
        results = []
        for i in range(epochs):
            res = self.run_epoch(retrain_defense=True)
            results.append(res)
        return results
