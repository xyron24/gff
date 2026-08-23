"""ATK-011: Token Replay on Mobile Wallets Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class TokenReplayInjector(AttackInjector):
    attack_id = "ATK-011"
    attack_name = "Token Replay on Mobile Wallets"
    category = "token_exploitation"
    channel = "POS"

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

        stolen_dpan = f"DPAN-TOKEN-{uuid.uuid4().hex[:8].upper()}"
        cloned_device = f"DEV-NFC-RELAY-{uuid.uuid4().hex[:6].upper()}"

        records = []
        for i in range(n_attacks):
            transit_merchant = f"MERCH-TRANSIT-{random.randint(100, 999)}"
            # High concurrency token replays across distant terminals within minutes
            txn_time = base_time + timedelta(minutes=random.uniform(1.0, 30.0))

            records.append({
                "txn_id": f"TXN-TOKEN-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": txn_time,
                "sender_account": stolen_dpan,
                "receiver_account": transit_merchant,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CHASUS33XXX",
                "amount": round(random.uniform(15.0, 95.0), 2),  # sub-limit contactless payments
                "currency": "USD",
                "channel": "POS",
                "mcc": "4111",  # Local and Suburban Commuter Passenger Transportation
                "mcc_description": "Local/Suburban Commuter Passenger Transportation",
                "device_id": cloned_device,
                "ip_address": f"107.150.{random.randint(10, 200)}.{random.randint(10, 200)}",
                "ip_country": "US",
                "user_agent": "ApplePay-NFC-Core/17.4 (RelayedSession)",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(1.0, 3.5), 2),  # instant NFC tap
                "biometric_friction_score": round(random.uniform(0.01, 0.03), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": "Contactless Tap-to-Pay Fare",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "NFC token replay targeting relaxed offline unattended transit gates",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
