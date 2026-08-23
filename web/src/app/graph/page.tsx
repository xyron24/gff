"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { Network, RefreshCw, Layers, ShieldAlert, CheckCircle2, X } from "lucide-react";
import { fetchGraph } from "@/lib/api";

export default function GraphPage() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("ALL");

  async function loadGraph() {
    setLoading(true);
    try {
      const data = await fetchGraph(140);
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
    const height = 620;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Radar coordinate grid background
    const gridGroup = svg.append("g").attr("class", "radar-grid");
    const cx = width / 2;
    const cy = height / 2;
    const maxRadius = Math.min(width, height) * 0.45;

    [0.2, 0.4, 0.6, 0.8, 1.0].forEach((ratio) => {
      gridGroup
        .append("circle")
        .attr("cx", cx)
        .attr("cy", cy)
        .attr("r", maxRadius * ratio)
        .attr("fill", "none")
        .attr("stroke", "#1A1F2C")
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "3 3");
    });

    gridGroup
      .append("line")
      .attr("x1", cx)
      .attr("y1", cy - maxRadius)
      .attr("x2", cx)
      .attr("y2", cy + maxRadius)
      .attr("stroke", "#1A1F2C")
      .attr("stroke-width", 1);

    gridGroup
      .append("line")
      .attr("x1", cx - maxRadius)
      .attr("y1", cy)
      .attr("x2", cx + maxRadius)
      .attr("y2", cy)
      .attr("stroke", "#1A1F2C")
      .attr("stroke-width", 1);

    const g = svg.append("g");

    // Add zoom capabilities
    const zoom = d3.zoom().scaleExtent([0.3, 4]).on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
    svg.call(zoom as any);

    let nodes = graphData.nodes.map((d: any) => ({ ...d }));
    if (filterType === "MULES") {
      nodes = nodes.filter((d: any) => d.is_fraud);
    } else if (filterType === "MERCHANTS") {
      nodes = nodes.filter((d: any) => d.type === "merchant");
    }

    const nodeSet = new Set(nodes.map((n: any) => n.id));
    const links = graphData.links
      .filter((l: any) => nodeSet.has(l.source?.id || l.source) && nodeSet.has(l.target?.id || l.target))
      .map((d: any) => ({ ...d }));

    const simulation = d3
      .forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(55))
      .force("charge", d3.forceManyBody().strength(-130))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => (d.is_fraud ? 20 : 14)));

    // Render Links
    const link = g
      .append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", (d: any) => (d.is_fraud ? "#EF4444" : "#334155"))
      .attr("stroke-width", (d: any) => (d.is_fraud ? 2.0 : 0.8))
      .attr("stroke-dasharray", (d: any) => (d.is_fraud ? "4,3" : "none"))
      .attr("opacity", (d: any) => (d.is_fraud ? 0.95 : 0.45));

    // Color & Radii
    const getNodeRadius = (d: any) => {
      if (d.is_fraud) return 10;
      if (d.type === "merchant") return 8;
      if (d.type === "device" || d.type === "ip") return 7;
      return 6;
    };

    const getNodeColor = (d: any) => {
      if (d.is_fraud) return "#EF4444";
      if (d.type === "merchant") return "#10B981";
      if (d.type === "device") return "#8B5CF6";
      if (d.type === "ip") return "#F59E0B";
      return "#38BDF8"; // Account
    };

    // Render Nodes
    const nodeGroup = g
      .append("g")
      .selectAll("g")
      .data(nodes)
      .enter()
      .append("g")
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        setSelectedNode(d);
      });

    nodeGroup
      .filter((d: any) => d.is_fraud)
      .append("circle")
      .attr("r", 16)
      .attr("fill", "rgba(239, 68, 68, 0.15)")
      .attr("stroke", "rgba(239, 68, 68, 0.4)")
      .attr("stroke-width", 1)
      .attr("class", "animate-pulse");

    nodeGroup
      .append("circle")
      .attr("r", getNodeRadius)
      .attr("fill", getNodeColor)
      .attr("stroke", "#08090C")
      .attr("stroke-width", 1.5);

    // Drag behavior
    nodeGroup.call(
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

      nodeGroup.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [graphData, filterType]);

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Header */}
      <div className="terminal-panel p-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge-clean badge-neutral font-mono">PILLAR 2 &amp; 3: TOPOLOGY</span>
            <h1 className="font-bold text-sm text-slate-100 tracking-tight">
              TEMPORAL TRANSACTION &amp; MULE-RING NETWORK GRAPH
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Heterogeneous multi-relational graph connecting Accounts, Merchants, Devices, and IPs with dynamic cycle detection.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-[#08090C] border border-[#1C2230] rounded p-0.5 text-xs font-mono">
            {["ALL", "MULES", "MERCHANTS"].map((f) => (
              <button
                key={f}
                onClick={() => setFilterType(f)}
                className={`px-2.5 py-1 rounded ${
                  filterType === f ? "bg-[#1C2230] text-slate-100 font-bold" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          <button onClick={loadGraph} className="btn-subtle text-xs font-mono">
            <RefreshCw size={13} />
            <span>RELOAD GRAPH</span>
          </button>
        </div>
      </div>

      {/* Graph Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-9 terminal-panel h-[620px] relative bg-[#08090C] overflow-hidden">
          <svg ref={svgRef} className="w-full h-full" />

          {/* Floating Telemetry Badge */}
          <div className="absolute top-3 left-3 bg-[#0D1017]/90 backdrop-blur border border-[#1C2230] rounded px-3 py-1.5 text-xs font-mono text-slate-300 shadow-md">
            <span>Topology: </span>
            <span className="text-slate-100 font-bold">{graphData?.total_nodes || 140} Nodes</span>
            <span className="text-slate-500 mx-1.5">|</span>
            <span className="text-slate-100 font-bold">{graphData?.total_edges || 210} Edges</span>
            <span className="text-slate-500 mx-1.5">|</span>
            <span className="text-rose-400 font-bold">4 Cyclic Clusters</span>
          </div>

          {/* Legend */}
          <div className="absolute bottom-3 left-3 bg-[#0D1017]/90 backdrop-blur border border-[#1C2230] rounded px-3 py-1.5 flex items-center gap-3.5 text-[10px] font-mono text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#38BDF8]" /> ACC (6px)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" /> MERCH (8px)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#8B5CF6]" /> DEV (7px)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" /> IP (7px)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" /> MULE / CYCLE (10px)
            </span>
          </div>
        </div>

        {/* Node Telemetry HUD */}
        <div className="lg:col-span-3 terminal-panel p-4 flex flex-col gap-3 h-[620px] bg-[#0D1017]">
          <div className="terminal-title text-slate-200">
            <Network size={13} className="text-purple-400" />
            <span>NODE TELEMETRY HUD</span>
          </div>

          {selectedNode ? (
            <div className="flex flex-col gap-2.5 text-xs">
              <div className="bg-[#131722] border border-[#1C2230] rounded p-3 font-mono">
                <div className="text-[10px] text-slate-500">IDENTIFIER</div>
                <div className="text-sky-400 font-bold text-sm">{selectedNode.id}</div>
                <div className="text-[11px] text-slate-300 uppercase mt-1">TYPE: {selectedNode.type}</div>
              </div>

              <div className="bg-[#131722] border border-[#1C2230] rounded p-3 flex flex-col gap-1.5 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-500">MULE STATUS:</span>
                  <span className={selectedNode.is_fraud ? "text-rose-400 font-bold" : "text-emerald-400 font-bold"}>
                    {selectedNode.is_fraud ? "FLAGGED MULE" : "CLEAN NODE"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">TOPOLOGY RISK:</span>
                  <span className="text-slate-200">{selectedNode.is_fraud ? "HIGH (Cycle/Decoy)" : "LOW (Retail)"}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 text-xs">
              <Network size={32} className="opacity-30 mb-2 text-slate-400" />
              <span className="font-mono text-xs text-slate-300">No Node Selected</span>
              <span className="text-[11px] text-slate-500 max-w-xs mt-1">
                Click any graph node to inspect relational topology and mule cycle participation.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
