"""Baseline Legitimate Payment Transaction Synthesizer.

Implements high-fidelity multivariate distribution sampling for legitimate financial
transactions reflecting empirical payment properties (diurnal seasonality, Benford's law,
log-normal transaction amounts, realistic MCC distributions, and device affinities).
"""

from __future__ import annotations

import math
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from data.schema import CurrencyCode, PaymentTransaction, TransactionChannel


# Empirical Merchant Category Codes with frequency weights & default descriptions
MCC_PROFILES: List[Tuple[str, str, float, float, float]] = [
    # (mcc, description, relative_weight, mu_log_amount, sigma_log_amount)
    ("5411", "Grocery Stores, Supermarkets", 0.30, 3.8, 0.7),       # ~$45 avg
    ("5812", "Eating Places, Restaurants", 0.22, 3.4, 0.6),         # ~$30 avg
    ("5814", "Fast Food Restaurants", 0.15, 2.4, 0.4),              # ~$11 avg
    ("5541", "Service Stations (Gasoline)", 0.12, 3.7, 0.5),        # ~$40 avg
    ("5311", "Department Stores", 0.08, 4.4, 0.8),                  # ~$80 avg
    ("5732", "Electronic Sales", 0.04, 5.5, 0.9),                   # ~$240 avg
    ("4829", "Money Orders / Wire Transfer", 0.03, 6.5, 1.1),       # ~$650 avg
    ("3000", "Airlines & Air Carriers", 0.02, 5.9, 0.8),            # ~$360 avg
    ("7011", "Hotels, Motels, Resorts", 0.02, 5.7, 0.7),            # ~$300 avg
    ("5942", "Book Stores", 0.02, 3.2, 0.5),                        # ~$25 avg
]

CURRENCY_WEIGHTS = {
    CurrencyCode.USD: 0.70,
    CurrencyCode.EUR: 0.15,
    CurrencyCode.GBP: 0.08,
    CurrencyCode.SGD: 0.03,
    CurrencyCode.AED: 0.02,
    CurrencyCode.INR: 0.02,
}

REMITTANCE_TEMPLATES = [
    "Monthly invoice settlement",
    "Grocery purchase checkout",
    "Subscription renewal",
    "Online retail order payment",
    "Dining expenditure",
    "Fuel and service station charge",
    "Utility bill auto-debit",
    "Digital goods license",
    "Consulting services retainer",
    "Travel booking confirmation",
]


