"""Abstract Base Class for Attack Injectors.

Defines the contract for transforming baseline legitimate transactions into high-fidelity
adversarial fraud attacks aligned with the Threat Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd


class AttackInjector(ABC):
    """Abstract base class for all pluggable GenAI attack injection modules."""

    attack_id: str
    attack_name: str
    category: str
    channel: str

    def __init__(self, default_params: Optional[Dict[str, Any]] = None) -> None:
        self.default_params = default_params or {}

    @abstractmethod
    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """Transform or generate n_attacks fraud transactions based on this attack vector.

        Args:
            baseline_df: Pool of legitimate transactions to sample entities or derive context.
            n_attacks: Number of attack transaction rows to generate.
            params: Optional override hyperparameters.

        Returns:
            DataFrame of generated attack transactions with is_fraud=1 and attack_type=self.attack_id.
        """
        pass
