"""Reinforcement Learning Red-Team Evasion Policy Agent.

Autonomous Red-Team policy optimizer that dynamically shifts attack vector selection
and continuous parameter tuning towards the Blue Team's weakest defense corridors.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from generate.attack_injectors import INJECTOR_REGISTRY


class RedTeamRLAgent:
    """Adaptive Red-Team policy agent seeking maximal defense evasion."""

    def __init__(
        self,
        learning_rate: float = 0.15,
        exploration_rate: float = 0.20,
        temperature: float = 1.0,
    ) -> None:
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        self.temperature = temperature

        # Policy Q-values for each attack vector
        self.attack_ids = sorted(list(INJECTOR_REGISTRY.keys()))
        self.q_values: Dict[str, float] = {atk: 1.0 for atk in self.attack_ids}
        self.selection_counts: Dict[str, int] = {atk: 0 for atk in self.attack_ids}
        self.evasion_history: List[Dict[str, Any]] = []

    def get_attack_distribution(self) -> Dict[str, float]:
        """Compute Boltzmann softmax distribution over attack vectors based on current Q-values."""
        q_arr = np.array([self.q_values[a] for a in self.attack_ids])
        # Softmax with temperature
        exp_q = np.exp(q_arr / max(0.1, self.temperature))
        probs = exp_q / np.sum(exp_q)

        # Mix with epsilon uniform exploration
        uniform = np.ones(len(self.attack_ids)) / len(self.attack_ids)
        final_probs = (1.0 - self.exploration_rate) * probs + self.exploration_rate * uniform

        return {atk: float(p) for atk, p in zip(self.attack_ids, final_probs)}

    def select_attack_batch(self, n_attacks: int = 50) -> List[str]:
        """Sample attack vector batch based on adaptive policy."""
        dist = self.get_attack_distribution()
        atks = list(dist.keys())
        weights = list(dist.values())
        return random.choices(atks, weights=weights, k=n_attacks)

    def update_policy(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Update Red-Team Q-values using evasion diagnostic feedback from defense grid.

        Reward formulation:
        - High evasion rate (> 0.70) -> High positive reward (+2.0)
        - Moderate evasion (0.30 - 0.70) -> Moderate reward (+0.5)
        - Caught by defense (< 0.30) -> Negative reward (-1.0)
        """
        per_vector = diagnostics.get("per_vector_evasion", {})
        updates = {}

        for atk in self.attack_ids:
            if atk in per_vector:
                evasion_rate = per_vector[atk].get("evasion_rate", 0.0)
                reward = (evasion_rate - 0.40) * 3.0  # centered reward

                # Q-learning policy update step
                current_q = self.q_values[atk]
                new_q = current_q + self.learning_rate * (reward - current_q)
                self.q_values[atk] = float(np.clip(new_q, 0.1, 10.0))
                self.selection_counts[atk] += per_vector[atk].get("total_attempts", 0)

                updates[atk] = {
                    "old_q": round(current_q, 3),
                    "new_q": round(new_q, 3),
                    "reward": round(reward, 3),
                    "evasion_rate": round(evasion_rate, 3),
                }

        # Log policy evolution step
        self.evasion_history.append({
            "overall_evasion_rate": diagnostics.get("overall_evasion_rate", 0.0),
            "defense_catch_rate": diagnostics.get("defense_catch_rate", 0.0),
            "top_evasive_vector": max(self.q_values, key=self.q_values.get),
        })

        return {
            "policy_updates": updates,
            "current_attack_distribution": self.get_attack_distribution(),
            "epochs_trained": len(self.evasion_history),
        }