class BaseTransactionGenerator:
    """High-fidelity synthetic transaction generator for legitimate financial baseline traffic."""

    def __init__(
        self,
        num_accounts: int = 500,
        num_merchants: int = 100,
        random_seed: Optional[int] = 42,
    ) -> None:
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

        self.num_accounts = num_accounts
        self.num_merchants = num_merchants

        # Pre-generate persistent entity registry
        self.accounts = [f"ACC-{i:06d}" for i in range(1, num_accounts + 1)]
        self.merchants = [f"MERCH-{i:05d}" for i in range(1, num_merchants + 1)]

        # Assign home characteristics to accounts
        self.account_profiles: Dict[str, Dict] = {}
        for acc in self.accounts:
            self.account_profiles[acc] = {
                "home_country": random.choice(["US", "US", "US", "GB", "DE", "SG"]),
                "primary_device": f"DEV-{uuid.uuid4().hex[:12].upper()}",
                "secondary_device": f"DEV-{uuid.uuid4().hex[:12].upper()}" if random.random() < 0.3 else None,
                "primary_ip": f"{random.randint(12, 198)}.{random.randint(10, 240)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                "bank_bic": random.choice(["MSTRUS33XXX", "CHASUS33XXX", "BOFAUS3NXXX", "CITIUS33XXX", "BARCGB22XXX"]),
                "preferred_currency": random.choice(list(CurrencyCode)),
            }

    def _sample_amount(self, mu: float, sigma: float) -> float:
        """Sample a realistic monetary amount with pricing psychological anchors (.99, .50)."""
        raw_amt = float(np.random.lognormal(mean=mu, sigma=sigma))
        raw_amt = max(1.0, min(raw_amt, 25000.0))

        # 40% probability of typical commercial retail price anchoring (.99 or .50)
        p = random.random()
        if p < 0.35:
            return round(math.floor(raw_amt) + 0.99, 2)
        elif p < 0.50:
            return round(math.floor(raw_amt) + 0.50, 2)
        elif p < 0.65:
            return float(round(raw_amt))
        else:
            return round(raw_amt, 2)

    def _sample_diurnal_timestamp(self, start_time: datetime, time_span_days: float = 1.0) -> datetime:
        """Sample timestamp using non-homogeneous diurnal probability density."""
        # Random day offset within window
        day_offset = random.uniform(0, time_span_days)
        base_date = start_time + timedelta(days=day_offset)

        # Diurnal distribution: peak at 13:00 (1pm) and 19:00 (7pm), trough at 04:00 (4am)
        hour_weights = [
            0.01, 0.005, 0.005, 0.005, 0.01, 0.02,  # 00-05
            0.04, 0.06, 0.08, 0.07, 0.06, 0.07,     # 06-11
            0.09, 0.08, 0.06, 0.06, 0.07, 0.08,     # 12-17
            0.09, 0.08, 0.06, 0.04, 0.02, 0.01      # 18-23
        ]
        hour = random.choices(range(24), weights=hour_weights, k=1)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        micro = random.randint(0, 999999)

        return datetime(
            base_date.year, base_date.month, base_date.day,
            hour, minute, second, micro, tzinfo=timezone.utc
        )

    def generate_single_transaction(
        self,
        timestamp: Optional[datetime] = None,
        account_id: Optional[str] = None,
    ) -> PaymentTransaction:
        """Synthesize a single valid legitimate payment transaction."""
        sender = account_id or random.choice(self.accounts)
        receiver = random.choice(self.merchants)
        profile = self.account_profiles[sender]

        # Select MCC profile
        mcc_weights = [p[2] for p in MCC_PROFILES]
        chosen_mcc = random.choices(MCC_PROFILES, weights=mcc_weights, k=1)[0]
        mcc_code, mcc_desc, _, mu, sigma = chosen_mcc

        amount = self._sample_amount(mu, sigma)
        txn_time = timestamp or self._sample_diurnal_timestamp(datetime.now(timezone.utc) - timedelta(days=3))

        # Device & IP selection
        device_id = profile["primary_device"]
        if profile["secondary_device"] and random.random() < 0.25:
            device_id = profile["secondary_device"]

        # Channel mapping
        if mcc_code in ["5411", "5812", "5814", "5541"]:
            channel = random.choices(
                [TransactionChannel.POS, TransactionChannel.ONLINE, TransactionChannel.API],
                weights=[0.65, 0.30, 0.05], k=1
            )[0]
        elif mcc_code in ["4829"]:
            channel = TransactionChannel.WIRE
        else:
            channel = random.choices(
                [TransactionChannel.ONLINE, TransactionChannel.POS, TransactionChannel.P2P],
                weights=[0.75, 0.15, 0.10], k=1
            )[0]

        # Currency selection
        currencies = list(CURRENCY_WEIGHTS.keys())
        curr_weights = list(CURRENCY_WEIGHTS.values())
        currency = random.choices(currencies, weights=curr_weights, k=1)[0]

        return PaymentTransaction(
            txn_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
            timestamp=txn_time,
            sender_account=sender,
            receiver_account=receiver,
            sender_bank_bic=profile["bank_bic"],
            receiver_bank_bic=random.choice(["MSTRUS33XXX", "CHASUS33XXX", "CITIUS33XXX", "HSBCGB2LXXX"]),
            amount=amount,
            currency=currency,
            channel=channel,
            mcc=mcc_code,
            mcc_description=mcc_desc,
            device_id=device_id,
            ip_address=profile["primary_ip"],
            ip_country=profile["home_country"],
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4; Mobile/15E148)",
            is_foreign_transaction=False,
            session_duration_sec=float(np.random.gamma(shape=3.0, scale=15.0)),
            biometric_friction_score=float(np.random.beta(a=1.5, b=25.0)),  # centered near 0.03
            iso_message_type="pacs.008.001.08",
            remittance_info=random.choice(REMITTANCE_TEMPLATES),
            purpose_code="GDDS" if channel != TransactionChannel.WIRE else "INTE",
            is_fraud=0,
            attack_type=None,
        )

    def generate_batch(
        self,
        n: int = 1000,
        start_time: Optional[datetime] = None,
        time_span_days: float = 7.0,
    ) -> pd.DataFrame:
        """Generate a batch of legitimate transactions formatted as a DataFrame."""
        base_start = start_time or (datetime.now(timezone.utc) - timedelta(days=time_span_days))
        records = []
        for _ in range(n):
            ts = self._sample_diurnal_timestamp(base_start, time_span_days)
            txn = self.generate_single_transaction(timestamp=ts)
            records.append(txn.to_dict())

        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
