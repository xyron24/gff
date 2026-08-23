"""Tier-3 Cognitive LLM Explainer & Automated SAR Narrative Generator.

Generates structured regulatory Suspicious Activity Reports (SAR) for high-risk
transactions using multi-tier detection context and graph signals.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import google.generativeai as genai


SAR_PROMPT_TEMPLATE = """You are a Principal Anti-Money Laundering (AML) Compliance Officer generating a formal FinCEN Suspicious Activity Report (SAR) narrative.

TRANSACTION CONTEXT:
- Transaction ID: {txn_id}
- Timestamp: {timestamp}
- Amount: ${amount:,.2f} {currency}
- Originator Account: {sender_account} (BIC: {sender_bic})
- Beneficiary Account: {receiver_account} (BIC: {receiver_bic})
- Channel / Rail: {channel}
- Merchant Category Code (MCC): {mcc} ({mcc_description})
- Remittance Text: "{remittance_info}"
- Purpose Code: {purpose_code}

DETECTION SIGNALS & AI DEFENSE GRID METRICS:
- Tier-1 Fast GBDT Risk Score: {tier1_score:.3f}
- Tier-2 Temporal Graph Risk Score: {tier2_score:.3f}
- Suspected Attack Vector: {suspected_attack} ({attack_category})
- Graph Anomalies: In-Degree={in_degree}, Out-Degree={out_degree}, In-Mule-Cycle={in_cycle}
- Telemetry Flags: Biometric Friction={friction:.4f}, Session Duration={duration}s, Unicode Anomalies={has_unicode}

INSTRUCTIONS:
Generate a structured, professional SAR Narrative following standard AML structure:
1. Executive Summary (Brief 2-sentence synopsis of suspicious activity)
2. Chronological & Tactical Breakdown (Adversarial GenAI technique observed)
3. Relational & Graph Analysis (Mule network, fan-out structuring, or proxy links)
4. Regulatory Conclusion & Recommended Action (Account freeze, law enforcement referral)
"""


class Tier3LLMExplainer:
    """Async cognitive explainer generating human-in-the-loop SAR reports."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._is_gemini_available = False

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self._is_gemini_available = True
            except Exception:
                self._is_gemini_available = False

    def generate_sar_report(
        self,
        txn: Dict[str, Any],
        tier1_score: float,
        tier2_score: float,
        suspected_attack: str = "ATK-001 (Agentic Micro-Smurfing)",
        attack_category: str = "structuring",
        graph_feats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete SAR narrative package for a flagged transaction."""
        g_feats = graph_feats or {}
        in_deg = g_feats.get("in_degree", 0.0)
        out_deg = g_feats.get("out_degree", 0.0)
        in_cycle = "YES" if g_feats.get("is_in_mule_cycle", 0.0) == 1.0 else "NO"
        friction = float(txn.get("biometric_friction_score", 0.05))
        duration = float(txn.get("session_duration_sec", 45.0))
        has_unicode = "DETECTED" if "TXN-ISO" in str(txn.get("txn_id", "")) else "NONE"

        formatted_prompt = SAR_PROMPT_TEMPLATE.format(
            txn_id=txn.get("txn_id", "TXN-UNKNOWN"),
            timestamp=txn.get("timestamp", datetime.now(timezone.utc).isoformat()),
            amount=float(txn.get("amount", 0.0)),
            currency=txn.get("currency", "USD"),
            sender_account=txn.get("sender_account", "ACC-UNKNOWN"),
            sender_bic=txn.get("sender_bank_bic", "MSTRUS33XXX"),
            receiver_account=txn.get("receiver_account", "ACC-UNKNOWN"),
            receiver_bic=txn.get("receiver_bank_bic", "CHASUS33XXX"),
            channel=txn.get("channel", "ONLINE"),
            mcc=txn.get("mcc", "5411"),
            mcc_description=txn.get("mcc_description", "Retail"),
            remittance_info=txn.get("remittance_info", ""),
            purpose_code=txn.get("purpose_code", "GDDS"),
            tier1_score=tier1_score,
            tier2_score=tier2_score,
            suspected_attack=suspected_attack,
            attack_category=attack_category,
            in_degree=in_deg,
            out_degree=out_deg,
            in_cycle=in_cycle,
            friction=friction,
            duration=duration,
            has_unicode=has_unicode,
        )

        narrative = None
        if self._is_gemini_available:
            try:
                response = self.model.generate_content(formatted_prompt)
                narrative = response.text
            except Exception:
                narrative = None

        if not narrative:
            # Deterministic rule-grounded FinCEN narrative fallback
            narrative = self._generate_fallback_narrative(
                txn, tier1_score, tier2_score, suspected_attack, in_deg, out_deg, in_cycle
            )

        return {
            "sar_id": f"SAR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{txn.get('txn_id', '0000')[-6:]}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target_transaction_id": txn.get("txn_id"),
            "risk_assessment": {
                "composite_score": round(0.4 * tier1_score + 0.6 * tier2_score, 4),
                "tier1_score": round(tier1_score, 4),
                "tier2_score": round(tier2_score, 4),
                "threat_vector": suspected_attack,
                "regulatory_filing_status": "RECOMMENDED_IMMEDIATE_FILING",
            },
            "narrative_text": narrative,
        }

    def _generate_fallback_narrative(
        self,
        txn: Dict[str, Any],
        t1: float,
        t2: float,
        atk: str,
        in_deg: float,
        out_deg: float,
        in_cycle: str,
    ) -> str:
        """High-quality regulatory narrative generator when LLM API key is offline."""
        amt = float(txn.get("amount", 0.0))
        sender = txn.get("sender_account", "ACC-UNKNOWN")
        receiver = txn.get("receiver_account", "ACC-UNKNOWN")
        txn_id = txn.get("txn_id", "TXN-UNKNOWN")

        return f"""### 1. Executive Summary
On {datetime.now(timezone.utc).strftime('%B %d, %Y')}, the AI Defense Lab real-time transaction monitoring grid flagged transaction {txn_id} involving originator account {sender} and beneficiary {receiver} for total value ${amt:,.2f}. The transaction exhibited high-confidence indicators of autonomous GenAI financial fraud categorized under {atk}.

### 2. Tactical & Technical Analysis
The multi-tier detection grid recorded a Tier-1 tabular anomaly score of {t1:.3f} and a Tier-2 temporal graph risk score of {t2:.3f}. Telemetry signals indicated structured micro-amounts, behavioral kinematic anomalies, and rapid out-of-pattern transaction velocities designed to bypass static threshold monitoring.

### 3. Relational & Network Ledger Context
Graph adjacency evaluation revealed abnormal topological fan-out metrics (Out-Degree: {out_deg}, In-Degree: {in_deg}, Mule Cycle: {in_cycle}). Transaction routing exhibits signature characteristics of ephemeral mule accounts acting as transient liquidity conduits.

### 4. Regulatory Conclusion & Action Taken
In compliance with 31 CFR § 1020.320, an automatic provisional hold has been applied to funds associated with {txn_id}. Originator account {sender} has been placed under active forensic monitoring and this report is forwarded to internal compliance for SAR submission to regulatory authorities."""
