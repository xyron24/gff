"""Tabular Feature Engineering Pipeline for Payment Fraud Detection.

Extracts real-time transaction-level features, rolling historical velocities,
statistical deviation z-scores, behavioral scores, and metadata risk signals
optimized for sub-millisecond inference in Tier-1 GBDT.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from generate.iso20022_formatter import inspect_unicode_anomalies


class TabularFeatureExtractor:
    """Extracts numeric feature vectors from raw payment transaction records."""

    FEATURE_NAMES: List[str] = [
        # Numeric amounts & transformations
        "amount",
        "log_amount",
        "is_round_amount",
        "is_just_below_threshold",  # near $200, $500, $1000, $10000
        # Temporal features
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "is_night_time",  # 00:00 - 05:00
        # Categorical / Rail encodings
        "channel_pos",
        "channel_online",
        "channel_wire",
        "channel_p2p",
        "channel_api",
        "is_foreign_transaction",
        "is_high_risk_mcc",  # 4829 wire, 5732 electronics, 7995 crypto/gambling
        # Behavioral & Telemetry features
        "session_duration_sec",
        "log_session_duration",
        "biometric_friction_score",
        "is_instant_session",  # <5s (bot ATO indicator)
        # ISO 20022 Metadata signals
        "has_unicode_anomalies",
        "zero_width_count",
        # Historical velocity mock features (rolling counters)
        "velocity_1h_count",
        "velocity_24h_count",
        "amount_zscore",
    ]

    def __init__(self) -> None:
        # In-memory account history cache for real-time streaming velocity calculation
        self._account_history: Dict[str, List[Tuple[datetime, float]]] = {}

    def reset_cache(self) -> None:
        """Clear account streaming cache."""
        self._account_history.clear()

    def update_history(self, account: str, ts: datetime, amount: float) -> None:
        """Register transaction in streaming cache."""
        if account not in self._account_history:
            self._account_history[account] = []
        self._account_history[account].append((ts, amount))
        # Keep only recent 100 txns
        if len(self._account_history[account]) > 100:
            self._account_history[account] = self._account_history[account][-100:]

    def extract_single(self, txn: Dict[str, Any]) -> np.ndarray:
        """Extract a 1D numpy feature vector for a single transaction record."""
        amt = float(txn.get("amount", 0.0))
        log_amt = math.log(max(amt, 0.01) + 1.0)
        is_round = 1.0 if (amt % 1.0 == 0 or amt % 10.0 == 0) else 0.0

        # Sub-threshold check ($180-$199, $480-$499, $950-$999, $9500-$9999)
        is_sub_thresh = 1.0 if (
            (180 <= amt < 200) or (470 <= amt < 500) or (940 <= amt < 1000) or (9000 <= amt < 10000)
        ) else 0.0

        # Time parsing
        ts = txn.get("timestamp")
        if isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.now(timezone.utc)
        elif isinstance(ts, datetime):
            dt = ts
        else:
            dt = datetime.now(timezone.utc)

        hour = dt.hour
        dow = dt.weekday()
        is_weekend = 1.0 if dow in [5, 6] else 0.0
        is_night = 1.0 if (0 <= hour <= 5) else 0.0

        # Channel one-hot
        ch = str(txn.get("channel", "ONLINE")).upper()
        ch_pos = 1.0 if ch == "POS" else 0.0
        ch_online = 1.0 if ch == "ONLINE" else 0.0
        ch_wire = 1.0 if ch == "WIRE" else 0.0
        ch_p2p = 1.0 if ch == "P2P" else 0.0
        ch_api = 1.0 if ch == "API" else 0.0

        is_foreign = 1.0 if txn.get("is_foreign_transaction", False) else 0.0
        mcc = str(txn.get("mcc", "5411"))
        is_high_risk_mcc = 1.0 if mcc in ["4829", "5732", "7995", "5094"] else 0.0

        # Behavioral
        dur = float(txn.get("session_duration_sec", 45.0))
        log_dur = math.log(max(dur, 0.1) + 1.0)
        friction = float(txn.get("biometric_friction_score", 0.05))
        is_instant = 1.0 if dur < 6.0 else 0.0

        # ISO Unicode analysis
        remittance = str(txn.get("remittance_info", ""))
        unicode_diag = inspect_unicode_anomalies(remittance)
        has_unicode = 1.0 if unicode_diag["has_anomalies"] else 0.0
        zw_count = float(unicode_diag["zero_width_count"])

        # Dynamic Streaming Velocity Calculation
        sender = str(txn.get("sender_account", "ACC-UNKNOWN"))
        history = self._account_history.get(sender, [])
        v1h = sum(1 for (past_t, _) in history if (dt - past_t).total_seconds() <= 3600 and (dt - past_t).total_seconds() >= 0)
        v24h = sum(1 for (past_t, _) in history if (dt - past_t).total_seconds() <= 86400 and (dt - past_t).total_seconds() >= 0)

        # Amount z-score
        past_amts = [past_a for (past_t, past_a) in history if (dt - past_t).total_seconds() <= 86400 * 7]
        if len(past_amts) >= 3:
            mean_a = np.mean(past_amts)
            std_a = np.std(past_amts)
            z_score = float((amt - mean_a) / max(std_a, 1.0))
        else:
            z_score = 0.0

        # Register current
        self.update_history(sender, dt, amt)

        feature_vector = [
            amt,
            log_amt,
            is_round,
            is_sub_thresh,
            float(hour),
            float(dow),
            is_weekend,
            is_night,
            ch_pos,
            ch_online,
            ch_wire,
            ch_p2p,
            ch_api,
            is_foreign,
            is_high_risk_mcc,
            dur,
            log_dur,
            friction,
            is_instant,
            has_unicode,
            zw_count,
            float(v1h),
            float(v24h),
            float(z_score),
        ]
        return np.array(feature_vector, dtype=np.float32)

    def extract_dataframe(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Batch extract feature matrix from DataFrame."""
        matrix = []
        for _, row in df.iterrows():
            vec = self.extract_single(row.to_dict())
            matrix.append(vec)
        return np.vstack(matrix), self.FEATURE_NAMES
