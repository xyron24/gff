"""ATK-008: Adversarial Feature Perturbation Attack Injector."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd

from generate.attack_injectors.base import AttackInjector


class FeaturePerturbationInjector(AttackInjector):
    attack_id = "ATK-008"
    attack_name = "Adversarial Feature Perturbation"
    category = "adversarial_perturbation"
    channel = "ONLINE"

    def inject(
        self,
        baseline_df: pd.DataFrame,
        n_attacks: int,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        epsilon = float(p.get("epsilon", 0.08))

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
            dest = f"MERCH-FRAUD-{uuid.uuid4().hex[:5].upper()}"

            # Attacker applies PGD delta offset to continuous features:
            # Shift amount just below high-risk decision tree threshold (e.g. $499.50 vs $500.00)
            base_amt = random.choice([49.50, 99.00, 199.50, 495.00, 985.00])
            perturbed_amount = round(base_amt * (1.0 - epsilon * random.uniform(0.5, 1.0)), 2)

            records.append({
                "txn_id": f"TXN-ADV-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": base_time + timedelta(hours=random.uniform(0.1, 12.0)),
                "sender_account": sender,
                "receiver_account": dest,
                "sender_bank_bic": "MSTRUS33XXX",
                "receiver_bank_bic": "CITIUS33XXX",
                "amount": perturbed_amount,
                "currency": "USD",
                "channel": "ONLINE",
                "mcc": "5311",  # Department store (low risk MCC)
                "mcc_description": "Department Stores",
                "device_id": f"DEV-ADV-{uuid.uuid4().hex[:8].upper()}",
                "ip_address": f"173.252.{random.randint(10, 200)}.{random.randint(10, 200)}",
                "ip_country": "US",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "is_foreign_transaction": False,
                # PGD perturbed session duration to sit at median of legitimate distribution
                "session_duration_sec": round(45.0 + random.gauss(0, 5.0), 2),
                "biometric_friction_score": round(0.035 + random.gauss(0, 0.005), 4),
                "iso_message_type": "pacs.008.001.08",
                "remittance_info": "Department store retail purchase",
                "purpose_code": "GDDS",
                "is_fraud": 1,
                "attack_type": self.attack_id,
                "evasion_strategy": f"Projected Gradient Descent (PGD) continuous feature shifting (eps={epsilon})",
            })

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
