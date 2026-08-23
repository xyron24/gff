"""ATK-012: Real-Time ATO via Session Hijack Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class SessionHijackInjector(AttackInjector):
    attack_id = "ATK-012"
    attack_name = "Real-Time ATO via Session Hijack"
    category = "account_takeover"
    channel = "API"

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
            victim_account = (
                str(baseline_df["sender_account"].sample(1).iloc[0])
                if not baseline_df.empty
                else f"ACC-{random.randint(1000, 9999):06d}"
            )
            dest = f"ACC-MULE-ATO-{uuid.uuid4().hex[:6].upper()}"

            # High value balance drain within <5 seconds of session hijacking
            records.append({
                "txn_id": f"TXN-ATO-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": base_time + timedelta(seconds=random.uniform(3.0, 15.0) * (i + 1)),
                "sender_account": victim_account,
                "receiver_account": dest,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CHASUS33XXX",
                "amount": round(random.uniform(4800.0, 24500.0), 2),
                "currency": "USD",
                "channel": "API",
                "mcc": "4829",
                "mcc_description": "Money Orders / Wire Transfer",
                "device_id": f"DEV-AITM-PROXY-{uuid.uuid4().hex[:6].upper()}",  # Attacker device fingerprint
                "ip_address": f"195.123.{random.randint(10, 200)}.{random.randint(10, 200)}",  # VPN / Proxy IP
                "ip_country": "US",
                "user_agent": "OpenBanking-PISP-Agent/2.0 (AutomatedClient)",
                "is_foreign_transaction": False,
                "session_duration_sec": round(random.uniform(2.5, 6.0), 2),  # Sub-second automated API execution!
                "biometric_friction_score": round(random.uniform(0.01, 0.03), 4),
                "iso_message_type": "pain.001.001.09",
                "remittance_info": f"Instant Open Banking transfer ref {uuid.uuid4().hex[:6]}",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": "Reverse-proxy AiTM OAuth token capture and sub-5s automated PISP API drainage",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
