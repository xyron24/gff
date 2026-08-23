"""Real-Time Transaction Settlement WebSocket Stream Handler.

Streams live synthetic payment authorizations with concurrent sub-30ms fraud evaluation
for interactive web dashboard visualization.
"""

from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect

from generate.base_generator import BaseTransactionGenerator
from generate.attack_injectors import INJECTOR_REGISTRY, get_injector
from generate.iso20022_formatter import format_pacs008, format_pain001
from defend.ensemble import DetectionGrid

base_gen = BaseTransactionGenerator(random_seed=42)
detection_grid = DetectionGrid()


async def handle_transaction_websocket(websocket: WebSocket) -> None:
    """Stream live transactions to connected dashboard client."""
    await websocket.accept()
    attack_ids = list(INJECTOR_REGISTRY.keys())

    try:
        while True:
            # 15% probability of generating an attack transaction
            is_fraud_turn = random.random() < 0.15

            if is_fraud_turn:
                atk_id = random.choice(attack_ids)
                injector = get_injector(atk_id)
                legit_sample = base_gen.generate_batch(n=5)
                atk_df = injector.inject(baseline_df=legit_sample, n_attacks=1)
                txn_data = atk_df.iloc[0].to_dict()
            else:
                txn = base_gen.generate_single_transaction()
                txn_data = txn.to_dict()

            if hasattr(txn_data.get("timestamp"), "isoformat"):
                txn_data["timestamp"] = txn_data["timestamp"].isoformat()

            # Score through cascading grid
            result = detection_grid.score_transaction(txn_data, generate_sar=False)

            # Build ISO 20022 XML snippet
            if txn_data.get("channel") == "WIRE":
                xml_snippet = format_pain001(txn_data)
            else:
                xml_snippet = format_pacs008(txn_data)

            payload = {
                "event_type": "TRANSACTION_AUTHORIZATION",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "transaction": txn_data,
                "detection": result,
                "iso_xml": xml_snippet,
            }

            await websocket.send_text(json.dumps(payload))
            # Stream at ~10-15 events per second (60ms-100ms interval)
            await asyncio.sleep(0.08)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
