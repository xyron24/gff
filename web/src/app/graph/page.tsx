"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { Network, RefreshCw, Layers, ShieldAlert, CheckCircle2 } from "lucide-react";
import { fetchGraph } from "@/lib/api";

export default function GraphPage() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  async function loadGraph() {
    setLoading(true);
    try {
      const data = await fetchGraph(120);
      setGraphData(data);
    } catch (err) {
      console.error("Failed to load graph:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadGraph();
  }, []);

  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const width = svgRef.current.clientWidth || 900;
    const height = 580;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const g = svg.append("g");

    // Add zoom capabilities
    const zoom = d3.zoom().scaleExtent([0.2, 4]).on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
    svg.call(zoom as any);

    // Deep clone data for D3 mutation
    const nodes = graphData.nodes.map((d: any) => ({ ...d }));
    const links = graphData.links.map((d: any) => ({ ...d }));

    const simulation = d3
      .forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(60))
      .force("charge", d3.forceManyBody().strength(-140))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(22));

    // Render Links
    const link = g
      .append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", (d: any) => (d.is_fraud ? "#ef4444" : "rgba(255, 255, 255, 0.15)"))
      .attr("stroke-width", (d: any) => (d.is_fraud ? 2.5 : 1))
      .attr("stroke-dasharray", (d: any) => (d.is_fraud ? "4,2" : "none"));

    // Color by node type
    const getNodeColor = (d: any) => {
      if (d.is_fraud) return "#ef4444";
      if (d.type === "merchant") return "#10b981";
      if (d.type === "device") return "#8b5cf6";
      if (d.type === "ip") return "#f59e0b";
      return "#00d4ff"; // account
    };

    // Render Nodes
    const node = g
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", (d: any) => (d.is_fraud ? 9 : 6))
      .attr("fill", getNodeColor)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.5)
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        setSelectedNode(d);
      });

    // Drag behaviour
    node.call(
      d3
        .drag()
        .on("start", (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event: any, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as any
    );

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
    });

    return () => {
      simulation.stop();
    };
  }, [graphData]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div className="badge badge-purple" style={{ marginBottom: "10px" }}>
            PILLAR 2 &amp; 3 • RELATIONAL TOPOLOGY
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: "800", letterSpacing: "-0.02em", marginBottom: "8px" }}>
            Temporal Transaction &amp; Mule-Ring Network Graph
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Multi-relational graph connecting Accounts, Merchants, Devices, and IPs. Red dotted edges highlight dynamic money-mule cycle flows and smurfing fan-outs.
          </p>
        </div>

        <button onClick={loadGraph} className="btn-secondary">
          <RefreshCw size={16} />
          Reload Graph
        </button>
      </div>

      {/* Legend & Stats Bar */}
      <div className="glass-card" style={{ padding: "14px 24px", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "18px", fontSize: "0.82rem", fontWeight: 600 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#00d4ff" }} /> Account
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#10b981" }} /> Merchant
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#8b5cf6" }} /> Device
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#f59e0b" }} /> IP Node
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#ef4444" }} /> Flagged Mule / Fraud
          </div>
        </div>

        <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          Total Nodes: {graphData?.total_nodes || 0} • Total Flow Edges: {graphData?.total_edges || 0}
        </div>
      </div>

      {/* Graph Canvas & Side Inspector */}
      <div style={{ display: "grid", gridTemplateColumns: selectedNode ? "1fr 340px" : "1fr", gap: "24px" }}>
        <div className="glass-card" style={{ padding: "16px", background: "#050811", overflow: "hidden", position: "relative" }}>
          <svg ref={svgRef} style={{ width: "100%", height: "580px" }} />
          <div style={{ position: "absolute", bottom: "16px", left: "16px", fontSize: "0.72rem", color: "var(--text-muted)" }}>
            Scroll to zoom • Drag nodes to reposition • Click to inspect node details
          </div>
        </div>

        {/* Node Inspector Drawer */}
        {selectedNode && (
          <div className="glass-card" style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700 }}>Node Telemetry</h3>
              <button
                onClick={() => setSelectedNode(null)}
                style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
              >
                &times;
              </button>
            </div>

            <div style={{ padding: "14px", borderRadius: "8px", background: "rgba(255, 255, 255, 0.03)", border: "1px solid var(--border-color)" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>IDENTIFIER</div>
              <div style={{ fontSize: "1rem", fontWeight: 700, fontFamily: "var(--font-mono)", color: "var(--accent-cyan)", margin: "4px 0" }}>
                {selectedNode.id}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase" }}>
                Type: {selectedNode.type}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.85rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Mule Status:</span>
                <span style={{ fontWeight: 700, color: selectedNode.is_fraud ? "var(--accent-red)" : "var(--accent-green)" }}>
                  {selectedNode.is_fraud ? "FLAGGED FRAUDULENT" : "CLEAN"}
                </span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                <span style={{ color: "var(--text-muted)" }}>Topology Risk:</span>
                <span>{selectedNode.is_fraud ? "HIGH (Mule Ring/Fan-Out)" : "LOW (Standard Retail)"}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
