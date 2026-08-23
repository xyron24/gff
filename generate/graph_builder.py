"""Temporal Heterogeneous Transaction Graph Builder.

Constructs multi-relational temporal graphs connecting Accounts, Merchants,
Devices, and IPs with timestamped financial flows, supporting graph metrics
extraction, cycle detection, and D3.js dashboard serialization.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import networkx as nx
import numpy as np
import pandas as pd

from data.schema import PaymentTransaction


class TransactionGraphBuilder:
    """Builds and queries temporal multi-relational graphs from payment logs."""

    def __init__(self) -> None:
        # MultiDiGraph allows multiple timestamped transactions between the same node pairs
        self.graph = nx.MultiDiGraph()
        self._node_types: Dict[str, str] = {}

    def add_transaction(self, txn: Union[PaymentTransaction, Dict[str, Any]]) -> None:
        """Insert a single payment transaction and its associated telemetry into the graph."""
        d = txn.model_dump() if isinstance(txn, PaymentTransaction) else txn

        sender = str(d["sender_account"])
        receiver = str(d["receiver_account"])
        device = str(d.get("device_id", "DEV-UNKNOWN"))
        ip = str(d.get("ip_address", "0.0.0.0"))
        ts = d.get("timestamp")
        ts_iso = ts.isoformat() if isinstance(ts, datetime) else str(ts)
        amount = float(d.get("amount", 0.0))
        is_fraud = int(d.get("is_fraud", 0))
        attack_type = d.get("attack_type")

        # 1. Register Account / Merchant Nodes
        self._add_node(sender, "account")
        receiver_type = "merchant" if receiver.startswith("MERCH-") else "account"
        self._add_node(receiver, receiver_type)

        # 2. Register Device and IP Nodes
        self._add_node(device, "device")
        self._add_node(ip, "ip")

        # 3. Add Financial Flow Edge (sender -> receiver)
        self.graph.add_edge(
            sender,
            receiver,
            key=d.get("txn_id", f"e_{len(self.graph.edges)}"),
            relation="TRANSACTS_WITH" if receiver_type == "merchant" else "TRANSFERS_TO",
            timestamp=ts_iso,
            amount=amount,
            channel=d.get("channel", "ONLINE"),
            is_fraud=is_fraud,
            attack_type=attack_type,
        )

        # 4. Add Telemetry Edges (sender -> device -> ip)
        self.graph.add_edge(
            sender,
            device,
            relation="USES_DEVICE",
            timestamp=ts_iso,
            is_fraud=is_fraud,
        )
        self.graph.add_edge(
            device,
            ip,
            relation="CONNECTS_FROM",
            timestamp=ts_iso,
            is_fraud=is_fraud,
        )

    def _add_node(self, node_id: str, node_type: str) -> None:
        """Helper to register typed node."""
        if node_id not in self.graph:
            self.graph.add_node(node_id, node_type=node_type, fraud_flag=0)
            self._node_types[node_id] = node_type

    def build_from_dataframe(self, df: pd.DataFrame) -> None:
        """Batch construct graph from pandas DataFrame."""
        for _, row in df.iterrows():
            self.add_transaction(row.to_dict())

    def compute_node_features(self, node_id: str) -> Dict[str, float]:
        """Extract graph topology and velocity features for a specific account node."""
        if node_id not in self.graph:
            return {
                "in_degree": 0.0,
                "out_degree": 0.0,
                "fan_out_ratio": 0.0,
                "total_sent_volume": 0.0,
                "total_received_volume": 0.0,
                "shared_device_count": 0.0,
                "shared_ip_count": 0.0,
            }

        out_edges = self.graph.out_edges(node_id, data=True)
        in_edges = self.graph.in_edges(node_id, data=True)

        out_degree = len([e for e in out_edges if e[2].get("relation") in ["TRANSACTS_WITH", "TRANSFERS_TO"]])
        in_degree = len([e for e in in_edges if e[2].get("relation") in ["TRANSACTS_WITH", "TRANSFERS_TO"]])

        sent_volume = sum(
            e[2].get("amount", 0.0) for e in out_edges if e[2].get("relation") in ["TRANSACTS_WITH", "TRANSFERS_TO"]
        )
        recv_volume = sum(
            e[2].get("amount", 0.0) for e in in_edges if e[2].get("relation") in ["TRANSACTS_WITH", "TRANSFERS_TO"]
        )

        devices = [e[1] for e in out_edges if e[2].get("relation") == "USES_DEVICE"]
        device_sharing_count = sum(len(self.graph.in_edges(dev)) for dev in devices) if devices else 0

        ips = []
        for dev in devices:
            ips.extend([e[1] for e in self.graph.out_edges(dev, data=True) if e[2].get("relation") == "CONNECTS_FROM"])
        ip_sharing_count = sum(len(self.graph.in_edges(ip_node)) for ip_node in ips) if ips else 0

        fan_out_ratio = float(out_degree / max(1, in_degree))

        return {
            "in_degree": float(in_degree),
            "out_degree": float(out_degree),
            "fan_out_ratio": float(fan_out_ratio),
            "total_sent_volume": float(sent_volume),
            "total_received_volume": float(recv_volume),
            "shared_device_count": float(device_sharing_count),
            "shared_ip_count": float(ip_sharing_count),
        }

    def detect_mule_cycles(self, max_cycle_length: int = 6) -> List[List[str]]:
        """Identify closed cyclic fund flows (ATK-006 mule ring detection)."""
        # Create a simplified DiGraph of financial flow edges only
        flow_graph = nx.DiGraph()
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") in ["TRANSFERS_TO", "TRANSACTS_WITH"]:
                flow_graph.add_edge(u, v)

        try:
            cycles = list(nx.simple_cycles(flow_graph))
            filtered = [c for c in cycles if 2 <= len(c) <= max_cycle_length]
            return filtered
        except Exception:
            return []

    def to_d3_json(self, max_nodes: int = 150) -> Dict[str, Any]:
        """Serialize graph to D3.js force-directed JSON format for web dashboard."""
        # Prioritize fraudulent nodes / high degree nodes if exceeding max_nodes
        nodes_to_include: Set[str] = set()
        for u, v, data in self.graph.edges(data=True):
            if data.get("is_fraud", 0) == 1:
                nodes_to_include.add(u)
                nodes_to_include.add(v)
            if len(nodes_to_include) >= max_nodes:
                break

        if len(nodes_to_include) < max_nodes:
            all_nodes = list(self.graph.nodes())
            nodes_to_include.update(all_nodes[: max_nodes - len(nodes_to_include)])

        nodes = []
        for n in nodes_to_include:
            node_type = self._node_types.get(n, "account")
            is_fraudulent = any(
                data.get("is_fraud", 0) == 1
                for _, _, data in self.graph.edges(n, data=True)
            )
            nodes.append({
                "id": n,
                "type": node_type,
                "is_fraud": 1 if is_fraudulent else 0,
            })

        links = []
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            if u in nodes_to_include and v in nodes_to_include:
                links.append({
                    "source": u,
                    "target": v,
                    "relation": data.get("relation", "FLOW"),
                    "amount": data.get("amount", 0.0),
                    "is_fraud": data.get("is_fraud", 0),
                    "attack_type": data.get("attack_type"),
                    "timestamp": data.get("timestamp"),
                })

        return {
            "nodes": nodes,
            "links": links,
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
        }
