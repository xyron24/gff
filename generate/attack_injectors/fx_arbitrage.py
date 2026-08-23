"""ATK-010: Cross-Border FX Arbitrage Layering Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class FXArbitrageInjector(AttackInjector):
    attack_id = "ATK-010"
    attack_name = "Cross-Border FX Arbitrage Layering"
    category = "cross_border_layering"
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

        currency_chain = ["USD", "EUR", "GBP", "SGD", "AED"]
        bics = ["MSTRUS33XXX", "DBEKDEFFXXX", "BARCGB22XXX", "DBSSSGSGXXX", "EBILAEADXXX"]
        countries = ["US", "DE", "GB", "SG", "AE"]

        records = []
        current_time = base_time
        base_amount = float(p.get("initial_amount", 125000.0))

        for i in range(n_attacks):
            idx = i % len(currency_chain)
            next_idx = (i + 1) % len(currency_chain)

            # Rapid hops: 2-5 minutes between cross-border hops
            current_time += timedelta(minutes=random.uniform(2.0, 5.0))
            curr = currency_chain[idx]
            sender_bic = bics[idx]
            recv_bic = bics[next_idx]

            records.append({
                "txn_id": f"TXN-FX-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": current_time,
                "sender_account": f"ACC-FX-{curr}-{uuid.uuid4().hex[:4].upper()}",
                "receiver_account": f"ACC-FX-{currency_chain[next_idx]}-{uuid.uuid4().hex[:4].upper()}",
                "sender_bank_bic": sender_bic,
                "receiver_bank_bic": recv_bic,
                "amount": round(base_amount * random.uniform(0.98, 1.02), 2),
                "currency": curr,
                "channel": "WIRE",
                "mcc": "4829",
                "mcc_description": "Money Orders / Wire Transfer",
                "device_id": f"DEV-FX-API-{uuid.uuid4().hex[:6].upper()}",
                "ip_address": f"185.190.{random.randint(10, 200)}.{random.randint(10, 200)}",
                "ip_country": countries[idx],
                "user_agent": "CrossBorder-RemitAPI/3.0",
                "is_foreign_transaction": True,
                "session_duration_sec": round(random.uniform(40.0, 90.0), 2),
                "biometric_friction_score": round(random.uniform(0.02, 0.06), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": f"Cross-currency liquidity conversion hop {i+1} ({curr}->{currency_chain[next_idx]})",
                "purpose_code": "INTE",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Multi-jurisdiction rapid FX hops exploiting asynchronous clearing windows",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
