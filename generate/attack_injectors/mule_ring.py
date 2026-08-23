"""ATK-006: Dynamic Mule Cycle Rings Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class MuleRingInjector(AttackInjector):
    attack_id = "ATK-006"
    attack_name = "Dynamic Mule Cycle Rings"
    category = "graph_mule_orchestration"
    channel = "P2P"

    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        hop_count = int(p.get("hop_count", 4))
        dwell_seconds = float(p.get("dwell_seconds", 90.0))

        base_time = (
            pd.to_datetime(baseline_df["timestamp"].max()).to_pydatetime()
            if not baseline_df.empty
            else datetime.now(timezone.utc)
        )

        # Create cycle ring accounts: A -> B -> C -> D -> A or E
        num_mules = max(4, hop_count)
        mule_ring = [f"ACC-RING-{uuid.uuid4().hex[:6].upper()}" for _ in range(num_mules)]
        shared_asn_ip = f"185.220.{random.randint(100, 250)}"

        records = []
        current_amount = float(p.get("initial_amount", 50000.0))
        current_time = base_time

        for i in range(n_attacks):
            sender_idx = i % num_mules
            receiver_idx = (i + 1) % num_mules
            sender = mule_ring[sender_idx]
            receiver = mule_ring[receiver_idx]

            # Rapid flow through ring: funds dwell only 60-120 seconds per hop
            current_time += timedelta(seconds=random.uniform(dwell_seconds * 0.7, dwell_seconds * 1.3))
            # Minor commission haircut per hop (0.5% - 2%)
            current_amount *= random.uniform(0.98, 0.995)

            records.append({
                "txn_id": f"TXN-MULE-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": current_time,
                "sender_account": sender,
                "receiver_account": receiver,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CHASUS33XXX",
                "amount": round(current_amount, 2),
                "currency": "USD",
                "channel": "P2P",
                "mcc": "4829",
                "mcc_description": "Money Orders / Wire Transfer",
                "device_id": f"DEV-MULE-{sender_idx:02d}",
                "ip_address": f"{shared_asn_ip}.{random.randint(10, 250)}",
                "ip_country": "US",
                "user_agent": "P2P-MobileApp/4.12 (Android 14)",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(15.0, 45.0), 2),
                "biometric_friction_score": round(random.uniform(0.04, 0.12), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": f"Instant P2P transfer hop {i+1}",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Dynamic cycle topology rewiring and low dwell-time transit hops",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
