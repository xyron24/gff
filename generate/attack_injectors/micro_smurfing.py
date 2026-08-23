"""ATK-001: Agentic Micro-Smurfing Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class MicroSmurfingInjector(AttackInjector):
    attack_id = "ATK-001"
    attack_name = "Agentic Micro-Smurfing"
    category = "structuring"
    channel = "ONLINE"

    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        threshold = float(p.get("threshold", 199.99))
        min_amount = float(p.get("min_amount", 12.50))
        time_spread_hours = float(p.get("time_spread_hours", 24.0))

        # Sample originating account from baseline
        originator = (
            str(baseline_df["sender_account"].sample(1).iloc[0])
            if not baseline_df.empty
            else f"ACC-{random.randint(1000, 9999):06d}"
        )
        base_time = (
            pd.to_datetime(baseline_df["timestamp"].max()).to_pydatetime()
            if not baseline_df.empty
            else datetime.now(timezone.utc)
        )

        # Generate synthetic destination mule wallets (fan-out ratio)
        num_mules = max(5, int(n_attacks / 4))
        mule_wallets = [f"ACC-MULE-{uuid.uuid4().hex[:6].upper()}" for _ in range(num_mules)]
        originator_device = f"DEV-{uuid.uuid4().hex[:12].upper()}"
        originator_ip = f"198.51.100.{random.randint(10, 250)}"

        records = []
        for i in range(n_attacks):
            dest = random.choice(mule_wallets)
            # Dirichlet-like distribution clustering near reporting bounds
            amt = round(random.uniform(min_amount, threshold), 2)
            # Add temporal jitter (Poisson process)
            jitter_sec = random.expovariate(1.0 / (time_spread_hours * 3600.0 / max(1, n_attacks)))
            txn_time = base_time + timedelta(seconds=min(jitter_sec * (i + 1), time_spread_hours * 3600.0))

            records.append({
                "txn_id": f"TXN-SMURF-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": txn_time,
                "sender_account": originator,
                "receiver_account": dest,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CHASUS33XXX",
                "amount": amt,
                "currency": "USD",
                "channel": "ONLINE",
                "mcc": random.choice(["4829", "5411", "5814", "5311"]),
                "mcc_description": "Money Orders / Wire Transfer",
                "device_id": originator_device,
                "ip_address": originator_ip,
                "ip_country": "US",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(12.0, 40.0), 2),
                "biometric_friction_score": round(random.uniform(0.08, 0.25), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": f"P2P split settlement ref {uuid.uuid4().hex[:6]}",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Sub-threshold Dirichlet amount jitter with high-density fan-out",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
