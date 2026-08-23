"""ATK-004: ISO 20022 Metadata Tampering Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


# Homoglyph lookalike mappings (Latin -> Cyrillic/Greek lookalikes)
HOMOGLYPH_MAP = {
    "a": "\u0430",  # Cyrillic small letter a
    "e": "\u0435",  # Cyrillic small letter ie
    "o": "\u043e",  # Cyrillic small letter o
    "p": "\u0440",  # Cyrillic small letter er
    "c": "\u0441",  # Cyrillic small letter es
    "y": "\u0443",  # Cyrillic small letter u
    "x": "\u0445",  # Cyrillic small letter ha
    "i": "\u0456",  # Cyrillic small letter byelorussian-ukrainian i
}


def _inject_homoglyphs(text: str, rate: float = 0.25) -> str:
    """Subtly replace Latin characters with identical-looking Cyrillic glyphs."""
    chars = []
    for ch in text:
        if ch.lower() in HOMOGLYPH_MAP and random.random() < rate:
            chars.append(HOMOGLYPH_MAP[ch.lower()])
        else:
            chars.append(ch)
    # 50% chance of injecting a zero-width space
    if random.random() < 0.5:
        idx = random.randint(0, len(chars))
        chars.insert(idx, "\u200B")
    return "".join(chars)


class MetadataTamperInjector(AttackInjector):
    attack_id = "ATK-004"
    attack_name = "ISO 20022 Metadata Tampering"
    category = "metadata_tampering"
    channel = "WIRE"

    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        base_time = (
            pd.to_datetime(baseline_df["timestamp"].max()).to_pydatetime()
            if not baseline_df.empty
            else datetime.now(timezone.utc)
        )

        sanctioned_entity_templates = [
            "Petro Chemical Export Syndicate",
            "Global Maritime Logistics Limited",
            "Aerospace Components Trade Corp",
            "Defense Material Technologies",
        ]

        records = []
        for i in range(n_attacks):
            sender = (
                str(baseline_df["sender_account"].sample(1).iloc[0])
                if not baseline_df.empty
                else f"ACC-{random.randint(1000, 9999):06d}"
            )
            raw_entity = random.choice(sanctioned_entity_templates)
            tampered_remittance = _inject_homoglyphs(f"Payment for {raw_entity} invoice #9921")

            records.append({
                "txn_id": f"TXN-ISO-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": base_time + timedelta(hours=random.uniform(0.5, 36.0)),
                "sender_account": sender,
                "receiver_account": f"ACC-SANCT-{uuid.uuid4().hex[:6].upper()}",
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CHASUS33XXX",
                "amount": round(random.uniform(85000.0, 950000.0), 2),
                "currency": "EUR",
                "channel": "WIRE",
                "mcc": "4829",
                "mcc_description": "Money Orders / Wire Transfer",
                "device_id": f"DEV-SWIFT-{uuid.uuid4().hex[:8].upper()}",
                "ip_address": f"194.187.{random.randint(10, 200)}.{random.randint(10, 200)}",
                "ip_country": "DE",
                "user_agent": "SWIFT-Alliance-Gateway/7.6",
                "is_foreign_transaction": True,
                "session_duration_sec": round(random.uniform(60.0, 180.0), 2),
                "biometric_friction_score": round(random.uniform(0.01, 0.05), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": tampered_remittance,
                "purpose_code": "GDDS",  # spoofed innocent purpose code
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Homoglyphic Unicode character injection and zero-width spaces in RmtInf",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
