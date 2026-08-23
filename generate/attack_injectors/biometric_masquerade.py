"""ATK-005: Behavioral Biometric Masquerade Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class BiometricMasqueradeInjector(AttackInjector):
    attack_id = "ATK-005"
    attack_name = "Behavioral Biometric Masquerade"
    category = "behavioral_mimicry"
    channel = "ONLINE"

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

        records = []
        for i in range(n_attacks):
            sender = (
                str(baseline_df["sender_account"].sample(1).iloc[0])
                if not baseline_df.empty
                else f"ACC-{random.randint(1000, 9999):06d}"
            )
            dest = f"MERCH-ONLINE-{uuid.uuid4().hex[:5].upper()}"

            records.append({
                "txn_id": f"TXN-BIO-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": base_time + timedelta(hours=random.uniform(0.2, 24.0)),
                "sender_account": sender,
                "receiver_account": dest,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CITIUS33XXX",
                "amount": round(random.uniform(350.0, 3200.0), 2),
                "currency": "USD",
                "channel": "ONLINE",
                "mcc": "5732",
                "mcc_description": "Electronic Sales",
                "device_id": f"DEV-BOTGAN-{uuid.uuid4().hex[:8].upper()}",
                "ip_address": f"64.233.{random.randint(10, 200)}.{random.randint(10, 200)}",
                "ip_country": "US",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4) AppleWebKit/605.1.15",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(30.0, 75.0), 2),
                # Synthesized TimeGAN touch dynamics make friction score appear legitimately human (<0.06)
                "biometric_friction_score": round(random.uniform(0.015, 0.055), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": "E-Commerce Card Purchase",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "TimeGAN touch dynamics and physiological tremor emulation",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
