"""ATK-009: Ghost Merchant & MCC Shifting Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class GhostMerchantInjector(AttackInjector):
    attack_id = "ATK-009"
    attack_name = "Ghost Merchant & MCC Shifting"
    category = "merchant_collusion"
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

        ghost_merchants = [f"MERCH-GHOST-{uuid.uuid4().hex[:5].upper()}" for _ in range(3)]
        # Low risk everyday MCCs used to mask high-ticket money laundering
        rotated_mccs = [
            ("5411", "Grocery Stores, Supermarkets"),
            ("5812", "Eating Places, Restaurants"),
            ("5942", "Book Stores"),
        ]

        records = []
        for i in range(n_attacks):
            sender = (
                str(baseline_df["sender_account"].sample(1).iloc[0])
                if not baseline_df.empty
                else f"ACC-{random.randint(1000, 9999):06d}"
            )
            ghost_merch = random.choice(ghost_merchants)
            chosen_mcc, mcc_desc = random.choice(rotated_mccs)
            # High ticket amount for grocery/restaurant ($450 - $2,800)
            amt = round(random.uniform(450.0, 2800.0), 2)

            records.append({
                "txn_id": f"TXN-GHOST-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": base_time + timedelta(hours=random.uniform(0.5, 36.0)),
                "sender_account": sender,
                "receiver_account": ghost_merch,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CHASUS33XXX",
                "amount": amt,
                "currency": "USD",
                "channel": "POS",
                "mcc": chosen_mcc,
                "mcc_description": mcc_desc,
                "device_id": f"DEV-POS-{uuid.uuid4().hex[:8].upper()}",
                "ip_address": f"24.105.{random.randint(10, 200)}.{random.randint(10, 200)}",
                "ip_country": "US",
                "user_agent": "Verifone-POS-Terminal/5.2",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(10.0, 25.0), 2),
                "biometric_friction_score": round(random.uniform(0.01, 0.04), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": f"POS retail settlement terminal #{ghost_merch[-4:]}",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Dynamic MCC hopping across essential retail categories to disguise high-ticket extraction",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
