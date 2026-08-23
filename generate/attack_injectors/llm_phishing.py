"""ATK-007: LLM-Powered Spear Phishing & BEC Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class LLMPhishingInjector(AttackInjector):
    attack_id = "ATK-007"
    attack_name = "LLM-Powered Spear Phishing & BEC"
    category = "social_engineering_bec"
    channel = "WIRE"

    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        min_amt = float(p.get("min_amount", 120000.0))
        max_amt = float(p.get("max_amount", 1850000.0))

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
                else f"ACC-CORP-{random.randint(100, 999):04d}"
            )
            spoofed_vendor_account = f"ACC-BEC-{uuid.uuid4().hex[:6].upper()}"
            amt = round(random.uniform(min_amt, max_amt), 2)

            records.append({
                "txn_id": f"TXN-BEC-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": base_time + timedelta(hours=random.uniform(2.0, 72.0)),
                "sender_account": sender,
                "receiver_account": spoofed_vendor_account,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": random.choice(["CHASUS33XXX", "CITIUS33XXX", "BARCGB22XXX"]),
                "amount": amt,
                "currency": "USD",
                "channel": "WIRE",
                "mcc": "4829",
                "mcc_description": "Money Orders / Wire Transfer",
                "device_id": f"DEV-CORP-{uuid.uuid4().hex[:8].upper()}",
                "ip_address": f"12.180.{random.randint(10, 240)}.{random.randint(10, 240)}",
                "ip_country": "US",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CorporatePortal/2.1",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(120.0, 300.0), 2),
                "biometric_friction_score": round(random.uniform(0.01, 0.04), 4),  # authorized by real AP clerk!
                "iso_message_type": "pain.001.001.09",
                "remittance_info": f"Updated settlement beneficiary for master services agreement MSA-2026-{random.randint(100,999)}",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Context-grounded LLM invoice mimicry fooling AP clerk into authentic authorization",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
