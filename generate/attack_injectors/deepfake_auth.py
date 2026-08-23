"""ATK-002: Deepfake Voice Authorization Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class DeepfakeAuthInjector(AttackInjector):
    attack_id = "ATK-002"
    attack_name = "Deepfake Voice Authorization"
    category = "voice_biometric_spoofing"
    channel = "WIRE"

    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        min_amount = float(p.get("min_amount", 250000.0))
        max_amount = float(p.get("max_amount", 4500000.0))

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
            dest = f"ACC-OFFSHORE-{uuid.uuid4().hex[:6].upper()}"
            amt = round(random.uniform(min_amount, max_amount), 2)
            txn_time = base_time + timedelta(hours=random.uniform(1.0, 48.0))

            records.append({
                "txn_id": f"TXN-VOICE-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": txn_time,
                "sender_account": sender,
                "receiver_account": dest,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": random.choice(["HSBCHKHHXXX", "SCBLSG22XXX", "UBSWCHZHXXX"]),
                "amount": amt,
                "currency": random.choice(["USD", "EUR", "GBP"]),
                "channel": "WIRE",
                "mcc": "4829",
                "mcc_description": "Money Orders / Wire Transfer",
                "device_id": f"DEV-IVR-{uuid.uuid4().hex[:8].upper()}",
                "ip_address": f"104.28.{random.randint(10, 240)}.{random.randint(10, 240)}",
                "ip_country": "US",
                "user_agent": "Telephony-IVR-Gateway/2.4 (VoiceCallback)",
                "is_foreign_transaction": True,
                "session_duration_sec": round(random.uniform(180.0, 420.0), 2),  # long phone call
                "biometric_friction_score": round(random.uniform(0.01, 0.08), 4),  # cloned voice fools IVR!
                "iso_message_type": "pain.001.001.09",
                "remittance_info": f"Urgent acquisition escrow wire authorization ref {uuid.uuid4().hex[:8].upper()}",
                "purpose_code": "INTE",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Zero-shot voice acoustic cloning with low spectral phase dissonance",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
