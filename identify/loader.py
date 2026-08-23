"""Threat Registry Loader & Query Interface.

Provides functions to load, validate, index, and query the YAML attack card
repository for the Mastercard AI Defense Lab.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
import pandas as pd

from identify.taxonomy import AttackCard, AttackCategory, PaymentChannel, SeverityLevel


class AttackRegistry:
    """In-memory registry and query engine for GenAI payment fraud vectors."""

    def __init__(self, registry_dir: Optional[Union[str, Path]] = None) -> None:
        if registry_dir is None:
            # Default to identify/registry relative to this file
            self.registry_dir = Path(__file__).parent / "registry"
        else:
            self.registry_dir = Path(registry_dir)

        self._cards: Dict[str, AttackCard] = {}
        self.reload()

    def reload(self) -> int:
        """Scan registry directory and load all YAML attack cards."""
        self._cards.clear()
        if not self.registry_dir.exists():
            return 0

        yaml_files = sorted(list(self.registry_dir.glob("*.yaml")) + list(self.registry_dir.glob("*.yml")))
        for file_path in yaml_files:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
                if raw_data:
                    card = AttackCard(**raw_data)
                    self._cards[card.id] = card

        return len(self._cards)

    def get(self, attack_id: str) -> Optional[AttackCard]:
        """Retrieve attack card by ID (e.g. 'ATK-001')."""
        return self._cards.get(attack_id.upper())

    def list_all(self) -> List[AttackCard]:
        """List all loaded attack cards sorted by ID."""
        return sorted(self._cards.values(), key=lambda c: c.id)

    def filter_by_category(self, category: Union[str, AttackCategory]) -> List[AttackCard]:
        """Filter cards by threat category."""
        target = category.value if isinstance(category, AttackCategory) else category
        return [c for c in self._cards.values() if c.category == target]

    def filter_by_channel(self, channel: Union[str, PaymentChannel]) -> List[AttackCard]:
        """Filter cards by payment channel."""
        target = channel.value if isinstance(channel, PaymentChannel) else channel
        return [c for c in self._cards.values() if c.channel == target]

    def filter_by_severity(self, severity: Union[str, SeverityLevel]) -> List[AttackCard]:
        """Filter cards by severity level."""
        target = severity.value if isinstance(severity, SeverityLevel) else severity
        return [c for c in self._cards.values() if c.severity == target]

    def summary_dataframe(self) -> pd.DataFrame:
        """Export high-level metadata of all registered attacks as a DataFrame."""
        records = []
        for card in self.list_all():
            records.append({
                "ID": card.id,
                "Name": card.name,
                "Category": card.category,
                "Channel": card.channel,
                "Severity": card.severity,
                "GenAI Role": card.genai_role,
                "ISO Message": card.iso_mapping.message_type,
                "Signals Count": len(card.detection_signals),
                "KillChain Steps": len(card.kill_chain),
            })
        return pd.DataFrame(records)

    def to_dict_list(self) -> List[Dict]:
        """Export all cards as serialized dicts for JSON/REST APIs."""
        return [card.model_dump() for card in self.list_all()]

    def count(self) -> int:
        """Total number of registered attack vectors."""
        return len(self._cards)


# Global default instance
_default_registry: Optional[AttackRegistry] = None


def get_default_registry() -> AttackRegistry:
    """Return singleton instance of AttackRegistry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = AttackRegistry()
    return _default_registry
