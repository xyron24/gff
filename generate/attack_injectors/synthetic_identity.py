"""ATK-003: Synthetic Identity Bust-Out Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class SyntheticIdentityInjector(AttackInjector):
    attack_id = "ATK-003"
    attack_name = "Synthetic Identity Bust-Out"
    category = "identity_synthesis"
    channel = "ONLINE"

    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        bustout_limit_min = float(p.get("limit_min", 25000.0))
        bustout_limit_max = float(p.get("limit_max", 75000.0))

        base_time = (
            pd.to_datetime(baseline_df["timestamp"].max()).to_pydatetime()
            if not baseline_df.empty
            else datetime.now(timezone.utc)
        )

        # Generate synthetic account cluster with shared device/IP latent links
        num_identities = max(2, int(n_attacks / 3))
        synthetic_accounts = [f"ACC-SYNTH-{uuid.uuid4().hex[:6].upper()}" for _ in range(num_identities)]
        shared_device = f"DEV-SYNTH-{uuid.uuid4().hex[:8].upper()}"
        shared_ip = f"172.56.{random.randint(10, 200)}.{random.randint(10, 200)}"

        records = []
        for i in range(n_attacks):
            sender = random.choice(synthetic_accounts)
            dest = f"MERCH-LUXURY-{uuid.uuid4().hex[:4].upper()}"
            amt = round(random.uniform(bustout_limit_min, bustout_limit_max), 2)
            # Bust-out occurs in synchronized narrow burst window
            txn_time = base_time + timedelta(minutes=random.uniform(5.0, 180.0))

            records.append({
                "txn_id": f"TXN-SYNTH-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": txn_time,
                "sender_account": sender,
                "receiver_account": dest,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CITIUS33XXX",
                "amount": amt,
                "currency": "USD",
                "channel": "ONLINE",
                "mcc": random.choice(["5732", "5094", "7995"]),  # Electronics, Jewelry, Crypto/Gaming
                "mcc_description": "Electronic Sales / High Liquidity",
                "device_id": shared_device,
                "ip_address": shared_ip,
                "ip_country": "US",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(35.0, 90.0), 2),
                "biometric_friction_score": round(random.uniform(0.02, 0.09), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": "High-limit credit line retail purchase",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Aged credit score nurturing prior to zero-hour synchronized credit drawdown",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
